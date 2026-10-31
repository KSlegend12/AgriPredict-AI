"""
Security filter middleware for AgriPredict-AI.

Features:
- Request payload size protection (enforces 1MB maximum payload including chunked bodies).
- Path traversal and null byte rejection on URL paths.
- Context-aware security headers (HSTS over HTTPS or configured force, nosniff, DENY).
"""

import os
import logging
from urllib.parse import unquote
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger("agripredict.security")

# Maximum permitted payload size: 1 Megabyte (1,048,576 bytes)
MAX_PAYLOAD_SIZE = 1 * 1024 * 1024

FORCE_HSTS = os.getenv("FORCE_HSTS", "false").lower() in ("true", "1", "yes")

SUSPICIOUS_PATH_PATTERNS = [
    "..",        # Directory traversal
    "\x00",      # Null byte injection
    "%00",       # URL-encoded null byte
    "etc/passwd",
    "win.ini",
]

class SecurityFilterMiddleware(BaseHTTPMiddleware):
    """Enforces payload bounds, path traversal safety, and contextual security headers."""

    async def dispatch(self, request: Request, call_next):
        # 1. Inspect request path for traversal and poison bytes
        raw_path = request.url.path
        decoded_path = unquote(raw_path)

        for pattern in SUSPICIOUS_PATH_PATTERNS:
            if pattern in decoded_path:
                logger.warning("Suspicious request path rejected: %s", raw_path)
                return JSONResponse(
                    status_code=400,
                    content={
                        "status": "error",
                        "error_code": "SUSPICIOUS_REQUEST_PATH",
                        "detail": "Invalid characters or directory traversal detected in request path."
                    }
                )

        # 2. Check Content-Length header for early rejection
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                length = int(content_length)
                if length > MAX_PAYLOAD_SIZE:
                    logger.warning("Oversized payload rejected (Content-Length): %d bytes", length)
                    return JSONResponse(
                        status_code=413,
                        content={
                            "status": "error",
                            "error_code": "PAYLOAD_TOO_LARGE",
                            "detail": f"Request body exceeds maximum permitted size of {MAX_PAYLOAD_SIZE // 1024} KB."
                        }
                    )
            except ValueError:
                pass

        # 3. For state-changing methods, verify actual body size (including chunked requests)
        if request.method in ("POST", "PUT", "PATCH"):
            try:
                body = await request.body()
                if len(body) > MAX_PAYLOAD_SIZE:
                    logger.warning("Oversized body rejected (actual read): %d bytes", len(body))
                    return JSONResponse(
                        status_code=413,
                        content={
                            "status": "error",
                            "error_code": "PAYLOAD_TOO_LARGE",
                            "detail": f"Request body exceeds maximum permitted size of {MAX_PAYLOAD_SIZE // 1024} KB."
                        }
                    )
            except Exception as e:
                logger.error("Error reading request body: %s", e)
                return JSONResponse(
                    status_code=400,
                    content={"status": "error", "detail": "Malformed request body."}
                )

        # 4. Proceed to application
        response = await call_next(request)

        # 5. Inject defense-in-depth security response headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # RFC 6797: Only send HSTS over secure transport or when explicitly forced
        is_https = (
            request.url.scheme == "https"
            or request.headers.get("x-forwarded-proto") == "https"
            or FORCE_HSTS
        )
        if is_https:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response
