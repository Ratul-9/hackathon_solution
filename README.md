# BlackRock Auto-Save & Investment Engine

A high-performance, hybrid Python-C++ system designed to process large-scale financial transactions (up to $10^6$ constraints) using an optimized **Sweep-line Algorithm**. This engine automates rounding-based savings, validates them against complex financial and temporal rules, and calculates real-world returns for NPS and Index Fund portfolios.

## 🚀 System Architecture

The project utilizes a **Polyglot Architecture** to balance developer productivity with computational performance:
* **FastAPI Orchestrator (Python):** Handles the web interface, Pydantic data validation, and multi-stage financial filtering.
* **Core Logic Engine (C++):** A high-performance backend that executes the sweep-line algorithm for $O((N+Q+P) \log (N+Q+P))$ time complexity, ensuring millisecond responses even under heavy load.



---

## ✨ Features

* **Smart Rounding (Builder):** Automatically rounds expenses to the nearest ₹100 and calculates the investable remanent.
* **Financial Guardrails (Validator):** Enforces strict limits based on user wage (min of 10% annual income or ₹200,000 limit). Includes descriptive error messaging for invalid transactions.
* **Dynamic Rule Engine:**
    * **Q-Periods:** Implements a "Latest Start Date Wins" override rule using a priority-ordered sweep-line.
    * **P-Periods:** Supports additive investment rules for overlapping bonus periods.
* **Financial Forecasting:** Calculates inflation-adjusted real returns using historical benchmarks (7.11% for NPS, 14.49% for Index Funds).
* **Production Metrics:** Built-in performance reporting for memory usage, execution time, and system health.

---

## 🛠️ Technical Stack

* **Backend:** Python 3.13+, FastAPI
* **Engine:** C++17/20 (Optimized with `-O3`)
* **Data Parsing:** `nlohmann/json` (Integrated via CMake `FetchContent`)
* **Validation:** Pydantic v2
* **Environment:** Windows (executable built in `build/Debug/`)

---

## 📂 Project Structure

```text
root/
├── api/
│   └── main.py          # FastAPI Orchestrator & Multi-stage APIs
├── engine/
│   └── main.cpp         # C++ Sweep-line Core Logic
├── build/
│   └── Debug/
│       └── engine.exe   # Compiled High-Performance Binary
├── CMakeLists.txt       # C++ Build Configuration (FetchContent for JSON)
├── .gitignore           # Standard excludes (build/, __pycache__/, etc.)
└── README.md