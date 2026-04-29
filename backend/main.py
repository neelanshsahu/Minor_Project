"""
MediVault — FastAPI Backend Entry Point
========================================
Provides REST API endpoints for the SMPC healthcare data collaboration system.

Endpoints:
    POST /api/init-session       → Initialize SMPC session with N parties
    POST /api/upload-shares      → Party uploads their encrypted shares
    GET  /api/compute-aggregate  → Trigger secure aggregation
    GET  /api/get-result         → Return final decrypted aggregate result
    GET  /api/audit-log          → Fetch all computation event logs
    GET  /api/evaluation-report  → Fetch performance benchmarks

All operations are performed on synthetic data and run fully offline.
"""

import time
import uuid
import json
import os
import glob
from typing import Dict, List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

from smpc.secret_sharing import split_secret, reconstruct_secret, split_record, verify_share
from smpc.aggregation import (
    secure_sum, secure_average, secure_count,
    secure_aggregate_field, compute_frequency_distribution
)
from smpc.garbled_circuit import create_garbled_circuit, evaluate_circuit, compare_threshold
from smpc.homomorphic import he_encrypt, he_add, he_multiply, he_decrypt, HEContext
from smpc.zkp import generate_proof, verify_proof
from data.synthetic_generator import (
    generate_all_parties, generate_party_records,
    get_data_summary, save_party_data, ICD10_CODES
)
from evaluation.benchmarks import run_all_benchmarks, compute_security_metrics
from evaluation.report_generator import generate_html_report, generate_json_report

# Ensure reports directory exists
REPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

# =============================================================================
# App Setup
# =============================================================================

