BlackRock Auto-Save & Investment Engine

A high-performance, hybrid Python–C++ financial processing system designed to handle large-scale transactions (up to 10^6 constraints) using an optimized Sweep-Line Algorithm.

This engine automates rounding-based savings, validates them against complex financial and temporal rules, and computes real-world investment projections for NPS and Index Fund portfolios.

🚀 System Architecture

This project follows a Polyglot Architecture to balance developer productivity with computational performance.

🐍 FastAPI Orchestrator (Python)

REST API layer

Pydantic request/response validation

Multi-stage financial filtering

Pipeline orchestration

Triggers the C++ engine

⚡ Core Logic Engine (C++)

High-performance Sweep-line implementation

Time complexity:

O((N + Q + P) log (N + Q + P))

Efficient handling of up to 1,000,000 constraints

📂 Project Structure
root/
├── api/
│   └── main.py          # FastAPI Orchestrator & APIs
├── engine/
│   └── main.cpp         # C++ Sweep-line Core Logic
├── build/               # C++ build output (git ignored)
├── venv/                # Python virtual environment (git ignored)
├── CMakeLists.txt       # C++ Build config
├── compose.yaml         # Docker Compose config
├── Dockerfile           # Docker image definition
├── requirements.txt     # Python dependencies
└── README.md
⚙️ Local Setup & Installation
1️⃣ Build the C++ Engine

Make sure you have:

C++ Compiler (MSVC / MinGW / GCC)

CMake installed

mkdir build
cd build

cmake ..
cmake --build . --config Release

cd ..
2️⃣ Set Up Python Virtual Environment

Requires Python 3.11+

python -m venv venv

Activate virtual environment:

Windows

.\venv\Scripts\activate

macOS/Linux

source venv/bin/activate

Install dependencies:

pip install -r requirements.txt
3️⃣ Run Development Server
python -m uvicorn api.main:app --reload

Server runs at:

http://127.0.0.1:8000
🐳 Docker Deployment

The application is fully containerized.

🔹 Build & Run
docker build -t ratul9/blk-hacking-ind-ratul-mukherjee .
docker run -d -p 5477:5477 ratul9/blk-hacking-ind-ratul-mukherjee
🔹 Docker Compose
docker-compose up -d --build
📡 API Reference
1️⃣ Transaction Builder

POST /transactions:parse

Goal:
Rounds transaction amount to nearest 100 (ceiling) and calculates remanent.

Sample Request
[
  { 
    "date": "2023-02-28 15:49:20", 
    "amount": 375 
  }
]
2️⃣ Financial Validator

POST /transactions:validator

Goal:
Validates remanents against:

10% wage cap

₹2,00,000 maximum limit

Sample Request
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
3️⃣ Temporal Filter

POST /transactions:filter

Goal:

Validates date formats

Applies year constraints

Processes K-period fixed investments

Sample Request
{
  "wage": 50000,
  "q_periods": [
    {
      "start": "2023-07-01 00:00:00",
      "end": "2023-07-31 23:59:59",
      "fixed": 0
    }
  ],
  "transactions": []
}
4️⃣ Composite Orchestrators
POST /returns:nps
POST /returns:index

Goal:
Executes full pipeline and triggers the C++ Sweep-line engine.

Sample Request
{
  "age": 29,
  "wage": 50000,
  "inflation": 5.5,
  "q": [],
  "p": [],
  "k": [],
  "transactions": []
}
5️⃣ Performance Report

GET /performance-report

Sample Response

{
  "peakMB": 128,
  "totalEngineCalls": 42
}
📊 Performance Highlights

Handles up to 1,000,000 events

Optimized Sweep-Line processing

Logarithmic scaling

Low memory footprint

Production-ready Docker deployment

👤 Author

Ratul Mukherjee
B.Tech – Computer Science and Business Systems
Institute of Engineering and Management (IEM), Kolkata
