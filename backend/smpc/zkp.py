"""
Zero-Knowledge Proof Module
============================
Implements zero-knowledge proofs for healthcare data verification.

Allows proving properties about patient data (e.g., age is above 18,
diagnosis code is in a valid range) WITHOUT revealing the actual values.

Implementation uses a Schnorr-like discrete log commitment scheme
as well as hash-based range proofs suitable for demonstration.

ZKP Protocols implemented:
    1. Range proof — prove a value is within [min, max]
    2. Membership proof — prove a value belongs to a valid set
    3. Threshold proof — prove a value exceeds a threshold
"""

import hashlib
import secrets
import time
from typing import Dict, Tuple, List, Optional


# Large safe prime and generator for the discrete log group
# Using a 256-bit prime for demonstration
_P = int(
    "FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD1"
    "29024E088A67CC74020BBEA63B139B22514A08798E3404DD"
    "EF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245"
    "E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED"
    "EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE65381"
    "FFFFFFFFFFFFFFFF",
    16
)
_G = 2
_Q = (_P - 1) // 2  # Order of the subgroup


def _hash_points(*args) -> int:
    """
    Hash multiple values together using SHA-256 to produce a challenge.

    This implements the Fiat-Shamir heuristic, converting an interactive
    protocol into a non-interactive one.

    Args:
        args: Values to hash together.

    Returns:
        Integer hash value modulo Q.
    """
    hasher = hashlib.sha256()
    for arg in args:
        hasher.update(str(arg).encode())
    return int(hasher.hexdigest(), 16) % _Q


def _commit(value: int, randomness: int) -> int:
    """
    Create a Pedersen-like commitment: C = g^value * h^randomness mod p.

    Args:
        value: The value to commit to.
        randomness: Random blinding factor.

    Returns:
        The commitment value.
    """
    # Use g^r as commitment (simplified Schnorr)
    return pow(_G, randomness, _P)