app = FastAPI(
    title="MediVault — Secure Health Data Collaboration",
    description="SMPC system for confidential healthcare data sharing",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# In-Memory State (session-based)
# =============================================================================

sessions: Dict[str, dict] = {}
audit_log: List[dict] = []
cached_benchmark: Optional[dict] = None


def _log_event(session_id: str, event: str, details: dict = None):
    """
    Log an audit event with timestamp.

    Args:
        session_id: The SMPC session identifier.
        event: Description of the event.
        details: Optional additional details.
    """
    entry = {
        "id": str(uuid.uuid4())[:8],
        "session_id": session_id,
        "event": event,
        "details": details or {},
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    audit_log.append(entry)
    return entry


# =============================================================================
# Pydantic Models
# =============================================================================

class InitSessionRequest(BaseModel):
    """Request model for initializing an SMPC session."""
    num_parties: int = Field(default=3, ge=2, le=10, description="Number of participating parties")
    threshold: int = Field(default=2, ge=2, description="Minimum parties for reconstruction")
    records_per_party: int = Field(default=100, ge=10, le=1000, description="Synthetic records per party")

class UploadSharesRequest(BaseModel):
    """Request model for uploading party shares."""
    session_id: str = Field(..., description="Session identifier")
    party_id: str = Field(..., description="Party identifier (party_a, party_b, party_c)")
    field: str = Field(default="age", description="Field to share (age, blood_pressure_systolic, glucose_level)")

class ComputeRequest(BaseModel):
    """Request model for computation parameters."""
    session_id: str
    operation: str = Field(default="average", description="sum, average, or count")
    field: str = Field(default="age", description="Field to aggregate")

class ZKPRequest(BaseModel):
    """Request model for ZKP operations."""
    value: int = Field(..., description="Value to prove a property about")
    proof_type: str = Field(default="threshold", description="range, threshold, or membership")
    threshold: Optional[int] = Field(default=18, description="Threshold for threshold proofs")
    min_val: Optional[int] = Field(default=0, description="Min value for range proofs")
    max_val: Optional[int] = Field(default=200, description="Max value for range proofs")

class GarbledCircuitRequest(BaseModel):
    """Request model for garbled circuit operations."""
    value: int = Field(..., description="Value to compare")
    threshold_value: int = Field(default=140, description="Threshold for comparison")
    bit_width: int = Field(default=8, description="Bit width for comparison")

class SaveReportRequest(BaseModel):
    """Request model for saving a report."""
    report_data: dict = Field(..., description="Benchmark/evaluation data to save")
    report_name: Optional[str] = Field(default=None, description="Optional custom report name")


# =============================================================================
# API Endpoints
# =============================================================================

@app.get("/")
async def root():
    """Health check and API info."""
    return {
        "name": "MediVault — Secure Health Data Collaboration",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": [
            "POST /api/init-session",
            "POST /api/upload-shares",
            "GET  /api/compute-aggregate",
            "GET  /api/get-result",
            "GET  /api/audit-log",
            "GET  /api/evaluation-report",
        ]
    }


@app.post("/api/init-session")
async def init_session(request: InitSessionRequest):
    """
    Initialize an SMPC session with N parties.

    Generates synthetic patient data for each party and prepares
    the session for secure computation.
    """
    session_id = str(uuid.uuid4())[:12]

    # Validate threshold
    if request.threshold > request.num_parties:
        raise HTTPException(400, "Threshold cannot exceed number of parties")

    # Generate synthetic data
    party_data = generate_all_parties(
        parties=request.num_parties,
        records_per_party=request.records_per_party,
        seed=42
    )

    session = {
        "session_id": session_id,
        "num_parties": request.num_parties,
        "threshold": request.threshold,
        "records_per_party": request.records_per_party,
        "party_data": party_data,
        "party_shares": {},
        "results": {},
        "status": "initialized",
        "created_at": datetime.utcnow().isoformat() + "Z",
    }

    sessions[session_id] = session

    _log_event(session_id, "SESSION_INITIALIZED", {
        "num_parties": request.num_parties,
        "threshold": request.threshold,
        "records_per_party": request.records_per_party,
    })

    # Return summary without raw data
    summary = get_data_summary(party_data)

    return {
        "session_id": session_id,
        "status": "initialized",
        "num_parties": request.num_parties,
        "threshold": request.threshold,
        "records_per_party": request.records_per_party,
        "data_summary": summary,
        "message": "SMPC session initialized with synthetic data. Ready for share generation.",
    }


@app.post("/api/upload-shares")
async def upload_shares(request: UploadSharesRequest):
    """
    Generate and upload secret shares for a party's data.

    Splits the specified field from each patient record into
    Shamir shares. The shares are stored in the session.
    """
    session = sessions.get(request.session_id)
    if not session:
        raise HTTPException(404, f"Session {request.session_id} not found")

    party_data = session["party_data"].get(request.party_id)
    if not party_data:
        raise HTTPException(404, f"Party {request.party_id} not found in session")

    n = session["num_parties"]
    k = session["threshold"]
    field = request.field

    # Generate shares for each record's field value
    start_time = time.time()
    all_shares = []

    for record in party_data:
        value = record.get(field)
        if value is not None and isinstance(value, (int, float)):
            int_value = int(value)
            shares = split_secret(int_value, n, k)
            all_shares.append({
                "patient_id": record["patient_id"],
                "field": field,
                "shares": shares,
            })

    elapsed = time.time() - start_time

    # Store in session
    if request.party_id not in session["party_shares"]:
        session["party_shares"][request.party_id] = {}
    session["party_shares"][request.party_id][field] = all_shares

    _log_event(request.session_id, "SHARES_UPLOADED", {
        "party_id": request.party_id,
        "field": field,
        "num_records": len(all_shares),
        "computation_time_ms": round(elapsed * 1000, 2),
    })

    return {
        "session_id": request.session_id,
        "party_id": request.party_id,
        "field": field,
        "num_records_shared": len(all_shares),
        "num_shares_per_record": n,
        "threshold": k,
        "computation_time_ms": round(elapsed * 1000, 2),
        "status": "shares_uploaded",
        "message": f"Generated {n} shares for {len(all_shares)} records",
    }


@app.get("/api/compute-aggregate")
async def compute_aggregate(
    session_id: str,
    operation: str = "average",
    field: str = "age"
):
    """
    Trigger secure aggregation on uploaded shares.

    Performs the specified operation (sum, average, count) on 
    secret-shared data without decrypting individual values.
    """
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(404, f"Session {session_id} not found")

    n = session["num_parties"]
    k = session["threshold"]

    # Check if enough parties have shares
    parties_with_shares = [
        pid for pid, fields in session["party_shares"].items()
        if field in fields
    ]

    if len(parties_with_shares) < k:
        raise HTTPException(400,
            f"Need at least {k} parties with shares for field '{field}'. "
            f"Currently have {len(parties_with_shares)}. "
            f"Use POST /api/upload-shares for each party first."
        )

    # Auto-upload shares if not already done
    if not parties_with_shares:
        for party_id in list(session["party_data"].keys())[:n]:
            await upload_shares(UploadSharesRequest(
                session_id=session_id, party_id=party_id, field=field
            ))
        parties_with_shares = list(session["party_shares"].keys())

    # Collect all shares across parties
    start_time = time.time()
    all_value_shares = []

    # Aggregate across all records from all parties
    num_records = len(session["party_shares"][parties_with_shares[0]][field])
    for record_idx in range(num_records):
        record_shares = []
        for party_id in parties_with_shares:
            party_field_shares = session["party_shares"][party_id][field]
            if record_idx < len(party_field_shares):
                record_shares.append(party_field_shares[record_idx]["shares"])

        if record_shares:
            all_value_shares.append(record_shares[0])  # Each party split their own value

    # Perform aggregation
    if operation == "sum":
        result, meta = secure_sum(all_value_shares, k)
    elif operation == "average":
        result, meta = secure_average(all_value_shares, k)
    elif operation == "count":
        result, meta = secure_count(all_value_shares, k)
    else:
        raise HTTPException(400, f"Unknown operation: {operation}")

    elapsed = time.time() - start_time

    # Store result
    result_key = f"{field}_{operation}"
    session["results"][result_key] = {
        "value": result,
        "operation": operation,
        "field": field,
        "parties_involved": parties_with_shares,
        "computation_time_ms": round(elapsed * 1000, 2),
    }

    _log_event(session_id, "AGGREGATION_COMPUTED", {
        "operation": operation,
        "field": field,
        "result": result,
        "parties": parties_with_shares,
    })

    return {
        "session_id": session_id,
        "operation": operation,
        "field": field,
        "result": result,
        "parties_involved": parties_with_shares,
        "num_values_aggregated": len(all_value_shares),
        "computation_time_ms": round(elapsed * 1000, 2),
        "metadata": meta,
        "privacy": "Individual values never decrypted. Only aggregate result revealed.",
    }


@app.get("/api/get-result")
async def get_result(session_id: str):
    """
    Return all computed aggregate results for a session.
    """
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(404, f"Session {session_id} not found")

    if not session["results"]:
        raise HTTPException(400, "No results computed yet. Use /api/compute-aggregate first.")

    return {
        "session_id": session_id,
        "results": session["results"],
        "num_parties": session["num_parties"],
        "threshold": session["threshold"],
        "status": "results_available",
    }


@app.get("/api/audit-log")
async def get_audit_log(session_id: Optional[str] = None, limit: int = 100):
    """
    Fetch computation event logs.

    Args:
        session_id: Optional filter by session.
        limit: Max events to return.
    """
    if session_id:
        filtered = [e for e in audit_log if e["session_id"] == session_id]
    else:
        filtered = audit_log

    return {
        "total_events": len(filtered),
        "events": filtered[-limit:],
    }


@app.get("/api/evaluation-report")
async def get_evaluation_report(format: str = "json"):
    """
    Run performance benchmarks and return evaluation report.

    Args:
        format: Output format — "json" or "html".
    """
    global cached_benchmark

    _log_event("system", "BENCHMARK_STARTED", {})

    # Use cached results if available and recent (< 5 min)
    if cached_benchmark and time.time() - cached_benchmark.get("_cache_time", 0) < 300:
        results = cached_benchmark
    else:
        results = run_all_benchmarks()
        results["_cache_time"] = time.time()
        cached_benchmark = results

    _log_event("system", "BENCHMARK_COMPLETED", {
        "total_time": results.get("total_benchmark_time_seconds"),
    })

    # Auto-save report to reports/ directory
    try:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        report_filename = f"evaluation_report_{timestamp}.json"
        report_path = os.path.join(REPORTS_DIR, report_filename)
        save_data = {k: v for k, v in results.items() if k != "_cache_time"}
        with open(report_path, "w") as f:
            json.dump(save_data, f, indent=2, default=str)
        _log_event("system", "REPORT_SAVED", {"filename": report_filename})
    except Exception as e:
        _log_event("system", "REPORT_SAVE_ERROR", {"error": str(e)})

    if format == "html":
        html_path = os.path.join(REPORTS_DIR, f"evaluation_report_{timestamp}.html")
        generate_html_report(results, html_path)
        with open(html_path, "r") as f:
            return HTMLResponse(f.read())

    return results


# =============================================================================
# Additional Utility Endpoints
# =============================================================================

@app.post("/api/zkp/generate")
async def api_generate_proof(request: ZKPRequest):
    """Generate a zero-knowledge proof."""
    kwargs = {}
    if request.proof_type == "range":
        kwargs = {"min_val": request.min_val, "max_val": request.max_val}
    elif request.proof_type == "threshold":
        kwargs = {"threshold": request.threshold}
    elif request.proof_type == "membership":
        kwargs = {"valid_set": list(range(10, 200))}

    try:
        proof, meta = generate_proof(request.value, request.proof_type, **kwargs)
    except ValueError as e:
        raise HTTPException(400, str(e))

    # Convert large ints to strings for JSON serialization
    serializable_proof = {
        k: str(v) if isinstance(v, int) and v > 2**53 else v
        for k, v in proof.items()
    }

    _log_event("system", "ZKP_GENERATED", {
        "proof_type": request.proof_type,
        "proof_id": proof["proof_id"],
    })

    return {
        "proof": serializable_proof,
        "metadata": meta,
    }


@app.post("/api/zkp/verify")
async def api_verify_proof(proof: dict):
    """Verify a zero-knowledge proof."""
    # Convert string ints back
    for key in ["commitment", "commitment_low", "commitment_high", "t", "t_low", "t_high",
                "challenge", "response", "response_low", "response_high"]:
        if key in proof and isinstance(proof[key], str):
            try:
                proof[key] = int(proof[key])
            except ValueError:
                pass

    result = verify_proof(proof)

    _log_event("system", "ZKP_VERIFIED", {
        "proof_type": proof.get("proof_type"),
        "is_valid": result["is_valid"],
    })

    return result


@app.post("/api/garbled-circuit")
async def api_garbled_circuit(request: GarbledCircuitRequest):
    """Run a garbled circuit comparison."""
    try:
        result = compare_threshold(request.value, request.threshold_value, request.bit_width)
    except ValueError as e:
        raise HTTPException(400, str(e))

    _log_event("system", "GARBLED_CIRCUIT_EVALUATED", {
        "exceeds_threshold": result["exceeds_threshold"],
    })

    return result


@app.get("/api/session/{session_id}")
async def get_session_info(session_id: str):
    """Get full session information."""
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(404, f"Session {session_id} not found")

    return {
        "session_id": session_id,
        "status": session["status"],
        "num_parties": session["num_parties"],
        "threshold": session["threshold"],
        "records_per_party": session["records_per_party"],
        "parties_with_shares": list(session["party_shares"].keys()),
        "results_available": list(session["results"].keys()),
        "created_at": session["created_at"],
    }


@app.get("/api/sessions")
async def list_sessions():
    """List all active sessions."""
    return {
        "sessions": [
            {
                "session_id": sid,
                "num_parties": s["num_parties"],
                "status": s["status"],
                "created_at": s["created_at"],
            }
            for sid, s in sessions.items()
        ]
    }


@app.get("/api/security-metrics")
async def get_security_metrics():
    """Get security evaluation metrics."""
    metrics = compute_security_metrics()
    return metrics


# =============================================================================
# Report Storage Endpoints
# =============================================================================

@app.post("/api/save-report")
async def save_report(request: SaveReportRequest):
    """
    Save an evaluation report to the reports/ directory.

    Args:
        request: Contains the report data and optional custom name.
    """
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    if request.report_name:
        # Sanitize the name
        safe_name = "".join(c for c in request.report_name if c.isalnum() or c in "_-").strip()
        report_filename = f"{safe_name}_{timestamp}.json"
    else:
        report_filename = f"evaluation_report_{timestamp}.json"

    report_path = os.path.join(REPORTS_DIR, report_filename)

    try:
        with open(report_path, "w") as f:
            json.dump(request.report_data, f, indent=2, default=str)

        _log_event("system", "REPORT_SAVED", {
            "filename": report_filename,
            "size_bytes": os.path.getsize(report_path),
        })

        return {
            "status": "saved",
            "filename": report_filename,
            "path": report_path,
            "size_bytes": os.path.getsize(report_path),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to save report: {str(e)}")


@app.get("/api/reports")
async def list_reports():
    """
    List all saved evaluation reports from the reports/ directory.
    """
    reports = []
    for filepath in sorted(glob.glob(os.path.join(REPORTS_DIR, "*.json")), reverse=True):
        filename = os.path.basename(filepath)
        stat = os.stat(filepath)
        reports.append({
            "filename": filename,
            "size_bytes": stat.st_size,
            "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat() + "Z",
            "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat() + "Z",
        })

    return {
        "total_reports": len(reports),
        "reports_directory": REPORTS_DIR,
        "reports": reports,
    }


@app.get("/api/reports/{filename}")
async def get_report(filename: str):
    """
    Download a specific saved report by filename.
    """
    # Sanitize to prevent directory traversal
    safe_filename = os.path.basename(filename)
    report_path = os.path.join(REPORTS_DIR, safe_filename)

    if not os.path.exists(report_path):
        raise HTTPException(404, f"Report '{safe_filename}' not found")

    try:
        with open(report_path, "r") as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise HTTPException(500, f"Failed to read report: {str(e)}")


@app.get("/api/data-summary/{session_id}")
async def get_data_summary_endpoint(session_id: str):
    """Get data summary for a session."""
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(404, f"Session {session_id} not found")

    summary = get_data_summary(session["party_data"])
    return summary


# =============================================================================
# SMPC Protocol Simulation Endpoint
# =============================================================================

@app.post("/api/simulate-protocol")
async def simulate_protocol(
    num_parties: int = 3,
    records_per_party: int = 20,
    field: str = "age"
):
    """
    Simulate the full SMPC protocol end-to-end.

    Steps:
        1. Generate local shares for each party
        2. Exchange shares over simulated secure channel
        3. Compute aggregation on shares
        4. Reconstruct and display final result

    Returns step-by-step logs with timing benchmarks.
    """
    protocol_log = []
    overall_start = time.time()
    k = max(2, num_parties // 2 + 1)

    # Step 1: Generate data and local shares
    step_start = time.time()
    party_data = generate_all_parties(
        parties=num_parties,
        records_per_party=records_per_party,
        seed=42
    )

    all_shares = {}
    for party_id, records in party_data.items():
        party_shares = []
        for record in records:
            value = int(record.get(field, 0))
            shares = split_secret(value, num_parties, k)
            party_shares.append(shares)
        all_shares[party_id] = party_shares

    protocol_log.append({
        "step": 1,
        "name": "Generate Local Shares",
        "description": f"Each party splits their {field} data into {num_parties} shares",
        "time_ms": round((time.time() - step_start) * 1000, 2),
        "status": "complete",
    })

    # Step 2: Simulate secure share exchange
    step_start = time.time()
    exchanged_shares = {}
    for party_id, party_shares in all_shares.items():
        for i, shares in enumerate(party_shares):
            for share_idx, share in enumerate(shares):
                target_party = list(party_data.keys())[share_idx] if share_idx < num_parties else party_id
                if target_party not in exchanged_shares:
                    exchanged_shares[target_party] = []
                exchanged_shares[target_party].append({
                    "from": party_id,
                    "record_idx": i,
                    "share": share,
                })

    protocol_log.append({
        "step": 2,
        "name": "Secure Share Exchange (TLS Mock)",
        "description": "Shares exchanged between parties over simulated encrypted channels",
        "time_ms": round((time.time() - step_start) * 1000, 2),
        "shares_exchanged": sum(len(v) for v in exchanged_shares.values()),
        "status": "complete",
    })

    # Step 3: Aggregation on shares
    step_start = time.time()

    # Collect all value shares (one share set per original value)
    flat_shares = []
    for party_id, party_shares in all_shares.items():
        for shares in party_shares:
            flat_shares.append(shares)

    sum_result, sum_meta = secure_sum(flat_shares, k)
    avg_result, avg_meta = secure_average(flat_shares, k)

    protocol_log.append({
        "step": 3,
        "name": "Secure Aggregation",
        "description": f"Computing sum and average of {field} across all parties without decryption",
        "time_ms": round((time.time() - step_start) * 1000, 2),
        "status": "complete",
    })

    # Step 4: Result reconstruction
    step_start = time.time()

    # Compute ground truth for verification
    ground_truth_values = []
    for records in party_data.values():
        for record in records:
            val = record.get(field)
            if val is not None:
                ground_truth_values.append(int(val))

    true_sum = sum(ground_truth_values)
    true_avg = round(true_sum / len(ground_truth_values), 2) if ground_truth_values else 0

    protocol_log.append({
        "step": 4,
        "name": "Result Reconstruction",
        "description": "Final aggregate result reconstructed and verified",
        "time_ms": round((time.time() - step_start) * 1000, 2),
        "status": "complete",
    })

    total_time = time.time() - overall_start

    _log_event("protocol_sim", "PROTOCOL_SIMULATED", {
        "num_parties": num_parties,
        "field": field,
        "total_time_ms": round(total_time * 1000, 2),
    })

    return {
        "protocol": "Secure Multi-Party Computation",
        "num_parties": num_parties,
        "threshold": k,
        "field": field,
        "records_per_party": records_per_party,
        "total_records": len(ground_truth_values),
        "steps": protocol_log,
        "results": {
            "secure_sum": sum_result,
            "secure_average": avg_result,
            "ground_truth_sum": true_sum,
            "ground_truth_average": true_avg,
            "sum_match": sum_result == true_sum,
            "avg_match": abs(avg_result - true_avg) < 1.0,
        },
        "total_time_ms": round(total_time * 1000, 2),
        "privacy_guarantee": "Individual patient records were NEVER revealed during computation",
    }


# =============================================================================
# Run with: uvicorn main:app --reload --port 8000
# =============================================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
