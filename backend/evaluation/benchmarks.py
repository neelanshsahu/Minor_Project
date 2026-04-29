"""
Performance Benchmarking Module
================================
Benchmarks SMPC operations to evaluate:
    1. Computation time vs number of parties
    2. Communication overhead vs data size
    3. Security metrics — entropy of shares, reconstruction accuracy
    4. Homomorphic encryption performance
    5. Garbled circuit evaluation time
"""

import time
import math
import random
import statistics
from typing import List, Dict, Tuple, Optional

from smpc.secret_sharing import split_secret, reconstruct_secret, PRIME
from smpc.aggregation import secure_sum, secure_average
from smpc.garbled_circuit import create_garbled_circuit, evaluate_circuit, compare_threshold
from smpc.homomorphic import he_encrypt, he_add, he_decrypt, HEContext
from smpc.zkp import generate_proof, verify_proof


def benchmark_secret_sharing(
    max_parties: int = 10,
    threshold_ratio: float = 0.6,
    num_trials: int = 5
) -> Dict:
    """
    Benchmark secret sharing: split and reconstruct times vs party count.

    Args:
        max_parties: Maximum number of parties to test.
        threshold_ratio: Ratio of threshold to total parties.
        num_trials: Number of trials per configuration.

    Returns:
        Dictionary with timing data per party count.
    """
    results = {"operation": "secret_sharing", "data": []}
    secret = random.randint(1, 10000)

    for n in range(3, max_parties + 1):
        k = max(2, int(n * threshold_ratio))
        split_times = []
        reconstruct_times = []

        for _ in range(num_trials):
            # Benchmark split
            start = time.perf_counter()
            shares = split_secret(secret, n, k)
            split_times.append(time.perf_counter() - start)

            # Benchmark reconstruct
            start = time.perf_counter()
            result = reconstruct_secret(shares[:k])
            reconstruct_times.append(time.perf_counter() - start)

            assert result == secret, "Reconstruction failed!"

        results["data"].append({
            "num_parties": n,
            "threshold": k,
            "avg_split_time_ms": round(statistics.mean(split_times) * 1000, 3),
            "avg_reconstruct_time_ms": round(statistics.mean(reconstruct_times) * 1000, 3),
            "std_split_time_ms": round(statistics.stdev(split_times) * 1000, 3) if len(split_times) > 1 else 0,
            "std_reconstruct_time_ms": round(statistics.stdev(reconstruct_times) * 1000, 3) if len(reconstruct_times) > 1 else 0,
        })

    return results


