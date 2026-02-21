import math
import time
import tracemalloc
import subprocess
import json
import uuid
import os
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field
from datetime import datetime
import threading


# --- CONFIGURATION ---
if os.path.exists("/app/build/engine"):
    # Docker Path
    ENGINE_PATH = "/app/build/engine"
else:
    # Local Windows Path
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ROOT_DIR = os.path.dirname(BASE_DIR)
    ENGINE_PATH = os.path.join(ROOT_DIR, "build", "Debug", "engine.exe")# ---------------------------------------------------------
# 1. Pydantic Models (Validation Schemas)
# ---------------------------------------------------------

# Individual API Models
class Expense(BaseModel):
    date: str
    amount: float = Field(..., gt=0)

class Transaction(BaseModel):
    id: str
    date: str
    amount: float
    ceiling: int
    remanent: float
    status: str = "valid"

class WageData(BaseModel):
    wage: float = Field(..., gt=0)
    transactions: List[Transaction]

class Period(BaseModel):
    start: str
    end: str
    fixed: Optional[int] = None
    extra: Optional[int] = None

class TemporalValidationRequest(BaseModel):
    wage: float
    q_periods: List[Period]
    p_periods: List[Period]
    k_periods: List[Period]
    transactions: List[Transaction]

# Composite Orchestrator Models (Matching Screenshot 10)
class RawTransaction(BaseModel):
    date: str
    amount: float

class ChallengeRequest(BaseModel):
    age: int
    wage: float
    inflation: float
    q: List[Period]
    p: List[Period]
    k: List[Period]
    transactions: List[RawTransaction]

# ---------------------------------------------------------
# 2. Application Setup & Global Metrics
# ---------------------------------------------------------

app = FastAPI(title="BlackRock Auto-Save Engine")
tracemalloc.start()
start_time = time.time()
engine_calls = 0

# ---------------------------------------------------------
# 3. Individual APIs (Existing Logic)
# ---------------------------------------------------------

@app.post("/blackrock/challenge/v1/transactions:parse", response_model=List[Transaction])
async def api_build_transactions(expenses: List[Expense]):
    """Calculates ceiling (multiple of 100) and remanent."""
    transactions = []
    for idx, exp in enumerate(expenses):
        ceiling = math.ceil(exp.amount / 100.0) * 100
        remanent = ceiling - exp.amount
        transactions.append(Transaction(
            id=f"txn_{idx}_{uuid.uuid4().hex[:4]}",
            date=exp.date,
            amount=exp.amount,
            ceiling=ceiling,
            remanent=remanent
        ))
    return transactions

@app.post("/blackrock/challenge/v1/transactions:validator")
async def api_validate_financials(data: WageData):
    """Validates against 10% annual income or 2L max limit."""
    valid, invalid, seen_ids = [], [], set()
    total_invested = 0
    # Annual investment limit is 10% of wage or 200,000
    max_investment = min(data.wage * 0.10, 200000.0)

    for txn in data.transactions:
        # 1. Check for Duplicate IDs
        if txn.id in seen_ids:
            txn.status = "duplicate"
            invalid.append({
                "transaction": txn,
                "reason": f"Transaction ID '{txn.id}' has already been processed."
            })
            continue
            
        # 2. Check for Investment Limit Breach
        if total_invested + txn.remanent > max_investment:
            txn.status = "invalid_exceeds_limit"
            invalid.append({
                "transaction": txn,
                "reason": f"Adding {txn.remanent} would exceed your max investment limit of {max_investment}. Current total: {total_invested}."
            })
        
        # 3. Mark as Valid
        else:
            txn.status = "valid"
            total_invested += txn.remanent
            valid.append(txn)
            seen_ids.add(txn.id)
            
    return {
        "valid_transactions": valid, 
        "invalid_transactions": invalid,
        "summary": {
            "total_invested": total_invested,
            "limit": max_investment
        }
    }
