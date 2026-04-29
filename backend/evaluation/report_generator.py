"""
Report Generator Module
========================
Generates HTML evaluation reports from benchmark results.
Includes interactive charts and formatted tables.
"""

import json
import time
from typing import Dict


def generate_html_report(benchmark_results: Dict, output_path: str = "evaluation_report.html") -> str:
    """
    Generate a comprehensive HTML evaluation report.

    Args:
        benchmark_results: Results from run_all_benchmarks().
        output_path: File path to save the report.

    Returns:
        Path to generated HTML report.
    """
    html = _build_html(benchmark_results)

    with open(output_path, "w") as f:
        f.write(html)

    return output_path


def _make_row(cells):
    """Build a single HTML table row from a list of cell values."""
    tds = "".join("<td>{}</td>".format(c) for c in cells)
    return "<tr>{}</tr>".format(tds)


def _make_badge_row(cells):
    """Build a row where the first cell is wrapped in a badge span."""
    badge = '<span class="badge">{}</span>'.format(cells[0])
    rest = "".join("<td>{}</td>".format(c) for c in cells[1:])
    return "<tr><td>{}</td>{}</tr>".format(badge, rest)


def _build_html(results: Dict) -> str:
    """Build the full HTML report string."""

    benchmarks = results.get("benchmarks", {})
    security = results.get("security_metrics", {})

    # Extract data for tables
    ss_data = benchmarks.get("secret_sharing", {}).get("data", [])
    agg_data = benchmarks.get("secure_aggregation", {}).get("data", [])
    gc_data = benchmarks.get("garbled_circuits", {}).get("data", [])
    he_data = benchmarks.get("homomorphic_encryption", {}).get("data", [])
    zkp_data = benchmarks.get("zero_knowledge_proofs", {}).get("data", [])

    # Build table rows using helper functions (Python 3.9 compatible)
    ss_rows = "".join(_make_row([
        d["num_parties"], d["threshold"],
        d["avg_split_time_ms"], d["avg_reconstruct_time_ms"]
    ]) for d in ss_data)

    agg_rows = "".join(_make_row([
        d["num_parties"], d["total_values"],
        d["avg_sum_time_ms"], d["avg_average_time_ms"]
    ]) for d in agg_data)

    gc_rows = "".join(_make_row([
        d["bit_width"], d["avg_create_time_ms"],
        d["avg_eval_time_ms"], d["avg_compare_time_ms"]
    ]) for d in gc_data)

    he_rows = "".join(_make_row([
        d["vector_size"],
        "TenSEAL" if d.get("using_tenseal") else "Simulated",
        d["avg_encrypt_time_ms"], d["avg_add_time_ms"], d["avg_decrypt_time_ms"]
    ]) for d in he_data)

    zkp_rows = "".join(_make_badge_row([
        d["proof_type"], d["avg_generation_time_ms"], d["avg_verification_time_ms"]
    ]) for d in zkp_data)

    # Security values
    entropy = security.get("avg_share_entropy", "N/A")
    accuracy = security.get("reconstruction_accuracy", "N/A")
    info_sec = "✅ Yes" if security.get("information_theoretic_security") else "❌ No"
    threshold_sec = security.get("threshold_security", "")
    timestamp = results.get("timestamp", "N/A")
    total_time = results.get("total_benchmark_time_seconds", "N/A")

    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MediVault — SMPC Evaluation Report</title>
    <style>
        :root {
            --ocean-deep: #0D3B4F;
            --teal: #1A7A8A;
            --seafoam: #A8DADC;
            --pearl: #F1FAEE;
            --green: #52B788;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', 'Segoe UI', sans-serif;
            background: var(--ocean-deep);
            color: var(--pearl);
            padding: 2rem; line-height: 1.6;
        }
        h1 { font-size: 2.5rem; color: var(--seafoam); margin-bottom: 0.5rem; }
        h2 { color: var(--teal); font-size: 1.5rem; margin: 2rem 0 1rem;
             border-bottom: 2px solid var(--teal); padding-bottom: 0.5rem; }
        .subtitle { color: var(--seafoam); opacity: 0.7; margin-bottom: 2rem; }
        .card { background: rgba(26,122,138,0.15); border: 1px solid rgba(168,218,220,0.2);
                border-radius: 16px; padding: 1.5rem; margin-bottom: 1.5rem; }
        table { width: 100%%; border-collapse: collapse; margin: 1rem 0; }
        th, td { padding: 0.75rem 1rem; text-align: left;
                 border-bottom: 1px solid rgba(168,218,220,0.15); }
        th { color: var(--seafoam); font-weight: 600; font-size: 0.85rem;
             text-transform: uppercase; }
        td { font-size: 0.9rem; }
        .metric { display: inline-block; background: rgba(82,183,136,0.2);
                  border: 1px solid rgba(82,183,136,0.3); border-radius: 8px;
                  padding: 0.5rem 1rem; margin: 0.25rem; }
        .metric-label { font-size: 0.75rem; color: var(--seafoam); text-transform: uppercase; }
        .metric-value { font-size: 1.2rem; font-weight: 700; color: var(--green); }
        .badge { display: inline-block; background: var(--green); color: var(--ocean-deep);
                 padding: 0.2rem 0.6rem; border-radius: 12px; font-size: 0.75rem; font-weight: 600; }
        .timestamp { text-align: center; color: rgba(241,250,238,0.4); margin-top: 2rem; font-size: 0.85rem; }
    </style>
