# 📜 Full Application Audit & Resolution Log

This document provides a comprehensive, step-by-step audit of all questions asked, issues encountered, root cause analyses, code modifications, and system enhancements executed for the **Broker Platform Backend** project.

---

## 📑 Table of Contents
1. [Initial Setup & Server Execution](#1-initial-setup--server-execution)
2. [Unit Test Suite & Property-Based Stress Test Fix](#2-unit-test-suite--property-based-stress-test-fix)
3. [Authentication Credentials & Account Access](#3-authentication-credentials--account-access)
4. [Swagger UI vs cURL Authentication Fix (`422 Unprocessable Content`)](#4-swagger-ui-vs-curl-authentication-fix-422-unprocessable-content)
5. [Admin API Key vs Bearer Token Resolution (`403 Forbidden`)](#5-admin-api-key-vs-bearer-token-resolution-403-forbidden)
6. [Swagger UI Header Authorization Walkthrough (`401 Unauthorized`)](#6-swagger-ui-header-authorization-walkthrough-401-unauthorized)
7. [Group Endpoint Validation & Query Filtering (`422 Validation Error`)](#7-group-endpoint-validation--query-filtering-422-validation-error)
8. [Multi-Domain Isolated API Service Modes (`SERVICE_MODE`)](#8-multi-domain-isolated-api-service-modes-service_mode)
9. [Complete File Changes & Modified Files Summary](#9-complete-file-changes--modified-files-summary)

---

## 1. Initial Setup & Server Execution

### ❓ Question / Context
How to start and run the FastAPI server locally.

### 🛠️ Execution Steps
```bash
# 1. Navigate to the working project folder
cd e:\references-for-AIs-to-read-main\qwe-agen-broker-platform-backend\work\bp

# 2. Ensure virtual environment dependencies are installed
pip install -e ".[dev]"

# 3. Start the FastAPI development server with auto-reload
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```
Interactive Swagger UI documentation becomes available at: `http://localhost:8000/docs`.

---

## 2. Unit Test Suite & Property-Based Stress Test Fix

### ❌ Issue Encountered
When running full pytest test suite (`pytest tests -q`), `TestPropertyBasedGroupLogic` failed under heavy load due to Hypothesis framework timing checks (`HealthCheck.too_slow`).

### 🔍 Root Cause
Hypothesis property tests generate dozens of randomized synthetic inputs per test run. Under CPU load, input generation occasionally exceeded Hypothesis default execution threshold, causing artificial test failure.

### 🛠️ Code Fix
Modified [`tests/unit/domains/accounts/test_account_models_stress.py`](file:///e:/references-for-AIs-to-read-main/qwe-agen-broker-platform-backend/work/bp/tests/unit/domains/accounts/test_account_models_stress.py):
```python
from hypothesis import HealthCheck, given, settings

class TestPropertyBasedGroupLogic:
    @settings(suppress_health_check=[HealthCheck.too_slow])
    @given(...)
    def test_group_rules(self, ...):
        ...
```

### 🟢 Verification
All 24 stress tests passed cleanly (`24 passed in 3.42s`).

---

## 3. Authentication Credentials & Account Access

### ❓ Question
What are the passwords and credentials for testing client login endpoints?

### 🔑 Verified Credentials
* **Test Client Account 1:** Login ID `887914`, Password `Password123!`
* **Test Client Account 2:** Login ID `744209`, Password `Password123!`
* **Admin API Key (Server Secret):** `1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f` (configured in [`.env`](file:///e:/references-for-AIs-to-read-main/qwe-agen-broker-platform-backend/work/bp/.env))

---

## 4. Swagger UI vs cURL Authentication Fix (`422 Unprocessable Content`)

### ❌ Issue Encountered
`POST /api/v1/auth/login` returned `200 OK` when executed via terminal cURL, but returned `422 Unprocessable Content` / `Invalid credentials` when executed in Swagger UI (`http://127.0.0.1:8000/docs`).

### 🔍 Root Cause
1. Swagger UI's Authorize modal submits credentials using `application/x-www-form-urlencoded` format (`username=887914&password=Password123!`).
2. Standard REST clients (cURL, Postman) submit credentials using `application/json` format (`{"login_id": "887914", "password": "Password123!"}`).
3. FastAPI's parameter validator intercepted the form-encoded payload before endpoint execution and threw a `422 Unprocessable Content` error.

### 🛠️ Code Fix
Updated [`api/routers/auth.py`](file:///e:/references-for-AIs-to-read-main/qwe-agen-broker-platform-backend/work/bp/api/routers/auth.py) using `openapi_extra` to support multi-format content handling without parameter validation errors:
```python
@router.post(
    "/login",
    response_model=TokenResponse,
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/LoginRequest"}
                },
                "application/x-www-form-urlencoded": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "username": {"type": "string", "example": "887914"},
                            "password": {"type": "string", "example": "Password123!"}
                        },
                        "required": ["username", "password"]
                    }
                }
            }
        }
    }
)
```
Also added default example values to `LoginRequest` in [`api/schemas/account.py`](file:///e:/references-for-AIs-to-read-main/qwe-agen-broker-platform-backend/work/bp/api/schemas/account.py).

### 🟢 Verification
* **JSON Login (cURL):** `HTTP 200 OK`
* **Form OAuth2 Login (Swagger UI):** `HTTP 200 OK`

---

## 5. Admin API Key vs Bearer Token Resolution (`403 Forbidden`)

### ❌ Issue Encountered
Request to `GET /api/v1/admin/groups/schema` returned `403 Forbidden: Invalid X-Admin-API-Key header`.

### 🔍 Root Cause
A **JWT Access Token** (`eyJhbGciOi...`) was entered into the `X-Admin-API-Key` header field.

The platform enforces two separate authentication paths for Admin endpoints:
1. `X-Admin-API-Key` header: Expects the static server secret key `ADMIN_API_KEY` defined in [`.env`](file:///e:/references-for-AIs-to-read-main/qwe-agen-broker-platform-backend/work/bp/.env) (`1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f`).
2. `Authorization: Bearer <token>` header: Expects a **Manager JWT token** (with `is_manager: True`). A client token (`role: client`) is rejected.

### 🟢 Solution & Verification
Passed the correct `ADMIN_API_KEY` in `X-Admin-API-Key`:
```bash
curl -X GET 'http://127.0.0.1:8000/api/v1/admin/groups/schema' \
  -H 'accept: application/json' \
  -H 'X-Admin-API-Key: 1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f'
```
**Response:** `HTTP 200 OK` with 44 MT5 group schema field descriptors.

---

## 6. Swagger UI Header Authorization Walkthrough (`401 Unauthorized`)

### ❌ Issue Encountered
Executing `GET /api/v1/admin/groups/schema` in Swagger UI returned `401 Unauthorized: X-Admin-API-Key or a manager Bearer token is required`.

### 🔍 Root Cause
Clicking **Try it out** -> **Execute** without filling in the global **Authorize 🔓** modal causes Swagger UI to send HTTP requests with no authorization headers attached.

### 🛠️ Step-by-Step Authorization Instructions
1. Open `http://127.0.0.1:8000/docs` in your browser.
2. Click the green **Authorize 🔓** button at the top right of the page.
3. In the `admin_api_key_header (apiKey)` input box, paste:
   `1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f`
4. Click **Authorize** -> **Close**.
5. All subsequent requests in Swagger UI automatically attach the required `X-Admin-API-Key` header.

---

## 7. Group Endpoint Validation & Query Filtering (`422 Validation Error`)

### ❌ Issue Encountered
`GET /api/v1/admin/groups` returned `Validation Error` (HTTP 422) when triggered from Swagger UI.

### 🔍 Root Cause
HTTP 422 is raised by FastAPI/Pydantic when input parameters fail schema validation (e.g. entering an invalid type into query boxes or attempting to run POST endpoints without mandatory body fields).

### 🛠️ Resolution & Filtering Usage
`GET /api/v1/admin/groups` supports an optional query parameter `account_type`:
* **Get All Groups:** Leave `account_type` blank.
* **Filter Real Groups:** Set `account_type=real`.
* **Filter Demo Groups:** Set `account_type=demo`.

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/admin/groups?account_type=real" \
  -H "accept: application/json" \
  -H "X-Admin-API-Key: 1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f"
```
**Response:** `HTTP 200 OK` (returns `real\real-SF`, `real\real-A`, `real\real`).

---

## 8. Multi-Domain Isolated API Service Modes (`SERVICE_MODE`)

### 💡 Feature Request
Capability to isolate and run specific domain API suites individually (e.g., running only Manager APIs for dealer desktop terminal integration).

### 🛠️ Implementation
Updated [`api/main.py`](file:///e:/references-for-AIs-to-read-main/qwe-agen-broker-platform-backend/work/bp/api/main.py) to read the `SERVICE_MODE` environment variable and mount routers dynamically:

```python
service_mode = os.getenv("SERVICE_MODE", "all").lower()

if service_mode == "manager":
    # Mounts ONLY Manager & Auth APIs
    app.include_router(auth.router)
    app.include_router(manager_trading.router)
    app.include_router(manager_main.router)
    app.include_router(manager_connection.router)
    app.include_router(manager_service.router)
    app.include_router(manager_subscriptions.router)
    app.include_router(ws_endpoints.router)
elif service_mode == "client":
    # Mounts ONLY Client & Trading APIs
    app.include_router(auth.router)
    app.include_router(trade.router)
    app.include_router(account.router)
    app.include_router(market_data.router)
    app.include_router(ws_endpoints.router)
elif service_mode == "admin":
    # Mounts ONLY Admin & Backoffice APIs
    app.include_router(auth.router)
    app.include_router(admin_groups.router)
    app.include_router(admin_accounts.accounts_router)
    app.include_router(admin_reads.account_reads_router)
    ...
else:
    # Mounts ALL Institutional Brokerage Routers
    ...
```

### 🚀 Commands to Run Each Plane Individually

| Plane / Domain | PowerShell Command | Default Port | Description |
|---|---|---|---|
| **Client / Trader** | `$env:SERVICE_MODE="client"; python -m uvicorn api.main:app --reload --port 8000` | 8000 | Client auth, order execution, balances, market data |
| **Manager / Dealer** | `$env:SERVICE_MODE="manager"; python -m uvicorn api.main:app --reload --port 8001` | 8001 | Dealer desk, trade overrides, manager connection |
| **Admin / Backoffice** | `$env:SERVICE_MODE="admin"; python -m uvicorn api.main:app --reload --port 8002` | 8002 | Group CRUD, account management, risk & read planes |
| **Unified Full Suite** | `python -m uvicorn api.main:app --reload --port 8003` | 8003 | Full combined institutional platform |

---

## 9. Complete File Changes & Modified Files Summary

1. **[`api/main.py`](file:///e:/references-for-AIs-to-read-main/qwe-agen-broker-platform-backend/work/bp/api/main.py):**
   Added dynamic `SERVICE_MODE` filtering (`client`, `manager`, `admin`, `all`).
2. **[`api/routers/auth.py`](file:///e:/references-for-AIs-to-read-main/qwe-agen-broker-platform-backend/work/bp/api/routers/auth.py):**
   Added `openapi_extra` multi-format payload handling (`application/json` & `application/x-www-form-urlencoded`).
3. **[`api/schemas/account.py`](file:///e:/references-for-AIs-to-read-main/qwe-agen-broker-platform-backend/work/bp/api/schemas/account.py):**
   Added OpenAPI sample values (`887914` / `Password123!`) to `LoginRequest`.
4. **[`tests/unit/domains/accounts/test_account_models_stress.py`](file:///e:/references-for-AIs-to-read-main/qwe-agen-broker-platform-backend/work/bp/tests/unit/domains/accounts/test_account_models_stress.py):**
   Suppressed timing health check on Hypothesis stress tests (`HealthCheck.too_slow`).
5. **[`chat/chat.md`](file:///e:/references-for-AIs-to-read-main/chat/chat.md):**
   Updated partner execution log with entries `#01` through `#20`.
6. **[`audit.md`](file:///e:/references-for-AIs-to-read-main/audit.md):**
   Created full technical audit document.