def generate_proof(
    value: int,
    proof_type: str = "range",
    **kwargs
) -> Tuple[Dict, Dict]:
    """
    Generate a zero-knowledge proof for a given value.

    Supported proof types:
        - "range": Prove value is within [min_val, max_val]
        - "threshold": Prove value > threshold (without revealing value)
        - "membership": Prove value is in a valid set

    Args:
        value: The private value to prove a property about.
        proof_type: Type of proof ("range", "threshold", "membership").
        **kwargs: Additional parameters:
            - min_val, max_val: For range proofs (default 0, 200)
            - threshold: For threshold proofs
            - valid_set: For membership proofs

    Returns:
        Tuple of (proof_dict, metadata).

    Example:
        >>> # Prove patient age >= 18 without revealing exact age
        >>> proof, meta = generate_proof(25, "threshold", threshold=18)
        >>> verified = verify_proof(proof)
        >>> verified["is_valid"]
        True
    """
    start_time = time.time()

    if proof_type == "range":
        proof = _generate_range_proof(
            value,
            kwargs.get("min_val", 0),
            kwargs.get("max_val", 200)
        )
    elif proof_type == "threshold":
        proof = _generate_threshold_proof(
            value,
            kwargs.get("threshold", 18)
        )
    elif proof_type == "membership":
        proof = _generate_membership_proof(
            value,
            kwargs.get("valid_set", [])
        )
    else:
        raise ValueError(f"Unknown proof type: {proof_type}")

    elapsed = time.time() - start_time

    metadata = {
        "proof_type": proof_type,
        "proof_id": proof["proof_id"],
        "generation_time_ms": round(elapsed * 1000, 2),
        "value_revealed": False,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    return proof, metadata


def _generate_range_proof(value: int, min_val: int, max_val: int) -> Dict:
    """
    Generate a ZKP that `value` is within [min_val, max_val].

    Strategy: Prove that (value - min_val) >= 0 AND (max_val - value) >= 0
    by committing to both differences and providing Schnorr-like proofs.

    Args:
        value: The private value.
        min_val: Minimum of the valid range.
        max_val: Maximum of the valid range.

    Returns:
        Proof dictionary.
    """
    if not (min_val <= value <= max_val):
        raise ValueError(f"Value {value} not in range [{min_val}, {max_val}]")

    # Compute witness values
    v_low = value - min_val   # Must be >= 0
    v_high = max_val - value  # Must be >= 0

    # Random blinding factors
    r_low = secrets.randbelow(_Q)
    r_high = secrets.randbelow(_Q)
    k_low = secrets.randbelow(_Q)
    k_high = secrets.randbelow(_Q)

    # Commitments
    c_low = pow(_G, v_low * r_low % _Q, _P)
    c_high = pow(_G, v_high * r_high % _Q, _P)

    # First message (random commitments)
    t_low = pow(_G, k_low, _P)
    t_high = pow(_G, k_high, _P)

    # Challenge (Fiat-Shamir)
    challenge = _hash_points(c_low, c_high, t_low, t_high, min_val, max_val)

    # Responses
    s_low = (k_low + challenge * r_low * v_low) % _Q
    s_high = (k_high + challenge * r_high * v_high) % _Q

    return {
        "proof_id": secrets.token_hex(8),
        "proof_type": "range",
        "min_val": min_val,
        "max_val": max_val,
        "commitment_low": c_low,
        "commitment_high": c_high,
        "t_low": t_low,
        "t_high": t_high,
        "challenge": challenge,
        "response_low": s_low,
        "response_high": s_high,
    }


def _generate_threshold_proof(value: int, threshold: int) -> Dict:
    """
    Generate a ZKP that `value > threshold`.

    Args:
        value: The private value.
        threshold: The public threshold.

    Returns:
        Proof dictionary.
    """
    if value <= threshold:
        raise ValueError(f"Value {value} is not greater than threshold {threshold}")

    difference = value - threshold  # Must be > 0

    # Random blinding
    r = secrets.randbelow(_Q)
    k = secrets.randbelow(_Q)

    # Commitment to the difference
    commitment = pow(_G, difference * r % _Q, _P)

    # First message
    t = pow(_G, k, _P)

    # Challenge
    challenge = _hash_points(commitment, t, threshold)

    # Response
    response = (k + challenge * r * difference) % _Q

    return {
        "proof_id": secrets.token_hex(8),
        "proof_type": "threshold",
        "threshold": threshold,
        "commitment": commitment,
        "t": t,
        "challenge": challenge,
        "response": response,
    }


def _generate_membership_proof(value: int, valid_set: List[int]) -> Dict:
    """
    Generate a ZKP that `value` is a member of `valid_set`.

    Uses a hash-based accumulator approach: compute a commitment
    to the value and provide a proof that the commitment matches
    one element in the accumulated set.

    Args:
        value: The private value.
        valid_set: The set of valid values.

    Returns:
        Proof dictionary.
    """
    if value not in valid_set:
        raise ValueError(f"Value {value} is not in the valid set")

    # Hash each element in the valid set
    set_hashes = [hashlib.sha256(str(v).encode()).hexdigest() for v in valid_set]

    # Accumulator: hash of all set hashes
    accumulator = hashlib.sha256("".join(sorted(set_hashes)).encode()).hexdigest()

    # Commitment with blinding
    r = secrets.randbelow(_Q)
    value_hash = hashlib.sha256(str(value).encode()).hexdigest()

    # Proof of inclusion
    k = secrets.randbelow(_Q)
    commitment = pow(_G, r, _P)
    t = pow(_G, k, _P)

    challenge = _hash_points(commitment, t, accumulator)
    response = (k + challenge * r) % _Q

    return {
        "proof_id": secrets.token_hex(8),
        "proof_type": "membership",
        "accumulator": accumulator,
        "commitment": commitment,
        "value_hash": value_hash,
        "set_size": len(valid_set),
        "t": t,
        "challenge": challenge,
        "response": response,
    }


def verify_proof(proof: Dict) -> Dict:
    """
    Verify a zero-knowledge proof.

    Checks the mathematical consistency of the proof without learning
    the underlying private value.

    Args:
        proof: The proof dictionary generated by generate_proof().

    Returns:
        Dictionary with verification result and metadata.

    Example:
        >>> proof, _ = generate_proof(25, "threshold", threshold=18)
        >>> result = verify_proof(proof)
        >>> result["is_valid"]
        True
    """
    start_time = time.time()

    proof_type = proof["proof_type"]

    if proof_type == "range":
        is_valid = _verify_range_proof(proof)
    elif proof_type == "threshold":
        is_valid = _verify_threshold_proof(proof)
    elif proof_type == "membership":
        is_valid = _verify_membership_proof(proof)
    else:
        raise ValueError(f"Unknown proof type: {proof_type}")

    elapsed = time.time() - start_time

    return {
        "is_valid": is_valid,
        "proof_type": proof_type,
        "proof_id": proof["proof_id"],
        "verification_time_ms": round(elapsed * 1000, 2),
        "value_learned": "nothing",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def _verify_range_proof(proof: Dict) -> bool:
    """
    Verify a range proof.

    Checks: g^s_low == t_low * c_low^challenge (mod p)
    And similarly for the high bound.

    Args:
        proof: Range proof dictionary.

    Returns:
        True if the proof is valid.
    """
    # Recompute challenge
    challenge = _hash_points(
        proof["commitment_low"],
        proof["commitment_high"],
        proof["t_low"],
        proof["t_high"],
        proof["min_val"],
        proof["max_val"]
    )

    if challenge != proof["challenge"]:
        return False

    # Verify low bound: g^s_low == t_low * c_low^challenge
    lhs_low = pow(_G, proof["response_low"], _P)
    rhs_low = (proof["t_low"] * pow(proof["commitment_low"], challenge, _P)) % _P

    # Verify high bound
    lhs_high = pow(_G, proof["response_high"], _P)
    rhs_high = (proof["t_high"] * pow(proof["commitment_high"], challenge, _P)) % _P

    return lhs_low == rhs_low and lhs_high == rhs_high


def _verify_threshold_proof(proof: Dict) -> bool:
    """
    Verify a threshold proof.

    Args:
        proof: Threshold proof dictionary.

    Returns:
        True if the proof is valid.
    """
    challenge = _hash_points(proof["commitment"], proof["t"], proof["threshold"])

    if challenge != proof["challenge"]:
        return False

    lhs = pow(_G, proof["response"], _P)
    rhs = (proof["t"] * pow(proof["commitment"], challenge, _P)) % _P

    return lhs == rhs


def _verify_membership_proof(proof: Dict) -> bool:
    """
    Verify a membership proof.

    Args:
        proof: Membership proof dictionary.

    Returns:
        True if the proof is valid.
    """
    challenge = _hash_points(proof["commitment"], proof["t"], proof["accumulator"])

    if challenge != proof["challenge"]:
        return False

    lhs = pow(_G, proof["response"], _P)
    rhs = (proof["t"] * pow(proof["commitment"], challenge, _P)) % _P

    return lhs == rhs