</head>
<body>
    <h1>🔒 MediVault — SMPC Evaluation Report</h1>
    <p class="subtitle">Secure Multi-Party Computation Performance & Security Analysis</p>

    <h2>📊 Security Metrics</h2>
    <div class="card">
        <div class="metric"><div class="metric-label">Avg Share Entropy</div><div class="metric-value">%s bits</div></div>
        <div class="metric"><div class="metric-label">Reconstruction Accuracy</div><div class="metric-value">%s</div></div>
        <div class="metric"><div class="metric-label">Info-Theoretic Security</div><div class="metric-value">%s</div></div>
        <p style="margin-top: 1rem; opacity: 0.8;">%s</p>
    </div>

    <h2>🔑 Secret Sharing Performance</h2>
    <div class="card"><table>
        <thead><tr><th>Parties</th><th>Threshold</th><th>Avg Split (ms)</th><th>Avg Reconstruct (ms)</th></tr></thead>
        <tbody>%s</tbody>
    </table></div>

    <h2>📈 Secure Aggregation Performance</h2>
    <div class="card"><table>
        <thead><tr><th>Parties</th><th>Total Values</th><th>Avg Sum (ms)</th><th>Avg Average (ms)</th></tr></thead>
        <tbody>%s</tbody>
    </table></div>

    <h2>🔐 Garbled Circuits Performance</h2>
    <div class="card"><table>
        <thead><tr><th>Bit Width</th><th>Avg Create (ms)</th><th>Avg Evaluate (ms)</th><th>Avg Compare (ms)</th></tr></thead>
        <tbody>%s</tbody>
    </table></div>

    <h2>🔢 Homomorphic Encryption Performance</h2>
    <div class="card"><table>
        <thead><tr><th>Vector Size</th><th>Backend</th><th>Avg Encrypt (ms)</th><th>Avg Add (ms)</th><th>Avg Decrypt (ms)</th></tr></thead>
        <tbody>%s</tbody>
    </table></div>

    <h2>🛡️ Zero-Knowledge Proofs Performance</h2>
    <div class="card"><table>
        <thead><tr><th>Proof Type</th><th>Avg Generation (ms)</th><th>Avg Verification (ms)</th></tr></thead>
        <tbody>%s</tbody>
    </table></div>

    <div class="timestamp">Report generated at %s | Total benchmark time: %ss</div>
</body>
</html>""" % (entropy, accuracy, info_sec, threshold_sec,
              ss_rows, agg_rows, gc_rows, he_rows, zkp_rows,
              timestamp, total_time)

    return html


def generate_json_report(benchmark_results: Dict, output_path: str = "evaluation_report.json") -> str:
    """
    Save benchmark results as a JSON report.

    Args:
        benchmark_results: Results from run_all_benchmarks().
        output_path: File path to save the report.

    Returns:
        Path to generated JSON report.
    """
    with open(output_path, "w") as f:
        json.dump(benchmark_results, f, indent=2)
    return output_path
