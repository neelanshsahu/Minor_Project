"""
Homomorphic Encryption Module
==============================
Provides homomorphic encryption operations for secure computation
on encrypted healthcare data.

Supports two backends:
    1. TenSEAL (CKKS scheme) — if installed, provides real HE operations
    2. Simulated HE — fallback that demonstrates the API without requiring
       TenSEAL installation

The CKKS scheme supports approximate arithmetic on encrypted floating-point
numbers, making it suitable for healthcare computations like average
blood pressure, glucose levels, etc.
"""

import time
import json
import hashlib
import secrets
from typing import List, Tuple, Dict, Optional, Union

# Try to import tenseal; fall back to simulation if unavailable
_TENSEAL_AVAILABLE = False
try:
    import tenseal as ts
    _TENSEAL_AVAILABLE = True
except ImportError:
    pass


class SimulatedCiphertext:
    """
    Simulated ciphertext for when TenSEAL is not available.

    Wraps plaintext values with encryption metadata to simulate
    the HE workflow. In a real system, these would be actual
    encrypted values that cannot be read without the secret key.

    This is clearly labeled as SIMULATED and should not be used
    for actual security — it's for demonstration purposes only.
    """

    def __init__(self, values: List[float], context_id: str):
        """
        Initialize a simulated ciphertext.

        Args:
            values: The plaintext values (stored for simulation).
            context_id: Identifier linking to the encryption context.
        """
        self._values = values
        self._context_id = context_id
        self._noise_budget = 100  # Simulated noise budget
        self._operations_count = 0
        self._id = secrets.token_hex(8)

    def __add__(self, other: 'SimulatedCiphertext') -> 'SimulatedCiphertext':
        """Simulate homomorphic addition."""
        result = SimulatedCiphertext(
            [a + b for a, b in zip(self._values, other._values)],
            self._context_id
        )
        result._noise_budget = min(self._noise_budget, other._noise_budget) - 1
        result._operations_count = self._operations_count + other._operations_count + 1
        return result

    def __mul__(self, other: 'SimulatedCiphertext') -> 'SimulatedCiphertext':
        """Simulate homomorphic multiplication."""
        result = SimulatedCiphertext(
            [a * b for a, b in zip(self._values, other._values)],
            self._context_id
        )
        result._noise_budget = min(self._noise_budget, other._noise_budget) - 10
        result._operations_count = self._operations_count + other._operations_count + 1
        return result

    def decrypt(self) -> List[float]:
        """Simulate decryption (returns stored values)."""
        return self._values

    @property
    def metadata(self) -> Dict:
        """Return metadata about the ciphertext."""
        return {
            "ciphertext_id": self._id,
            "context_id": self._context_id,
            "noise_budget_remaining": self._noise_budget,
            "operations_performed": self._operations_count,
            "simulated": True,
        }


class HEContext:
    """
    Homomorphic Encryption context manager.

    Manages keys (public, secret, relinearization, galois) and provides
    a unified API for encryption/decryption regardless of backend.
    """

    def __init__(self, poly_modulus_degree: int = 8192, use_tenseal: bool = True):
        """
        Initialize the HE context.

        Args:
            poly_modulus_degree: Ring dimension (higher = more secure but slower).
            use_tenseal: Whether to use TenSEAL if available.
        """
        self._context_id = secrets.token_hex(8)
        self._using_tenseal = _TENSEAL_AVAILABLE and use_tenseal
        self._context = None
        self._creation_time = time.time()

        if self._using_tenseal:
            self._context = ts.context(
                ts.SCHEME_TYPE.CKKS,
                poly_modulus_degree=poly_modulus_degree,
                coeff_mod_bit_sizes=[60, 40, 40, 60]
            )
            self._context.global_scale = 2**40
            self._context.generate_galois_keys()
            self._context.generate_relin_keys()

    @property
    def is_real_he(self) -> bool:
        """Whether this context uses real HE (TenSEAL) or simulation."""
        return self._using_tenseal

    @property
    def context_id(self) -> str:
        """Unique identifier for this context."""
        return self._context_id

    def encrypt(self, values: List[float]) -> Union['SimulatedCiphertext', object]:
        """
        Encrypt a list of floating-point values.

        Args:
            values: List of float values to encrypt.

        Returns:
            Encrypted ciphertext (TenSEAL CKKSVector or SimulatedCiphertext).
        """
        if self._using_tenseal:
            return ts.ckks_vector(self._context, values)
        else:
            return SimulatedCiphertext(values, self._context_id)

    def decrypt(self, ciphertext) -> List[float]:
        """
        Decrypt a ciphertext back to plaintext values.

        Args:
            ciphertext: The encrypted data to decrypt.

        Returns:
            List of decrypted float values.
        """
        if self._using_tenseal:
            return ciphertext.decrypt()
        else:
            return ciphertext.decrypt()


# Global default context
_default_context: Optional[HEContext] = None


def _get_context() -> HEContext:
    """Get or create the global HE context."""
    global _default_context
    if _default_context is None:
        _default_context = HEContext()
    return _default_context