def benchmark_secure_aggregation(
    party_counts: Optional[List[int]] = None,
    values_per_party: int = 10,
    num_trials: int = 5
) -> Dict:
    """
    Benchmark secure aggregation (sum, average) vs number of parties.

    Args:
        party_counts: List of party counts to test.
        values_per_party: Number of values each party contributes.
        num_trials: Number of trials per configuration.

    Returns:
        Dictionary with aggregation timing data.
    """
    if party_counts is None:
        party_counts = [3, 5, 7, 10]

    results = {"operation": "secure_aggregation", "data": []}

    for num_parties in party_counts:
        k = max(2, num_parties // 2 + 1)
        sum_times = []
        avg_times = []

        for _ in range(num_trials):
            # Generate shares for random values
            all_shares = []
            for _ in range(num_parties * values_per_party):
                value = random.randint(1, 1000)
                shares = split_secret(value, num_parties, k)
                all_shares.append(shares)

            # Benchmark sum
            start = time.perf_counter()
            secure_sum(all_shares, k)
            sum_times.append(time.perf_counter() - start)

            # Benchmark average
            start = time.perf_counter()
            secure_average(all_shares, k)
            avg_times.append(time.perf_counter() - start)

        results["data"].append({
            "num_parties": num_parties,
            "total_values": num_parties * values_per_party,
            "threshold": k,
            "avg_sum_time_ms": round(statistics.mean(sum_times) * 1000, 3),
            "avg_average_time_ms": round(statistics.mean(avg_times) * 1000, 3),
        })

    return results


def benchmark_garbled_circuits(
    bit_widths: Optional[List[int]] = None,
    num_trials: int = 5
) -> Dict:
    """
    Benchmark garbled circuit operations.

    Args:
        bit_widths: Bit widths to test for threshold comparison.
        num_trials: Number of trials per configuration.

    Returns:
        Dictionary with garbled circuit timing data.
    """
    if bit_widths is None:
        bit_widths = [4, 8, 12, 16]

    results = {"operation": "garbled_circuits", "data": []}

    for bw in bit_widths:
        create_times = []
        eval_times = []
        compare_times = []

        for _ in range(num_trials):
            # Single gate benchmark
            start = time.perf_counter()
            circuit = create_garbled_circuit("GT")
            create_times.append(time.perf_counter() - start)

            start = time.perf_counter()
            evaluate_circuit(circuit, 1, 0)
            eval_times.append(time.perf_counter() - start)

            # Multi-bit comparison
            value = random.randint(0, 2**bw - 1)
            threshold = random.randint(0, 2**bw - 1)
            if value <= threshold:
                value, threshold = threshold + 1, threshold
            value = min(value, 2**bw - 1)

            if value > threshold:
                start = time.perf_counter()
                compare_threshold(value, threshold, bw)
                compare_times.append(time.perf_counter() - start)

        results["data"].append({
            "bit_width": bw,
            "avg_create_time_ms": round(statistics.mean(create_times) * 1000, 3),
            "avg_eval_time_ms": round(statistics.mean(eval_times) * 1000, 3),
            "avg_compare_time_ms": round(statistics.mean(compare_times) * 1000, 3) if compare_times else 0,
            "num_gates_for_compare": bw,
        })

    return results


def benchmark_homomorphic_encryption(
    vector_sizes: Optional[List[int]] = None,
    num_trials: int = 3
) -> Dict:
    """
    Benchmark homomorphic encryption operations.

    Args:
        vector_sizes: Sizes of vectors to encrypt/compute on.
        num_trials: Number of trials per configuration.

    Returns:
        Dictionary with HE timing data.
    """
    if vector_sizes is None:
        vector_sizes = [10, 50, 100]

    results = {"operation": "homomorphic_encryption", "data": []}
    ctx = HEContext(use_tenseal=True)

    for size in vector_sizes:
        encrypt_times = []
        add_times = []
        decrypt_times = []

        for _ in range(num_trials):
            values_a = [random.uniform(50, 200) for _ in range(size)]
            values_b = [random.uniform(50, 200) for _ in range(size)]

            # Encrypt
            start = time.perf_counter()
            ct_a, _ = he_encrypt(values_a, ctx)
            encrypt_times.append(time.perf_counter() - start)

            ct_b, _ = he_encrypt(values_b, ctx)

            # Add
            start = time.perf_counter()
            ct_sum, _ = he_add(ct_a, ct_b, ctx)
            add_times.append(time.perf_counter() - start)

            # Decrypt
            start = time.perf_counter()
            he_decrypt(ct_sum, ctx)
            decrypt_times.append(time.perf_counter() - start)

        results["data"].append({
            "vector_size": size,
            "using_tenseal": ctx.is_real_he,
            "avg_encrypt_time_ms": round(statistics.mean(encrypt_times) * 1000, 3),
            "avg_add_time_ms": round(statistics.mean(add_times) * 1000, 3),
            "avg_decrypt_time_ms": round(statistics.mean(decrypt_times) * 1000, 3),
        })

    return results


def benchmark_zkp(num_trials: int = 10) -> Dict:
    """
    Benchmark zero-knowledge proof generation and verification.

    Args:
        num_trials: Number of trials.

    Returns:
        Dictionary with ZKP timing data.
    """
    results = {"operation": "zero_knowledge_proofs", "data": []}

    proof_types = [
        {"type": "range", "kwargs": {"min_val": 0, "max_val": 200}},
        {"type": "threshold", "kwargs": {"threshold": 18}},
        {"type": "membership", "kwargs": {"valid_set": list(range(10, 100))}},
    ]

    for pt in proof_types:
        gen_times = []
        verify_times = []

        for _ in range(num_trials):
            if pt["type"] == "range":
                value = random.randint(1, 199)
            elif pt["type"] == "threshold":
                value = random.randint(19, 100)
            else:
                value = random.choice(pt["kwargs"]["valid_set"])

            start = time.perf_counter()
            proof, _ = generate_proof(value, pt["type"], **pt["kwargs"])
            gen_times.append(time.perf_counter() - start)

            start = time.perf_counter()
            verify_proof(proof)
            verify_times.append(time.perf_counter() - start)

        results["data"].append({
            "proof_type": pt["type"],
            "avg_generation_time_ms": round(statistics.mean(gen_times) * 1000, 3),
            "avg_verification_time_ms": round(statistics.mean(verify_times) * 1000, 3),
        })

    return results


def compute_share_entropy(shares: List[Tuple[int, int]]) -> float:
    """
    Compute the Shannon entropy of share values to verify randomness.

    High entropy = good security (shares appear random).

    Args:
        shares: List of (x, y) share tuples.

    Returns:
        Estimated entropy value.
    """
    # Use byte-level entropy of share values
    all_bytes = b""
    for _, y in shares:
        byte_len = (y.bit_length() + 7) // 8
        all_bytes += y.to_bytes(max(byte_len, 1), "big")

    if not all_bytes:
        return 0.0

    byte_counts = [0] * 256
    for b in all_bytes:
        byte_counts[b] += 1

    total = len(all_bytes)
    entropy = 0.0
    for count in byte_counts:
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)

    return round(entropy, 4)


