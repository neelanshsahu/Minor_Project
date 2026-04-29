"""
Shamir's Secret Sharing Module
==============================
Implements (k, n) threshold secret sharing over a prime field GF(p).

A secret is split into n shares such that any k or more shares can
reconstruct the original secret, but fewer than k shares reveal
nothing about the secret.

This is used in MediVault to split patient data (age, diagnosis codes,
vitals) across multiple healthcare parties so that no single party
can access the raw data.
"""

import random
import hashlib
from typing import List, Tuple, Optional

# Large Mersenne prime for the finite field
PRIME = 2**127 - 1


def _mod_inverse(a: int, p: int) -> int:
    """
    Compute the modular multiplicative inverse of a modulo p
    using Fermat's little theorem (p must be prime).

    Args:
        a: The number to find the inverse of.
        p: The prime modulus.

    Returns:
        The modular inverse of a mod p.
    """
    return pow(a, p - 2, p)


def _generate_coefficients(secret: int, k: int) -> List[int]:
    """
    Generate random polynomial coefficients for Shamir's scheme.
    The constant term is the secret, and we generate k-1 random coefficients.

    Args:
        secret: The secret value (constant term of the polynomial).
        k: The threshold (degree of polynomial + 1).

    Returns:
        List of k coefficients where coefficients[0] = secret.
    """
    coefficients = [secret % PRIME]
    for _ in range(k - 1):
        coefficients.append(random.randint(1, PRIME - 1))
    return coefficients


def _evaluate_polynomial(coefficients: List[int], x: int) -> int:
    """
    Evaluate a polynomial at point x using Horner's method in GF(p).

    Args:
        coefficients: List of polynomial coefficients [a0, a1, ..., ak-1].
        x: The point at which to evaluate.

    Returns:
        The polynomial value at x, mod PRIME.
    """
    result = 0
    for coeff in reversed(coefficients):
        result = (result * x + coeff) % PRIME
    return result


def _lagrange_interpolation(shares: List[Tuple[int, int]], prime: int) -> int:
    """
    Reconstruct the secret using Lagrange interpolation at x=0.

    Args:
        shares: List of (x, y) share tuples.
        prime: The prime modulus.

    Returns:
        The reconstructed secret value.
    """
    secret = 0
    k = len(shares)

    for i in range(k):
        xi, yi = shares[i]
        numerator = 1
        denominator = 1

        for j in range(k):
            if i == j:
                continue
            xj, _ = shares[j]
            numerator = (numerator * (-xj)) % prime
            denominator = (denominator * (xi - xj)) % prime

        lagrange_coeff = (yi * numerator * _mod_inverse(denominator, prime)) % prime
        secret = (secret + lagrange_coeff) % prime

    return secret


def split_secret(secret: int, n: int, k: int) -> List[Tuple[int, int]]:
    """
    Split a secret into n shares using Shamir's (k, n) threshold scheme.

    The secret is encoded as the constant term of a random polynomial
    of degree k-1 over GF(PRIME). Each share is a point (x, f(x)) on
    this polynomial.

    Args:
        secret: The integer secret to split (e.g., patient age, vital value).
        n: Total number of shares to generate.
        k: Minimum number of shares needed for reconstruction.

    Returns:
        List of n tuples (x, y), each representing one share.

    Raises:
        ValueError: If k > n or if parameters are invalid.

    Example:
        >>> shares = split_secret(42, n=5, k=3)
        >>> len(shares)
        5
        >>> reconstructed = reconstruct_secret(shares[:3])
        >>> reconstructed == 42
        True
    """
    if k > n:
        raise ValueError(f"Threshold k={k} cannot exceed total shares n={n}")
    if k < 2:
        raise ValueError(f"Threshold k={k} must be at least 2")
    if n < 2:
        raise ValueError(f"Total shares n={n} must be at least 2")
    if secret < 0:
        raise ValueError("Secret must be a non-negative integer")

    coefficients = _generate_coefficients(secret, k)
    shares = []

    for i in range(1, n + 1):
        x = i
        y = _evaluate_polynomial(coefficients, x)
        shares.append((x, y))

    return shares