def he_encrypt(values: Union[List[float], float], context: Optional[HEContext] = None) -> Tuple[object, Dict]:
    """
    Encrypt numerical patient data using homomorphic encryption.

    The encrypted values can be used in subsequent he_add() and
    he_multiply() operations without decryption.

    Args:
        values: A float or list of floats to encrypt (e.g., blood pressure readings).
        context: Optional HE context. Uses global default if not provided.

    Returns:
        Tuple of (ciphertext, metadata).

    Example:
        >>> ct, meta = he_encrypt([120.5, 130.0, 145.2])
        >>> meta["num_values"]
        3
    """
    start_time = time.time()
    ctx = context or _get_context()

    if isinstance(values, (int, float)):
        values = [float(values)]
    else:
        values = [float(v) for v in values]

    ciphertext = ctx.encrypt(values)
    elapsed = time.time() - start_time

    metadata = {
        "operation": "encrypt",
        "num_values": len(values),
        "context_id": ctx.context_id,
        "using_tenseal": ctx.is_real_he,
        "computation_time_ms": round(elapsed * 1000, 2),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    return ciphertext, metadata


def he_add(ct_a: object, ct_b: object, context: Optional[HEContext] = None) -> Tuple[object, Dict]:
    """
    Add two ciphertexts homomorphically (without decryption).

    The result is a new ciphertext encoding the element-wise sum
    of the two input plaintexts.

    Args:
        ct_a: First ciphertext.
        ct_b: Second ciphertext.
        context: Optional HE context.

    Returns:
        Tuple of (result_ciphertext, metadata).

    Example:
        >>> ct1, _ = he_encrypt([10.0, 20.0])
        >>> ct2, _ = he_encrypt([30.0, 40.0])
        >>> ct_sum, meta = he_add(ct1, ct2)
        >>> result = he_decrypt(ct_sum)
        >>> # result ≈ [40.0, 60.0]
    """
    start_time = time.time()
    ctx = context or _get_context()

    result = ct_a + ct_b
    elapsed = time.time() - start_time

    metadata = {
        "operation": "homomorphic_add",
        "using_tenseal": ctx.is_real_he,
        "computation_time_ms": round(elapsed * 1000, 2),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    return result, metadata


def he_multiply(ct_a: object, ct_b: object, context: Optional[HEContext] = None) -> Tuple[object, Dict]:
    """
    Multiply two ciphertexts homomorphically (without decryption).

    The result is a new ciphertext encoding the element-wise product.
    Note: multiplication is more expensive than addition in HE and
    consumes more noise budget.

    Args:
        ct_a: First ciphertext.
        ct_b: Second ciphertext.
        context: Optional HE context.

    Returns:
        Tuple of (result_ciphertext, metadata).

    Example:
        >>> ct1, _ = he_encrypt([5.0, 3.0])
        >>> ct2, _ = he_encrypt([2.0, 4.0])
        >>> ct_prod, meta = he_multiply(ct1, ct2)
        >>> result = he_decrypt(ct_prod)
        >>> # result ≈ [10.0, 12.0]
    """
    start_time = time.time()
    ctx = context or _get_context()

    result = ct_a * ct_b
    elapsed = time.time() - start_time

    metadata = {
        "operation": "homomorphic_multiply",
        "using_tenseal": ctx.is_real_he,
        "computation_time_ms": round(elapsed * 1000, 2),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    return result, metadata


def he_decrypt(ciphertext: object, context: Optional[HEContext] = None) -> Tuple[List[float], Dict]:
    """
    Decrypt a ciphertext to reveal the final computation result.

    This should only be called on the FINAL result — never on
    intermediate values, to preserve privacy.

    Args:
        ciphertext: The ciphertext to decrypt.
        context: Optional HE context.

    Returns:
        Tuple of (decrypted_values, metadata).

    Example:
        >>> ct, _ = he_encrypt([42.0])
        >>> values, meta = he_decrypt(ct)
        >>> abs(values[0] - 42.0) < 0.01
        True
    """
    start_time = time.time()
    ctx = context or _get_context()

    values = ctx.decrypt(ciphertext)
    elapsed = time.time() - start_time

    # Round to reasonable precision (CKKS is approximate)
    values = [round(v, 4) for v in values]

    metadata = {
        "operation": "decrypt",
        "num_values": len(values),
        "using_tenseal": ctx.is_real_he,
        "computation_time_ms": round(elapsed * 1000, 2),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    return values, metadata


def he_compute_average(
    value_lists: List[List[float]],
    context: Optional[HEContext] = None
) -> Tuple[List[float], Dict]:
    """
    Compute the average of multiple encrypted value lists.

    Each list is encrypted, all ciphertexts are summed, and the result
    is decrypted and divided by the count. Only the final average is
    revealed — individual value lists remain private.

    Args:
        value_lists: List of float lists from different parties.
        context: Optional HE context.

    Returns:
        Tuple of (average_values, metadata).

    Example:
        >>> values_a = [120.0, 130.0]  # Hospital A blood pressures
        >>> values_b = [140.0, 110.0]  # Hospital B blood pressures
        >>> avg, meta = he_compute_average([values_a, values_b])
        >>> # avg ≈ [130.0, 120.0]
    """
    start_time = time.time()
    ctx = context or _get_context()

    # Encrypt all lists
    ciphertexts = []
    for vl in value_lists:
        ct, _ = he_encrypt(vl, ctx)
        ciphertexts.append(ct)

    # Sum all ciphertexts
    total_ct = ciphertexts[0]
    for ct in ciphertexts[1:]:
        total_ct, _ = he_add(total_ct, ct, ctx)

    # Decrypt sum and compute average
    total_values, _ = he_decrypt(total_ct, ctx)
    n = len(value_lists)
    averages = [round(v / n, 4) for v in total_values]

    elapsed = time.time() - start_time

    metadata = {
        "operation": "he_compute_average",
        "num_parties": n,
        "using_tenseal": ctx.is_real_he,
        "computation_time_ms": round(elapsed * 1000, 2),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    return averages, metadata
