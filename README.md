# ⚡ BlackRock Auto-Save & Investment Engine

> A high-performance, hybrid **Python–C++** financial processing system designed to handle large-scale transactions (up to **10⁶ constraints**) using an optimized **Sweep-Line Algorithm**. This engine automates rounding-based savings, validates them against complex financial and temporal rules, and computes real-world investment projections for **NPS** and **Index Fund** portfolios.

---

## 📑 Table of Contents

- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [File-by-File Breakdown](#-file-by-file-breakdown)
- [Pydantic Data Models](#-pydantic-data-models)
- [API Reference](#-api-reference)
  - [1. Transaction Builder](#1%EF%B8%8F⃣-transaction-builder)
  - [2. Financial Validator](#2%EF%B8%8F⃣-financial-validator)
  - [3. Temporal Filter](#3%EF%B8%8F⃣-temporal-filter)
  - [4. NPS Returns (Composite Orchestrator)](#4%EF%B8%8F⃣-nps-returns-composite-orchestrator)
  - [5. Index Fund Returns (Composite Orchestrator)](#5%EF%B8%8F⃣-index-fund-returns-composite-orchestrator)
  - [6. Performance Report](#6%EF%B8%8F⃣-performance-report)
- [C++ Sweep-Line Engine](#-c-sweep-line-engine)
- [Frontend Tester UI](#-frontend-tester-ui)
- [Prerequisites](#-prerequisites)
- [Local Setup & Installation](#%EF%B8%8F-local-setup--installation)
- [Docker Deployment](#-docker-deployment)
- [Running Tests](#-running-tests)
- [Environment & Configuration](#-environment--configuration)
- [Performance Highlights](#-performance-highlights)
- [Troubleshooting](#-troubleshooting)
- [Author](#-author)

---

## 🚀 System Architecture

This project follows a **Polyglot Architecture** to balance developer productivity with computational performance:

```
┌──────────────────────────────────────────────────────────────┐
│                     CLIENT / TESTER UI                       │
│              index.html (TailwindCSS + Chart.js)             │
│                    http://localhost:5477                      │
└────────────────────────────┬─────────────────────────────────┘
                             │  HTTP (JSON)
                             ▼
┌──────────────────────────────────────────────────────────────┐
│              🐍 FastAPI Orchestrator (Python)                 │
│                        api/main.py                           │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌────────────────────┐   │
│  │ :parse      │  │ :validator  │  │ :filter            │   │
│  │ Transaction │  │ Financial   │  │ Temporal           │   │
│  │ Builder     │  │ Validator   │  │ Validator          │   │
│  └──────┬──────┘  └──────┬──────┘  └─────────┬──────────┘   │
│         │                │                    │              │
│         └────────────────┼────────────────────┘              │
│                          ▼                                   │
│              ┌──────────────────────┐                        │
│              │  Orchestrator Layer  │                        │
│              │  :nps / :index       │                        │
│              └──────────┬───────────┘                        │
│                         │ subprocess.Popen (stdin/stdout)    │
└─────────────────────────┼────────────────────────────────────┘
                          ▼
┌──────────────────────────────────────────────────────────────┐
│               ⚡ C++ Sweep-Line Engine                        │
│                    engine/main.cpp                            │
│                                                              │
│  • Parses JSON via nlohmann/json                             │
│  • Sweep-line event processing                               │
│  • NPS/Index fund projection calculations                    │
│  • Indian tax slab computation                               │
│  • Prefix-sum range queries on K-periods                     │
│  • Outputs JSON to stdout                                    │
└──────────────────────────────────────────────────────────────┘
```

**Data Flow (Composite Endpoints — `:nps` / `:index`):**

1. **Parse** — Raw transactions are rounded to the nearest ₹100 ceiling; remanent (saved amount) is calculated.
2. **Validate** — Remanents are checked against the 10% annual wage cap or ₹2,00,000 hard limit. Duplicates are flagged.
3. **Filter** — Date formats are validated, duplicate timestamps are rejected, and Q/P/K period bounds are checked.
4. **Engine** — Valid, filtered data is piped to the C++ binary via `subprocess.Popen`. The engine runs the Sweep-Line algorithm and returns investment projections as JSON.

---

## 🛠 Tech Stack

| Layer           | Technology                                                 |
| --------------- | ---------------------------------------------------------- |
| **API Server**  | Python 3.11, FastAPI 0.129.0, Uvicorn 0.41.0               |
| **Validation**  | Pydantic v2.12.5                                           |
| **Core Engine** | C++17, nlohmann/json v3.11.3                               |
| **Build**       | CMake ≥ 3.16 (uses `FetchContent` for nlohmann/json)       |
| **Testing**     | pytest 9.0.2, FastAPI TestClient, unittest.mock            |
| **Frontend**    | HTML5, TailwindCSS (CDN), Chart.js, Inter & JetBrains Mono |
| **Container**   | Docker (python:3.11-slim-bookworm), Docker Compose         |
| **HTTP Client** | httpx 0.28.1 (for integration tests)                       |

---

## 📂 Project Structure

```
hackathon_root/
├── api/
│   ├── __init__.py               # Python package marker
│   └── main.py                   # FastAPI app — all endpoints, models, orchestrator logic (332 lines)
│
├── engine/
│   ├── main.cpp                  # C++ Sweep-Line core engine (209 lines)
│   └── Makefile                  # (Empty — build is handled via CMake)
│
├── tests/
│   ├── __init__.py               # Python package marker
│   ├── api_tests/
│   │   ├── test_transaction_builder.py     # 2 tests — ceiling/remanent calculation
│   │   ├── test_transaction_calculator.py  # 4 tests — engine mocking, error handling
│   │   ├── test_transaction_filter.py      # 9 tests — temporal validation edge cases
│   │   └── test_transaction_validator.py   # 4 tests — wage cap, duplicates
│   ├── engine_tests/
│   │   └── engine.cpp            # C++ unit test for sweep-line savings logic
│   └── integration_tests/
│       └── test_integrity.py     # End-to-end test against running Docker server
│
├── build/                        # C++ build output (gitignored)
├── myenv/                        # Python virtual environment (should be gitignored)
│
├── CMakeLists.txt                # CMake build configuration for C++ engine
├── compose.yaml                  # Docker Compose service definition
├── Dockerfile                    # Multi-stage Docker build (Python + C++)
├── index.html                    # Interactive Tester UI (485 lines)
├── pytest.ini                    # pytest configuration (sets pythonpath = .)
├── requirements.txt              # Pinned Python dependencies (22 packages)
├── .gitignore                    # OS, IDE, Python, C++, Docker ignores
└── README.md                     # This file
```

---

## 📄 File-by-File Breakdown

### `api/main.py` — FastAPI Application (332 lines)

The entire backend is contained in a single file for simplicity. Key sections:

| Section                 | Lines   | Description                                                                           |
| ----------------------- | ------- | ------------------------------------------------------------------------------------- |
| **Configuration**       | 17–25   | Auto-detects Docker vs. local Windows path for the C++ engine binary                  |
| **Pydantic Models**     | 30–70   | All request/response validation schemas                                               |
| **Application Setup**   | 76–85   | FastAPI init, CORS middleware (allow all origins), `tracemalloc` for memory profiling |
| **Individual APIs**     | 91–227  | Three standalone endpoints: `:parse`, `:validator`, `:filter`                         |
| **Orchestrator Logic**  | 232–283 | Internal pipeline that chains parse → validate → filter → C++ engine                  |
| **Composite Endpoints** | 289–297 | `:nps` and `:index` — thin wrappers over `run_orchestrator()`                         |
| **Performance Report**  | 301–332 | Memory, uptime, thread count, and algorithm complexity metadata                       |

**Engine Path Resolution:**

```python
if os.path.exists("/app/build/engine"):
    ENGINE_PATH = "/app/build/engine"          # Docker (Linux) path
else:
    ENGINE_PATH = os.path.join(ROOT_DIR, "build", "Debug", "engine.exe")  # Local Windows path
```

### `engine/main.cpp` — C++ Sweep-Line Engine (209 lines)

| Component                   | Description                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------- |
| `parse_date()`              | Converts date string to numeric timestamp by stripping non-digits                           |
| `Event` struct              | Represents sweep-line events (types: 1=P-start, 2=Q-start, 3=Transaction, 4=Q-end, 5=P-end) |
| `Transaction` struct        | Holds time, amount, ceiling, final_remanent, original_id                                    |
| `calculate_tax()`           | Indian income tax slab calculator (₹7L/10L/12L/15L brackets)                                |
| `calculate_nps_metrics()`   | NPS projection: 7.11% annual return, tax rebate under 80CCD                                 |
| `calculate_index_metrics()` | Index fund projection: 14.49% annual return                                                 |
| **Sweep-Line Loop**         | Processes sorted events — applies Q/P modifiers to transaction remanents                    |
| **K-Period Aggregation**    | Uses prefix sums + binary search for O(log N) range queries                                 |
| **Output**                  | Pretty-printed JSON via `nlohmann::ordered_json`                                            |

### `index.html` — Frontend Tester UI (485 lines)

A fully self-contained, single-page testing dashboard:

- **Dark theme** with glassmorphism panels
- **API selector dropdown** — dynamically shows/hides input fields per endpoint
- **JSON editors** for Q, P, K periods and transactions
- **Chart.js bar chart** for performance metrics visualization
- **Real-time latency measurement** for each API call
- Connects to `http://localhost:5477`

### `CMakeLists.txt` — Build Configuration

- Requires CMake ≥ 3.16
- Sets C++17 standard
- Uses `FetchContent` to pull `nlohmann/json` v3.11.3 from GitHub
- Builds `engine` executable from `engine/main.cpp`

### `Dockerfile` — Container Build

- **Base Image:** `python:3.11-slim-bookworm`
- **Build tools installed:** `build-essential`, `cmake`, `git`
- **Two-phase build:** C++ engine first, then Python dependencies
- **Exposes port 5477**
- **CMD:** `uvicorn api.main:app --host 0.0.0.0 --port 5477`

### `compose.yaml` — Docker Compose

```yaml
services:
  backend:
    image: ratul9/blk-hacking-ind-ratul-mukherjee
    ports:
      - "5477:5477"
    restart: always
```

---

## 📐 Pydantic Data Models

All models are defined in `api/main.py`:

### `Expense`

```python
class Expense(BaseModel):
    date: str                       # Format: "YYYY-MM-DD HH:MM:SS"
    amount: float = Field(..., gt=0)  # Must be positive
```

### `Transaction`

```python
class Transaction(BaseModel):
    id: str
    date: str
    amount: float
    ceiling: int                    # Nearest 100 (ceiling)
    remanent: float                 # ceiling - amount
    status: str = "valid"           # valid | invalid_exceeds_limit | duplicate | invalid_timestamp_format | etc.
```

### `WageData`

```python
class WageData(BaseModel):
    wage: float = Field(..., gt=0)  # Monthly wage (must be positive)
    transactions: List[Transaction]
```

### `Period`

```python
class Period(BaseModel):
    start: str                      # "YYYY-MM-DD HH:MM:SS"
    end: str                        # "YYYY-MM-DD HH:MM:SS"
    fixed: Optional[int] = None     # For Q-periods (overrides remanent)
    extra: Optional[int] = None     # For P-periods (adds to remanent)
```

### `TemporalValidationRequest`

```python
class TemporalValidationRequest(BaseModel):
    wage: float
    q_periods: List[Period]
    p_periods: List[Period]
    k_periods: List[Period]
    transactions: List[Transaction]
```

### `RawTransaction`

```python
class RawTransaction(BaseModel):
    date: str
    amount: float
```

### `ChallengeRequest` (Used by `:nps` and `:index`)

```python
class ChallengeRequest(BaseModel):
    age: int
    wage: float                     # Monthly wage
    inflation: float                # Percentage (e.g., 5.5 for 5.5%)
    q: List[Period]                 # Q-periods (fixed remanent overrides)
    p: List[Period]                 # P-periods (extra additive savings)
    k: List[Period]                 # K-periods (aggregation windows)
    transactions: List[RawTransaction]
```

---

## 📡 API Reference

**Base URL:** `http://localhost:5477`  
**API Prefix:** `/blackrock/challenge/v1`

---

### 1️⃣ Transaction Builder

**`POST /blackrock/challenge/v1/transactions:parse`**

Rounds each transaction amount up to the nearest ₹100 and calculates the **remanent** (savings = ceiling − amount).

**Request Body:** `List[Expense]`

```json
[
  { "date": "2023-02-28 15:49:20", "amount": 375 },
  { "date": "2023-03-05 10:15:00", "amount": 1020 }
]
```

**Response:** `200 OK` — `List[Transaction]`

```json
[
  {
    "id": "txn_0_a1b2",
    "date": "2023-02-28 15:49:20",
    "amount": 375.0,
    "ceiling": 400,
    "remanent": 25.0,
    "status": "valid"
  },
  {
    "id": "txn_1_c3d4",
    "date": "2023-03-05 10:15:00",
    "amount": 1020.0,
    "ceiling": 1100,
    "remanent": 80.0,
    "status": "valid"
  }
]
```

**Error:** `422 Unprocessable Entity` — if `amount <= 0` (Pydantic validation).

**cURL:**

```bash
curl -X POST http://localhost:5477/blackrock/challenge/v1/transactions:parse \
  -H "Content-Type: application/json" \
  -d '[{"date":"2023-02-28 15:49:20","amount":375}]'
```

---

### 2️⃣ Financial Validator

**`POST /blackrock/challenge/v1/transactions:validator`**

Validates remanents against:

- **10% of annual wage** (wage × 0.10)
- **₹2,00,000 absolute maximum**
- Whichever is lower is used as the cap.
- Detects **duplicate transaction IDs**.

**Request Body:** `WageData`

```json
{
  "wage": 50000,
  "transactions": [
    {
      "id": "txn_0",
      "date": "2023-02-28 15:49:20",
      "amount": 375,
      "ceiling": 400,
      "remanent": 25,
      "status": "valid"
    }
  ]
}
```

**Response:** `200 OK`

```json
{
  "valid_transactions": [
    {
      "id": "txn_0",
      "date": "2023-02-28 15:49:20",
      "amount": 375.0,
      "ceiling": 400,
      "remanent": 25.0,
      "status": "valid"
    }
  ],
  "invalid_transactions": [],
  "summary": {
    "total_invested": 25.0,
    "limit": 5000.0
  }
}
```

**Validation Rules:**
| Rule | Status Assigned |
|------|-----------------|
| Duplicate ID | `duplicate` |
| Exceeds wage cap / ₹2L limit | `invalid_exceeds_limit` |

**cURL:**

```bash
curl -X POST http://localhost:5477/blackrock/challenge/v1/transactions:validator \
  -H "Content-Type: application/json" \
  -d '{"wage":50000,"transactions":[{"id":"txn_0","date":"2023-02-28 15:49:20","amount":375,"ceiling":400,"remanent":25,"status":"valid"}]}'
```

---

### 3️⃣ Temporal Filter

**`POST /blackrock/challenge/v1/transactions:filter`**

Validates:

- Date format compliance (`YYYY-MM-DD HH:MM:SS`)
- Duplicate timestamps across transactions
- Period bounds (start ≤ end, within transaction date range)
- K-period cannot span multiple years

**Request Body:** `TemporalValidationRequest`

```json
{
  "wage": 50000,
  "q_periods": [
    {
      "start": "2023-07-01 00:00:00",
      "end": "2023-07-31 23:59:59",
      "fixed": 100
    }
  ],
  "p_periods": [
    {
      "start": "2023-06-01 00:00:00",
      "end": "2023-06-30 23:59:59",
      "extra": 50
    }
  ],
  "k_periods": [
    {
      "start": "2023-01-01 00:00:00",
      "end": "2023-12-31 23:59:59"
    }
  ],
  "transactions": [
    {
      "id": "txn_0",
      "date": "2023-07-15 12:00:00",
      "amount": 375,
      "ceiling": 400,
      "remanent": 25,
      "status": "valid"
    }
  ]
}
```

**Response:** `200 OK`

```json
{
  "valid_transactions": [ ... ],
  "invalid_transactions": [ ... ]
}
```

**Validation Error Reasons:**
| Scenario | Reason |
|----------|--------|
| Bad date format | `Date 'X' does not match required format YYYY-MM-DD HH:MM:SS` |
| Duplicate timestamp | `A transaction at timestamp X already exists.` |
| Already invalid status | `Transaction already has status: X` |
| Period start > end | `Start date (X) is after end date (Y).` |
| Period out of bounds | `Period is out of bounds for the current transaction set (X to Y).` |
| K-period multi-year | `K-period spans multiple years (X to Y), which is forbidden.` |

**cURL:**

```bash
curl -X POST http://localhost:5477/blackrock/challenge/v1/transactions:filter \
  -H "Content-Type: application/json" \
  -d '{"wage":50000,"q_periods":[],"p_periods":[],"k_periods":[],"transactions":[{"id":"txn_0","date":"2023-07-15 12:00:00","amount":375,"ceiling":400,"remanent":25,"status":"valid"}]}'
```

---

### 4️⃣ NPS Returns (Composite Orchestrator)

**`POST /blackrock/challenge/v1/returns:nps`**

Executes the **full pipeline** (parse → validate → filter → C++ engine) and returns NPS investment projections.

**NPS Assumptions (hardcoded in C++ engine):**

- Annual return rate: **7.11%**
- Investment horizon: `60 - age` years (minimum 5)
- Tax benefit calculated under **Section 80CCD** (max ₹2,00,000 or 10% of annual income)
- Indian tax slabs: ₹7L (10%), ₹10L (15%), ₹12L (20%), ₹15L+ (30%)

**Request Body:** `ChallengeRequest`

```json
{
  "age": 29,
  "wage": 50000,
  "inflation": 5.5,
  "q": [
    {
      "start": "2023-01-01 00:00:00",
      "end": "2023-12-31 23:59:59",
      "fixed": 100
    }
  ],
  "p": [
    {
      "start": "2023-06-01 00:00:00",
      "end": "2023-06-30 23:59:59",
      "extra": 50
    }
  ],
  "k": [
    {
      "start": "2023-01-01 00:00:00",
      "end": "2023-12-31 23:59:59"
    }
  ],
  "transactions": [
    { "date": "2023-02-28 15:49:20", "amount": 375 },
    { "date": "2023-03-05 10:15:00", "amount": 1020 },
    { "date": "2023-07-21 18:30:00", "amount": 499 }
  ]
}
```

**Response:** `200 OK`

```json
{
  "totalTransactionAmount": 1894.0,
  "totalCeiling": 2100.0,
  "savingsByDates": [
    {
      "start": "2023-01-01 00:00:00",
      "end": "2023-12-31 23:59:59",
      "amount": 300.0,
      "profit": 450.75,
      "taxBenefit": 0.0
    }
  ],
  "performance": {
    "executionTimeUs": 123,
    "complexity": "O(N log N)",
    "engine": "C++20 Optimized"
  }
}
```

**cURL:**

```bash
curl -X POST http://localhost:5477/blackrock/challenge/v1/returns:nps \
  -H "Content-Type: application/json" \
  -d '{"age":29,"wage":50000,"inflation":5.5,"q":[{"start":"2023-01-01 00:00:00","end":"2023-12-31 23:59:59","fixed":100}],"p":[],"k":[{"start":"2023-01-01 00:00:00","end":"2023-12-31 23:59:59"}],"transactions":[{"date":"2023-02-28 15:49:20","amount":375}]}'
```

---

### 5️⃣ Index Fund Returns (Composite Orchestrator)

**`POST /blackrock/challenge/v1/returns:index`**

Identical pipeline to NPS, but uses Index Fund projection parameters.

**Index Fund Assumptions (hardcoded in C++ engine):**

- Annual return rate: **14.49%**
- Investment horizon: `60 - age` years (minimum 5)
- No tax benefit (returns `taxBenefit: 0`)

**Request Body:** Same as NPS (`ChallengeRequest`).

**Response:** Same structure as NPS, with Index Fund-specific profit values.

**cURL:**

```bash
curl -X POST http://localhost:5477/blackrock/challenge/v1/returns:index \
  -H "Content-Type: application/json" \
  -d '{"age":29,"wage":50000,"inflation":5.5,"q":[],"p":[],"k":[{"start":"2023-01-01 00:00:00","end":"2023-12-31 23:59:59"}],"transactions":[{"date":"2023-06-15 12:00:00","amount":450}]}'
```

---

### 6️⃣ Performance Report

**`GET /blackrock/challenge/v1/performance-report`**

Returns system-wide resource utilization metrics. **No request body needed.**

**Response:** `200 OK`

```json
{
  "status": "operational",
  "metrics": {
    "uptimeSeconds": 342.56,
    "totalEngineCalls": 12,
    "memoryUsage": {
      "currentMB": 4.2301,
      "peakMB": 8.9145
    },
    "concurrency": {
      "activeThreads": 3,
      "engineType": "Subprocess-Isolated (C++)"
    }
  },
  "algorithmEfficiency": {
    "temporalComplexity": "O((N+Q+P) log (N+Q+P))",
    "spatialComplexity": "O(N+Q+P+K)",
    "batchCapacity": "1,000,000 transactions"
  }
}
```

**cURL:**

```bash
curl http://localhost:5477/blackrock/challenge/v1/performance-report
```

---

## ⚙ C++ Sweep-Line Engine

### Algorithm Overview

The engine uses a **Sweep-Line / Event-Based** approach:

1. **Event Creation:** Each transaction, Q-period boundary (start/end), and P-period boundary becomes an event.
2. **Sorting:** All events are sorted by timestamp, with event type as tiebreaker.
3. **Sweep:** The algorithm sweeps through events in chronological order:
   - **P-period start (type 1):** Adds `extra` to running P sum.
   - **Q-period start (type 2):** Adds to active Q set (priority by latest start).
   - **Transaction (type 3):** Calculates remanent — if a Q-period is active, uses its `fixed` value; adds current P sum.
   - **Q-period end (type 4):** Removes from active Q set.
   - **P-period end (type 5):** Subtracts `extra` from running P sum.
4. **Aggregation:** For each K-period, uses **prefix sums + binary search** to compute total invested amount in O(log N).
5. **Projection:** Applies NPS or Index Fund formulas with inflation adjustment.

### Event Type Codes

| Type | Meaning        | Priority                  |
| ---- | -------------- | ------------------------- |
| 1    | P-period start | Highest (processed first) |
| 2    | Q-period start |                           |
| 3    | Transaction    |                           |
| 4    | Q-period end   |                           |
| 5    | P-period end   | Lowest                    |

### Complexity

- **Time:** `O((N + Q + P) log(N + Q + P))` — dominated by sorting
- **Space:** `O(N + Q + P + K)` — stores all events + prefix sums

### Financial Formulas

**NPS:**

```
A = invested × (1 + 0.0711)^t
real_value = A / (1 + inflation)^t
profit = real_value - invested
tax_benefit = tax(wage) - tax(wage - min(invested, wage*0.10, 200000))
```

**Index Fund:**

```
A = invested × (1 + 0.1449)^t
real_value = A / (1 + inflation)^t
profit = real_value - invested
```

Where `t = max(60 - age, 5)`.

---

## 🖥 Frontend Tester UI

The `index.html` file is a standalone testing dashboard:

- Open directly in a browser: `file:///path/to/hackathon_root/index.html`
- Or serve via any HTTP server while the backend is running
- **Requires:** Backend running at `http://localhost:5477`
- **Features:**
  - Dropdown to select any of the 6 API endpoints
  - Smart UI — hides/shows input fields relevant to the selected endpoint
  - JSON formatting button
  - Real-time roundtrip latency display
  - Financial value display with ₹ formatting
  - Bar chart visualization for performance metrics (Chart.js)

---

## 📋 Prerequisites

| Tool               | Version                    | Purpose                          |
| ------------------ | -------------------------- | -------------------------------- |
| **Python**         | 3.11+                      | FastAPI server & tests           |
| **C++ Compiler**   | MSVC / MinGW / GCC (C++17) | Engine compilation               |
| **CMake**          | ≥ 3.16                     | C++ build system                 |
| **Git**            | Any                        | FetchContent pulls nlohmann/json |
| **Docker**         | 20.10+                     | Container deployment             |
| **Docker Compose** | v2+                        | Multi-container orchestration    |

---

## ⚙️ Local Setup & Installation

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd hackathon_root
```

### Step 2: Build the C++ Engine

```bash
mkdir build
cd build
cmake ..
cmake --build . --config Release
cd ..
```

> **Windows Note:** The built binary will be at `build/Debug/engine.exe` (Debug) or `build/Release/engine.exe` (Release). The FastAPI server auto-detects `build/Debug/engine.exe` for local Windows development.

> **Linux/macOS Note:** The binary will be at `build/engine`.

### Step 3: Set Up Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate — Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Activate — Windows (CMD)
.\venv\Scripts\activate.bat

# Activate — macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Run the Development Server

```bash
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 5477
```

**Server will be available at:** `http://localhost:5477`

### Step 5: Verify

```bash
# Quick health check
curl http://localhost:5477/blackrock/challenge/v1/performance-report

# Test a transaction parse
curl -X POST http://localhost:5477/blackrock/challenge/v1/transactions:parse \
  -H "Content-Type: application/json" \
  -d '[{"date":"2023-02-28 15:49:20","amount":375}]'
```

### Step 6: Open the Tester UI

Open `index.html` in your browser to use the interactive testing dashboard.

---

## 🐳 Docker Deployment

### Option 1: Build & Run Directly

```bash
# Build the Docker image
docker build -t ratul9/blk-hacking-ind-ratul-mukherjee .

# Run the container (detached mode)
docker run -d -p 5477:5477 --name blackrock-engine ratul9/blk-hacking-ind-ratul-mukherjee

# Check logs
docker logs blackrock-engine

# Stop the container
docker stop blackrock-engine

# Remove the container
docker rm blackrock-engine
```

### Option 2: Docker Compose

```bash
# Build and start (detached)
docker compose up -d --build

# View logs
docker compose logs -f

# Stop
docker compose down

# Rebuild and restart
docker compose up -d --build --force-recreate
```

### Option 3: Pull Pre-Built Image (if pushed to Docker Hub)

```bash
docker pull ratul9/blk-hacking-ind-ratul-mukherjee
docker run -d -p 5477:5477 ratul9/blk-hacking-ind-ratul-mukherjee
```

### Docker Quick Verification

```bash
# Wait a few seconds for the server to boot, then test:
curl http://localhost:5477/blackrock/challenge/v1/performance-report

# Full NPS pipeline test:
curl -X POST http://localhost:5477/blackrock/challenge/v1/returns:nps \
  -H "Content-Type: application/json" \
  -d '{
    "age": 25,
    "wage": 60000,
    "inflation": 5.0,
    "q": [{"start": "2023-01-01 00:00:00", "end": "2023-12-31 23:59:59", "fixed": 100}],
    "p": [],
    "k": [{"start": "2023-01-01 00:00:00", "end": "2023-12-31 23:59:59"}],
    "transactions": [
      {"date": "2023-06-15 12:00:00", "amount": 450}
    ]
  }'
```

### Dockerfile Internals

```dockerfile
FROM python:3.11-slim-bookworm

# Install: build-essential, cmake, git
# Copy engine source → build C++ binary
# Copy requirements.txt → pip install
# Copy api/ source
# EXPOSE 5477
# CMD: uvicorn api.main:app --host 0.0.0.0 --port 5477
```

---

## 🧪 Running Tests

### Python API Tests (via pytest)

```bash
# Activate your virtual environment first, then:

# Run ALL tests
pytest

# Run with verbose output
pytest -v

# Run specific test files
pytest tests/api_tests/test_transaction_builder.py -v
pytest tests/api_tests/test_transaction_validator.py -v
pytest tests/api_tests/test_transaction_filter.py -v
pytest tests/api_tests/test_transaction_calculator.py -v

# Run a specific test function
pytest tests/api_tests/test_transaction_builder.py::test_build_transactions_success -v
```

### Test Suite Summary

| File                             | Tests | What's Tested                                                                                                                                                     |
| -------------------------------- | ----- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `test_transaction_builder.py`    | 2     | Ceiling/remanent calculation, negative amount rejection (422)                                                                                                     |
| `test_transaction_validator.py`  | 4     | All valid pass, wage-cap enforcement, duplicate ID detection, invalid wage (422)                                                                                  |
| `test_transaction_filter.py`     | 9     | Valid payload, bad date format, duplicate timestamp, period start > end, out-of-bounds, K-period multi-year, missing Q-fixed, missing P-extra, empty transactions |
| `test_transaction_calculator.py` | 4     | Successful C++ engine call (mocked), engine error handling, engine not found, only valid transactions forwarded                                                   |

### Integration Test (requires running server)

```bash
# Start the server first (locally or via Docker), then:
python tests/integration_tests/test_integrity.py
```

This sends a full NPS payload to `http://localhost:5477` and prints the result.

### C++ Engine Tests

```bash
# The engine test is in tests/engine_tests/engine.cpp
# It requires linking against the engine functions (not standalone)
# Build and run alongside the main engine build if needed
```

---

## 🔧 Environment & Configuration

### Port

The application **must** run on port **5477**. This is configured in:

- `Dockerfile` (`EXPOSE 5477` + CMD `--port 5477`)
- `compose.yaml` (port mapping `5477:5477`)
- `index.html` (`baseUrl = "http://localhost:5477"`)
- `tests/integration_tests/test_integrity.py` (`http://localhost:5477`)

### CORS

CORS is configured to allow **all origins** (`allow_origins=["*"]`), all methods, and all headers.

### Engine Binary Path

| Environment   | Path                                    |
| ------------- | --------------------------------------- |
| Docker        | `/app/build/engine`                     |
| Local Windows | `<project_root>/build/Debug/engine.exe` |

### Python Dependencies (requirements.txt)

```
fastapi==0.129.0        # Web framework
uvicorn==0.41.0         # ASGI server
pydantic==2.12.5        # Data validation
httpx==0.28.1           # HTTP client (for testing)
pytest==9.0.2           # Test framework
colorama==0.4.6         # Terminal colors
starlette==0.52.1       # ASGI utilities (FastAPI dependency)
```

---

## 📊 Performance Highlights

| Metric               | Value                          |
| -------------------- | ------------------------------ |
| **Max Events**       | 1,000,000 transactions         |
| **Time Complexity**  | `O((N+Q+P) log(N+Q+P))`        |
| **Space Complexity** | `O(N+Q+P+K)`                   |
| **Engine Isolation** | Subprocess (stdin/stdout pipe) |
| **Memory Profiling** | `tracemalloc` built-in         |
| **Startup Time**     | < 2 seconds (Docker)           |

---

## ❓ Troubleshooting

### Common Issues

| Issue                                          | Solution                                                                                       |
| ---------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `Connection Refused` on port 5477              | Ensure the server is running (`docker ps` or check uvicorn output)                             |
| `Engine binary not found`                      | Build the C++ engine first (`cmake --build . --config Release`)                                |
| `cmake` not found                              | Install CMake: `winget install Kitware.CMake` (Windows) or `apt install cmake`                 |
| `FetchContent` fails                           | Ensure Git is installed and network access is available (nlohmann/json is fetched from GitHub) |
| `422 Unprocessable Entity`                     | Check request body matches the Pydantic model exactly (see [Models](#-pydantic-data-models))   |
| `500 Internal Server Error` on `:nps`/`:index` | C++ engine crashed — check stderr output; verify engine binary exists                          |
| Docker build fails at cmake step               | Ensure `engine/main.cpp` exists and Git is available inside container                          |
| Frontend shows `Connection Refused`            | Backend must be running at `http://localhost:5477`                                             |
| Tests fail with `ModuleNotFoundError`          | Activate virtualenv; ensure `pytest.ini` has `pythonpath = .`                                  |
| `invalid_timestamp_format`                     | Dates must use format `YYYY-MM-DD HH:MM:SS` (24-hour)                                          |

### Docker Debugging

```bash
# Check if container is running
docker ps

# View real-time logs
docker logs -f blackrock-engine

# Shell into running container
docker exec -it blackrock-engine bash

# Test C++ engine directly inside container
echo '{"mode":"nps","age":25,"wage":50000,"inflation":0.05,"q_periods":[],"p_periods":[],"k_periods":[],"transactions":[]}' | /app/build/engine

# Restart container
docker restart blackrock-engine
```

---

## 👤 Author

**Ratul Mukherjee**  
B.Tech – Computer Science and Business Systems  
Institute of Engineering and Management (IEM), Kolkata
