"""
Lightweight in-memory process-local rate limiter for AgriPredict-AI.

Features:
- Sliding-window request counter per client IP and endpoint group.
- Fully process-local (no external daemon or Redis dependency required).
- Trusted reverse proxy client IP resolution with anti-spoofing controls.
- Automatic memory purging of inactive IP deques.
- Returns HTTP 429 with Retry-After and X-RateLimit headers.
- Thread-safe using threading.Lock.
"""

import time
import os
import logging
from collections import defaultdict, deque
from typing import Dict, Deque, Tuple, Optional, Set
from threading import Lock
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger("agripredict.security")

# Environment configurations
RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() in ("true", "1", "yes")

# Trusted reverse proxies (e.g. Nginx, Cloudflare, load balancers)
TRUSTED_PROXIES: Set[str] = set(
    ip.strip() for ip in os.getenv("TRUSTED_PROXIES", "127.0.0.1,::1,localhost").split(",") if ip.strip()
)

# Default quotas: (max_requests, window_seconds)
DEFAULT_QUOTAS: Dict[str, Tuple[int, int]] = {
    "cotton_ml": (60, 60),          # 60 req/min for cotton yield & SHAP
    "crop_ml": (60, 60),            # 60 req/min for crop recommendation & yield
    "future_forecast": (60, 60),    # 60 req/min for multi-year forecasting
    "weather": (60, 60),            # 60 req/min for Open-Meteo integration
    "general": (120, 60),           # 120 req/min for standard metadata/history
}

def extract_client_ip(request: Request) -> str:
    """Extract client IP securely, respecting X-Forwarded-For only if incoming host is trusted."""
    remote_ip = request.client.host if request.client else "127.0.0.1"
    if remote_ip in TRUSTED_PROXIES:
        xff = request.headers.get("x-forwarded-for")
        if xff:
            client_candidate = xff.split(",")[0].strip()
            if client_candidate:
                return client_candidate
        x_real_ip = request.headers.get("x-real-ip")
        if x_real_ip:
            return x_real_ip.strip()
    return remote_ip


class SlidingWindowRateLimiter:
    """Thread-safe in-memory sliding window rate limiter with auto memory purging."""

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.enforce_for_testclient = False
        self._lock = Lock()
        # storage: key -> deque of timestamp floats
        self._requests: Dict[str, Deque[float]] = defaultdict(deque)
        self._last_cleanup = time.time()
        self._cleanup_interval = 120.0  # Run purge every 2 minutes

    def _get_category(self, path: str) -> str:
        """Map URL path to rate limit category."""
        if path.startswith("/api/cotton/predict") or path.startswith("/api/cotton/xai"):
            return "cotton_ml"
        elif path.startswith("/api/cotton/future-forecast"):
            return "future_forecast"
        elif path.startswith("/api/crop") or path.startswith("/api/yield"):
            return "crop_ml"
        elif path.startswith("/api/weather"):
            return "weather"
        return "general"

    def purge_expired_keys(self, now: float):
        """Purge stale IP keys whose requests have fully expired out of the sliding window."""
        max_window = 120.0  # Keep keys alive at most 2 minutes after last hit
        expired_keys = []
        for key, q in self._requests.items():
            while q and q[0] <= now - max_window:
                q.popleft()
            if not q:
                expired_keys.append(key)
        for k in expired_keys:
            del self._requests[k]
        self._last_cleanup = now

    def is_allowed(self, client_ip: str, path: str, custom_limit: Optional[Tuple[int, int]] = None) -> Tuple[bool, int, int, int]:
        """Check if request is allowed under current rate limits.
        
        Returns:
            (allowed: bool, limit: int, remaining: int, retry_after: int)
        """
        if not self.enabled:
            return True, 999999, 999999, 0

        # Exempt testclient from production quotas during automated test runs
        # unless enforce_for_testclient is explicitly enabled for security tests.
        if client_ip == "testclient" and not self.enforce_for_testclient and custom_limit is None:
            return True, 10000, 10000, 0

        category = self._get_category(path)
        max_requests, window_seconds = custom_limit or DEFAULT_QUOTAS.get(category, (120, 60))
        key = f"{client_ip}:{category}"
        now = time.time()
        window_start = now - window_seconds

        with self._lock:
            # Periodic memory cleanup
            if now - self._last_cleanup > self._cleanup_interval:
                self.purge_expired_keys(now)

            q = self._requests[key]
            # Evict timestamps outside sliding window
            while q and q[0] <= window_start:
                q.popleft()

            current_count = len(q)
            if current_count >= max_requests:
                # Quota exceeded
                oldest_timestamp = q[0]
                retry_after = max(1, int(oldest_timestamp + window_seconds - now))
                return False, max_requests, 0, retry_after

            # Record this request
            q.append(now)
            remaining = max_requests - len(q)
            return True, max_requests, remaining, 0

    def reset(self):
        """Clear all recorded request counters."""
        with self._lock:
            self._requests.clear()
            self.enforce_for_testclient = False
            self._last_cleanup = time.time()


# Global rate limiter instance
limiter = SlidingWindowRateLimiter(enabled=RATE_LIMIT_ENABLED)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI / Starlette middleware enforcing process-local rate limits."""

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        # Only rate-limit API routes, skip static docs / openapi schema
        if not path.startswith("/api/"):
            return await call_next(request)

        # Skip health probes
        if path in ("/api/health", "/api/ready"):
            return await call_next(request)

        # Extract client IP securely
        client_ip = extract_client_ip(request)

        allowed, limit, remaining, retry_after = limiter.is_allowed(client_ip, path)

        if not allowed:
            logger.warning("Rate limit exceeded for IP %s on path %s", client_ip, path)
            response = JSONResponse(
                status_code=429,
                content={
                    "status": "error",
                    "error_code": "RATE_LIMIT_EXCEEDED",
                    "message": "Too many requests. Please slow down and try again later.",
                    "detail": f"Rate limit exceeded for {path}. Maximum {limit} requests allowed per window."
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time() + retry_after)),
                }
            )
            return response

        # Proceed with request
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