@app.post("/blackrock/challenge/v1/transactions:filter")
async def api_temporal_validate(data: TemporalValidationRequest):
    """Checks date formats and k-period year constraints with descriptive error messages."""
    valid_txns = []
    invalid_txns = []
    period_errors = []
    seen_ts = set()
    parsed_dates = []

    # 1. Validate Transactions
    for txn in data.transactions:
        # Skip transactions already marked invalid by previous APIs
        if txn.status != "valid":
            invalid_txns.append({
                "transaction": txn,
                "reason": f"Transaction already has status: {txn.status}"
            })
            continue
            
        try:
            # Enforce strict format: YYYY-MM-DD HH:MM:SS
            dt = datetime.strptime(txn.date, "%Y-%m-%d %H:%M:%S")
            
            # Check for duplicate timestamps (t_i != t_j)
            if txn.date in seen_ts:
                txn.status = "invalid_duplicate_timestamp"
                invalid_txns.append({
                    "transaction": txn,
                    "reason": f"A transaction at timestamp {txn.date} already exists."
                })
            else:
                seen_ts.add(txn.date)
                parsed_dates.append(dt)
                valid_txns.append(txn)
                
        except ValueError:
            txn.status = "invalid_timestamp_format"
            invalid_txns.append({
                "transaction": txn,
                "reason": f"Date '{txn.date}' does not match required format YYYY-MM-DD HH:MM:SS"
            })

    # 2. Extract bounds and Validate Periods
    if parsed_dates:
        min_t, max_t = min(parsed_dates), max(parsed_dates)
        
        def check_bounds(periods: List[Period], name: str):
            for i, p in enumerate(periods):
                try:
                    s_dt = datetime.strptime(p.start, "%Y-%m-%d %H:%M:%S")
                    e_dt = datetime.strptime(p.end, "%Y-%m-%d %H:%M:%S")
                    
                    # Rule: Start must be before End
                    if s_dt > e_dt:
                        period_errors.append({
                            "period": f"{name}_{i}",
                            "reason": f"Start date ({p.start}) is after end date ({p.end})."
                        })
                    
                    # Rule: min(t_i) <= start <= end <= max(t_i)
                    if s_dt < min_t or e_dt > max_t:
                        period_errors.append({
                            "period": f"{name}_{i}",
                            "reason": f"Period is out of bounds for the current transaction set ({min_t} to {max_t})."
                        })
                        
                    # Rule: K-periods cannot span multiple years
                    if name == "k" and s_dt.year != e_dt.year:
                        period_errors.append({
                            "period": f"k_{i}",
                            "reason": f"K-period spans multiple years ({s_dt.year} to {e_dt.year}), which is forbidden."
                        })
                        
                except ValueError:
                    period_errors.append({
                        "period": f"{name}_{i}",
                        "reason": "One or more timestamps in this period have an invalid format."
                    })

        check_bounds(data.q_periods, "q")
        check_bounds(data.p_periods, "p")
        check_bounds(data.k_periods, "k")
    else:
        period_errors.append({
            "period": "global",
            "reason": "No valid transactions available to establish temporal bounds."
        })

    return {
        "valid_transactions": valid_txns,
        "invalid_transactions": invalid_txns,
    }
# ---------------------------------------------------------
# 4. Composite Orchestrator Logic
# ---------------------------------------------------------

def internal_build_transactions(raw_txns: List[RawTransaction]) -> List[Transaction]:
    processed = []
    for idx, exp in enumerate(raw_txns):
        # Handle the -10 edge case from your image
        if exp.amount <= 0:
            status = "invalid_amount"
            ceiling, remanent = 0, 0
        else:
            status = "valid"
            ceiling = math.ceil(exp.amount / 100.0) * 100
            remanent = ceiling - exp.amount
            
        processed.append(Transaction(
            id=f"txn_{idx}_{uuid.uuid4().hex[:4]}",
            date=exp.date,
            amount=exp.amount,
            ceiling=ceiling,
            remanent=remanent,
            status=status # <-- Passes the status down the pipeline
        ))
    return processed

async def run_orchestrator(data: ChallengeRequest, mode: str):
    global engine_calls
    # Use existing logic as internal methods
    expenses = [Expense(date=t.date, amount=t.amount) for t in data.transactions]
    built = await api_build_transactions(expenses)
    
    wage_data = WageData(wage=data.wage, transactions=built)
    validated = await api_validate_financials(wage_data)
    
    temp_req = TemporalValidationRequest(
        wage=data.wage, q_periods=data.q, p_periods=data.p, k_periods=data.k, 
        transactions=validated["valid_transactions"]
    )
    filtered = await api_temporal_validate(temp_req)

    # Payload for C++
    engine_payload = {
        "mode": mode,
        "age": data.age,
        "wage": data.wage,
        "inflation": data.inflation,
        "q_periods": [p.model_dump() for p in data.q],
        "p_periods": [p.model_dump() for p in data.p],
        "k_periods": [p.model_dump() for p in data.k],
        "transactions": [t.model_dump() for t in filtered["valid_transactions"]]
    }

    engine_calls += 1
    process = subprocess.Popen([ENGINE_PATH], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate(input=json.dumps(engine_payload))

    if process.returncode != 0: raise HTTPException(status_code=500, detail=stderr)
    return Response(content=stdout, media_type="application/json")

# ---------------------------------------------------------
# 5. Final Composite Endpoints
# ---------------------------------------------------------

@app.post("/blackrock/challenge/v1/returns:nps")
async def get_nps(data: ChallengeRequest):
    """NPS orchestrator returning format from screenshot."""
    return await run_orchestrator(data, mode="nps")

@app.post("/blackrock/challenge/v1/returns:index")
async def get_index(data: ChallengeRequest):
    """Index Fund orchestrator returning format from screenshot."""
    return await run_orchestrator(data, mode="index")



@app.get("/blackrock/challenge/v1/performance-report")
async def performance_report():
    """
    v) Performance Report
    Outputs system-wide resource utilization metrics.
    """
    # 1. Get memory metrics (Current and Peak)
    current, peak = tracemalloc.get_traced_memory()
    
    # 2. Calculate total uptime since start_time
    uptime = time.time() - start_time
    
    # 3. Count active Python threads
    # This shows how many concurrent requests are being managed
    active_threads = threading.active_count()

    return {
        "status": "operational",
        "metrics": {
            "uptimeSeconds": round(uptime, 2),
            "totalEngineCalls": engine_calls,
            "memoryUsage": {
                "currentMB": round(current / 10**6, 4),
                "peakMB": round(peak / 10**6, 4)
            },
            "concurrency": {
                "activeThreads": active_threads,
                "engineType": "Subprocess-Isolated (C++)"
            }
        },
        "algorithmEfficiency": {
            "temporalComplexity": "O((N+Q+P) log (N+Q+P))", # Sweep-line complexity
            "spatialComplexity": "O(N+Q+P+K)", # Memory complexity
            "batchCapacity": "1,000,000 transactions" # Based on constraints
        }
    }