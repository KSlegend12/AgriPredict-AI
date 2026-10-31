# AgriPredict-AI — Project Run Guide (Windows / Production)

**Target Operating System:** Windows 10 / 11 (PowerShell / Command Prompt)  
**Demonstration Deadline:** November 2, 2026  
**Repository Path:** `C:\Users\karta\.gemini\antigravity\scratch\AgriPredict-AI`  

---

## 1. Prerequisites & Environment Requirements

Before launching the project, verify that the following runtimes are installed:

- **Python:** Version 3.10 to 3.13 (Verified on Python 3.13.7 x64)
- **Node.js:** Version 18.x or 20.x+ (Includes `npm`)
- **Git:** Optional (Note: do not commit or push modifications during evaluation)
- **Modern Web Browser:** Google Chrome, Microsoft Edge, or Mozilla Firefox

---

## 2. Directory Layout Overview

```text
AgriPredict-AI/
├── backend/
│   ├── main.py                  # FastAPI Application Entrypoint
│   ├── api/                     # REST API Routers (cotton, crop, weather, history)
│   ├── ml/                      # ML Inference Pipelines & SHAP Explainability
│   │   ├── artifacts/           # Serialized Model Artifacts (.pkl)
│   ├── database/                # SQLite Database Connector & Models (agripredict.db)
│   ├── schemas/                 # Pydantic V2 Request & Response Schemas
│   └── tests/                   # Pytest Test Suites (109 Tests)
├── frontend/
│   ├── src/                     # React 18 Source Code
│   │   ├── components/          # Reusable UI Components (Navbar, Footer, ErrorBoundary)
│   │   ├── pages/               # 12 Interactive Page Views
│   │   ├── services/            # Axios API Client Connectors
│   │   └── constants/           # Vidarbha District Constants & Benchmarks
│   ├── package.json             # Frontend Dependencies & Vite Scripts
│   └── vite.config.js           # Vite Configuration & Dev Server Proxy
├── data/
│   └── vidarbha_cotton_model_ready_1997_2024.csv  # Canonical Invariant Dataset
└── requirements.txt             # Python Backend Dependencies
```

---

## 3. Step-by-Step Launch Instructions

To demonstrate AgriPredict-AI, you will open **two separate terminal windows** (one for the FastAPI backend and one for the React frontend).

---

### Step 3.1 — Backend Startup (FastAPI)

1. Open **PowerShell** or **Command Prompt**.
2. Navigate to the project root directory:
   ```powershell
   cd "C:\Users\karta\.gemini\antigravity\scratch\AgriPredict-AI"
   ```
3. *(Optional / Recommended)* If using a Python virtual environment, activate it:
   ```powershell
   # If venv exists:
   .\venv\Scripts\Activate.ps1
   ```
4. Install backend dependencies (if not already installed):
   ```powershell
   pip install -r requirements.txt
   ```
5. Launch the FastAPI server with Uvicorn:
   ```powershell
   uvicorn backend.main:app --reload --port 8000
   ```
6. **Expected Backend Output:**
   ```text
   INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
   INFO:     Started reloader process
   INFO:     Started server process
   INFO:     Waiting for application startup.
   INFO:     Database tables verified / initialized.
   INFO:     Application startup complete.
   ```
7. **Verify Backend Health:**
   Open your browser or run:
   ```powershell
   curl http://127.0.0.1:8000/api/health
   ```
   *Expected Response:*
   ```json
   {
     "status": "ok",
     "is_model_loaded": true,
     "cotton": {
       "loaded": true,
       "candidate_thermal_loaded": true,
       "supported_districts": ["Akola", "Amravati", "Buldhana", "Nagpur", "Wardha", "Washim"]
     }
   }
   ```

---

### Step 3.2 — Frontend Startup (React / Vite)

1. Open a **second PowerShell** window.
2. Navigate to the `frontend` directory:
   ```powershell
   cd "C:\Users\karta\.gemini\antigravity\scratch\AgriPredict-AI\frontend"
   ```
3. Install frontend dependencies (if not already installed):
   ```powershell
   npm install
   ```
4. Start the Vite development server explicitly bound to local host:
   ```powershell
   npm run dev -- --host 127.0.0.1 --port 5173
   ```
5. **Expected Frontend Output:**
   ```text
     VITE v8.2.2  ready in 240 ms

     ➜  Local:   http://127.0.0.1:5173/
     ➜  Network: use --host to expose
     ➜  press h + enter to show help
   ```
6. Open your web browser and navigate to:
   ```
   http://127.0.0.1:5173
   ```

---

## 4. Database Setup & Persistence

- **Database Engine:** SQLite 3.
- **Database File:** `backend/agripredict.db` (auto-created on first server startup).
- **Initialization:** Automatic schema creation handles:
  - `cotton_prediction_history`: District, target year, predicted yield (kg/ha), model version, timestamp.
  - `prediction_history`: Crop type, NPK, pH, moisture, predicted yield (t/ha), timestamp.
- **Resetting Database (if needed):**
  To wipe historical test logs before the official demo, delete `backend/agripredict.db`; FastAPI will regenerate clean tables on the next request.

---

## 5. Running the Automated Test Suite

To verify backend integrity before presenting to evaluators:

```powershell
cd "C:\Users\karta\.gemini\antigravity\scratch\AgriPredict-AI"
python -m pytest backend/tests/ -v
```
- **Total Tests:** 109 tests.
- **Expected Result:** `109 passed, 34 warnings in ~9s`.

To verify the production frontend build:
```powershell
cd "C:\Users\karta\.gemini\antigravity\scratch\AgriPredict-AI\frontend"
npm run build
```
- **Expected Result:** Clean exit with `✓ built in <1s`.

---

## 6. Troubleshooting Common Issues

### Issue 1: Port 8000 or 5173 Already in Use
- **Symptom:** `[Errno 10048] error while attempting to bind on address ('127.0.0.1', 8000)`
- **Solution (PowerShell):**
  ```powershell
  # Find PID using port 8000:
  Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force
  # Find PID using port 5173:
  Get-Process -Id (Get-NetTCPConnection -LocalPort 5173).OwningProcess | Stop-Process -Force
  ```

### Issue 2: ModuleNotFoundError: No module named 'backend'
- **Cause:** Running python or uvicorn commands inside the `backend/` subfolder instead of the project root.
- **Solution:** Always run backend commands from `C:\Users\karta\.gemini\antigravity\scratch\AgriPredict-AI`.

### Issue 3: CORS or API Connection Refused
- **Symptom:** Browser shows `Failed to fetch` or `ERR_CONNECTION_REFUSED`.
- **Solution:** Ensure the backend terminal is running and responding at `http://127.0.0.1:8000/api/health`.

### Issue 4: PowerShell Script Execution Policy
- **Symptom:** `Activate.ps1 cannot be loaded because running scripts is disabled on this system.`
- **Solution:** Run in PowerShell as Administrator:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```