def compute_security_metrics(
    secret: int = 42,
    n: int = 5,
    k: int = 3,
    num_trials: int = 10
) -> Dict:
    """
    Compute security metrics for the SMPC system.

    Args:
        secret: Test secret value.
        n: Number of shares.
        k: Threshold.
        num_trials: Number of trials for accuracy.

    Returns:
        Dictionary with security evaluation metrics.
    """
    entropies = []
    reconstruction_errors = []

    for _ in range(num_trials):
        shares = split_secret(secret, n, k)
        entropy = compute_share_entropy(shares)
        entropies.append(entropy)

        # Test reconstruction accuracy
        result = reconstruct_secret(shares[:k])
        reconstruction_errors.append(abs(result - secret))

    return {
        "avg_share_entropy": round(statistics.mean(entropies), 4),
        "min_share_entropy": round(min(entropies), 4),
        "max_share_entropy": round(max(entropies), 4),
        "reconstruction_accuracy": 1.0 if all(e == 0 for e in reconstruction_errors) else 0.0,
        "max_reconstruction_error": max(reconstruction_errors),
        "information_theoretic_security": True,
        "threshold_security": f"Any {k-1} or fewer shares reveal NO information about the secret",
    }


def run_all_benchmarks() -> Dict:
    """
    Run all benchmarks and return combined results.

    Returns:
        Dictionary containing all benchmark results.
    """
    start_time = time.time()

    results = {
        "benchmarks": {
            "secret_sharing": benchmark_secret_sharing(),
            "secure_aggregation": benchmark_secure_aggregation(),
            "garbled_circuits": benchmark_garbled_circuits(),
            "homomorphic_encryption": benchmark_homomorphic_encryption(),
            "zero_knowledge_proofs": benchmark_zkp(),
        },
        "security_metrics": compute_security_metrics(),
        "total_benchmark_time_seconds": 0,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    results["total_benchmark_time_seconds"] = round(time.time() - start_time, 2)
    return results