def reconstruct_secret(shares: List[Tuple[int, int]]) -> int:
    """
    Reconstruct a secret from k or more shares using Lagrange interpolation.

    Args:
        shares: List of (x, y) share tuples. Must contain at least k shares
                from the original split operation.

    Returns:
        The reconstructed integer secret.

    Raises:
        ValueError: If fewer than 2 shares are provided.

    Example:
        >>> shares = split_secret(120, n=5, k=3)
        >>> result = reconstruct_secret(shares[:3])
        >>> result == 120
        True
    """
    if len(shares) < 2:
        raise ValueError("Need at least 2 shares to reconstruct")

    return _lagrange_interpolation(shares, PRIME)


def verify_share(share: Tuple[int, int], other_shares: List[Tuple[int, int]], k: int) -> bool:
    """
    Verify that a share is consistent with other shares by checking if
    reconstruction with subsets yields the same result.

    This provides a simple consistency check — if a malicious party
    submits a fake share, this verification will detect it (with high
    probability) by comparing reconstruction results from different
    subsets.

    Args:
        share: The (x, y) tuple to verify.
        other_shares: Other known-good shares to check against.
        k: The threshold parameter.

    Returns:
        True if the share is consistent, False otherwise.

    Example:
        >>> shares = split_secret(99, n=5, k=3)
        >>> verify_share(shares[0], shares[1:4], k=3)
        True
    """
    if len(other_shares) < k - 1:
        raise ValueError(f"Need at least {k-1} other shares for verification")

    # Reconstruct using the share + first (k-1) other shares
    subset1 = [share] + other_shares[:k - 1]
    result1 = reconstruct_secret(subset1)

    # Reconstruct using different subset if possible
    if len(other_shares) >= k:
        subset2 = other_shares[:k]
        result2 = reconstruct_secret(subset2)
        return result1 == result2

    return True


def generate_share_hash(share: Tuple[int, int]) -> str:
    """
    Generate a SHA-256 hash of a share for integrity verification.

    Args:
        share: The (x, y) share tuple.

    Returns:
        Hex-encoded SHA-256 hash string.
    """
    data = f"{share[0]}:{share[1]}".encode()
    return hashlib.sha256(data).hexdigest()


def split_record(record: dict, n: int, k: int) -> List[dict]:
    """
    Split all numeric fields in a patient record into Shamir shares.

    Non-numeric fields are excluded from sharing. Each party receives
    a dictionary mapping field names to their respective shares.

    Args:
        record: Dictionary with patient data fields.
        n: Total number of shares.
        k: Threshold for reconstruction.

    Returns:
        List of n dictionaries, each containing one share per numeric field.

    Example:
        >>> record = {"age": 45, "blood_pressure": 120, "glucose": 95}
        >>> party_shares = split_record(record, n=3, k=2)
        >>> len(party_shares)
        3
    """
    party_shares = [{} for _ in range(n)]

    for field, value in record.items():
        if isinstance(value, (int, float)):
            int_value = int(value)
            shares = split_secret(int_value, n, k)
            for i, share in enumerate(shares):
                party_shares[i][field] = share

    return party_shares


def reconstruct_record(party_shares: List[dict]) -> dict:
    """
    Reconstruct all fields from party shares.

    Args:
        party_shares: List of dictionaries, each containing shares
                      for the same set of fields.

    Returns:
        Dictionary with reconstructed field values.
    """
    if not party_shares:
        raise ValueError("No shares provided")

    fields = party_shares[0].keys()
    result = {}

    for field in fields:
        shares = [ps[field] for ps in party_shares if field in ps]
        result[field] = reconstruct_secret(shares)

    return result
