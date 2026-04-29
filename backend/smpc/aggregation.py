"""
Secure Aggregation Module
=========================
Computes sum, average, and count on secret-shared data WITHOUT
decrypting individual values.

The key insight: addition is homomorphic over Shamir shares.
If we add shares from different secrets point-wise, the resulting
shares encode the sum of the original secrets. This allows us to
compute aggregate statistics without any party learning individual values.

Supported operations:
    - secure_sum: Sum of values across parties
    - secure_average: Average of values across parties
    - secure_count: Count of records matching a predicate (on shares)
"""

import time
from typing import List, Tuple, Dict, Optional, Callable
from smpc.secret_sharing import PRIME, reconstruct_secret, split_secret


def _add_shares(shares_list: List[List[Tuple[int, int]]]) -> List[Tuple[int, int]]:
    """
    Add multiple sets of shares point-wise to produce shares of the sum.

    Because Shamir's secret sharing is additively homomorphic,
    adding the y-values of shares with the same x-index yields
    valid shares of the sum of the original secrets.

    Args:
        shares_list: List of share sets, where each share set is
                     a list of (x, y) tuples.

    Returns:
        A new set of shares encoding the sum of all original secrets.

    Raises:
        ValueError: If share sets have different lengths.
    """
    if not shares_list:
        raise ValueError("No shares provided for aggregation")

    n = len(shares_list[0])
    for shares in shares_list:
        if len(shares) != n:
            raise ValueError("All share sets must have the same length")

    result = []
    for i in range(n):
        x = shares_list[0][i][0]
        y_sum = sum(shares[i][1] for shares in shares_list) % PRIME
        result.append((x, y_sum))

    return result


def secure_sum(
    all_party_shares: List[List[Tuple[int, int]]],
    k: int
) -> Tuple[int, Dict]:
    """
    Compute the sum of secret-shared values across all parties
    without decrypting individual values.

    Each party holds shares of their private value. This function:
    1. Adds shares point-wise (homomorphic addition)
    2. Reconstructs only the final sum

    No individual value is ever revealed.

    Args:
        all_party_shares: List where each element is a list of shares
                          for one party's secret value.
        k: Threshold for reconstruction.

    Returns:
        Tuple of (sum_result, metadata) where metadata includes
        timing and party count information.

    Example:
        >>> # Party A has value 100, Party B has value 200
        >>> shares_a = split_secret(100, n=3, k=2)
        >>> shares_b = split_secret(200, n=3, k=2)
        >>> result, meta = secure_sum([shares_a, shares_b], k=2)
        >>> result == 300
        True
    """
    start_time = time.time()

    # Step 1: Add shares homomorphically
    sum_shares = _add_shares(all_party_shares)

    # Step 2: Reconstruct the sum using k shares
    result = reconstruct_secret(sum_shares[:k])

    elapsed = time.time() - start_time

    metadata = {
        "operation": "secure_sum",
        "num_parties": len(all_party_shares),
        "num_shares": len(sum_shares),
        "threshold": k,
        "computation_time_ms": round(elapsed * 1000, 2),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    return result, metadata


def secure_average(
    all_party_shares: List[List[Tuple[int, int]]],
    k: int,
    count: Optional[int] = None,
    precision: int = 2
) -> Tuple[float, Dict]:
    """
    Compute the average of secret-shared values without decryption.

    Uses secure_sum internally, then divides by the count of values.
    Division happens only on the final reconstructed sum — never on
    individual shares.

    Args:
        all_party_shares: List of share sets for each party's value.
        k: Threshold for reconstruction.
        count: Number of values (defaults to number of parties).
        precision: Decimal places for the result.

    Returns:
        Tuple of (average_result, metadata).

    Example:
        >>> shares_a = split_secret(100, n=3, k=2)
        >>> shares_b = split_secret(200, n=3, k=2)
        >>> shares_c = split_secret(300, n=3, k=2)
        >>> avg, meta = secure_average([shares_a, shares_b, shares_c], k=2)
        >>> avg == 200.0
        True
    """
    start_time = time.time()

    total, sum_meta = secure_sum(all_party_shares, k)
    n = count if count is not None else len(all_party_shares)

    if n == 0:
        raise ValueError("Cannot compute average of zero values")

    average = round(total / n, precision)
    elapsed = time.time() - start_time

    metadata = {
        "operation": "secure_average",
        "num_parties": len(all_party_shares),
        "count": n,
        "threshold": k,
        "computation_time_ms": round(elapsed * 1000, 2),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    return average, metadata


def secure_count(
    all_party_shares: List[List[Tuple[int, int]]],
    k: int,
    predicate_shares: Optional[List[List[Tuple[int, int]]]] = None
) -> Tuple[int, Dict]:
    """
    Count records matching a predicate using secure computation.

    Each party can locally evaluate a predicate on their data AND
    encode the result (0 or 1) as a secret share. The sum of these
    shares gives the total count without revealing which records matched.

    If predicate_shares is None, counts total records (sum of 1s).

    Args:
        all_party_shares: Original share sets (used for party count).
        k: Threshold for reconstruction.
        predicate_shares: Optional shares encoding predicate results
                          (each party contributes shares of 0 or 1).

    Returns:
        Tuple of (count_result, metadata).

    Example:
        >>> # 2 out of 3 parties have patients matching a condition
        >>> match_a = split_secret(1, n=3, k=2)  # matches
        >>> match_b = split_secret(0, n=3, k=2)  # doesn't match
        >>> match_c = split_secret(1, n=3, k=2)  # matches
        >>> count, meta = secure_count([], k=2,
        ...     predicate_shares=[match_a, match_b, match_c])
        >>> count == 2
        True
    """
    start_time = time.time()

    if predicate_shares is not None:
        count_result, _ = secure_sum(predicate_shares, k)
    else:
        # Count total parties contributing
        count_result = len(all_party_shares)

    elapsed = time.time() - start_time

    metadata = {
        "operation": "secure_count",
        "num_parties": len(all_party_shares) if all_party_shares else len(predicate_shares or []),
        "threshold": k,
        "computation_time_ms": round(elapsed * 1000, 2),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    return count_result, metadata


def secure_aggregate_field(
    party_records: List[List[dict]],
    field: str,
    n: int,
    k: int,
    operation: str = "sum"
) -> Tuple[float, Dict]:
    """
    Aggregate a specific field across all party records securely.

    This is a convenience function that:
    1. Extracts the specified field from each record
    2. Creates shares for each value
    3. Performs the requested aggregation
    4. Returns the result without revealing individual values

    Args:
        party_records: List of record lists, one per party.
        field: The field name to aggregate (e.g., "age", "blood_pressure").
        n: Number of shares per value.
        k: Threshold for reconstruction.
        operation: One of "sum", "average", "count".

    Returns:
        Tuple of (result, metadata).

    Example:
        >>> records_a = [{"age": 30}, {"age": 40}]
        >>> records_b = [{"age": 50}, {"age": 60}]
        >>> result, meta = secure_aggregate_field(
        ...     [records_a, records_b], "age", n=3, k=2, operation="average")
    """
    all_shares = []

    for party in party_records:
        for record in party:
            if field in record and isinstance(record[field], (int, float)):
                value = int(record[field])
                shares = split_secret(value, n, k)
                all_shares.append(shares)

    if not all_shares:
        raise ValueError(f"No numeric values found for field '{field}'")

    if operation == "sum":
        return secure_sum(all_shares, k)
    elif operation == "average":
        return secure_average(all_shares, k)
    elif operation == "count":
        return secure_count(all_shares, k)
    else:
        raise ValueError(f"Unknown operation: {operation}")


def compute_frequency_distribution(
    party_records: List[List[dict]],
    field: str,
    categories: List[str],
    n: int,
    k: int
) -> Tuple[Dict[str, int], Dict]:
    """
    Compute frequency distribution of a categorical field securely.

    For each category, parties encode whether their records match (1 or 0),
    then we use secure_sum to count matches without revealing which
    records belong to which category.

    Args:
        party_records: List of record lists, one per party.
        field: The categorical field (e.g., "diagnosis_code").
        categories: List of category values to count.
        n: Number of shares per value.
        k: Threshold for reconstruction.

    Returns:
        Tuple of (distribution_dict, metadata).
    """
    start_time = time.time()
    distribution = {}

    for category in categories:
        indicator_shares = []
        for party in party_records:
            for record in party:
                match = 1 if record.get(field) == category else 0
                shares = split_secret(match, n, k)
                indicator_shares.append(shares)

        if indicator_shares:
            count, _ = secure_sum(indicator_shares, k)
            distribution[category] = count

    elapsed = time.time() - start_time

    metadata = {
        "operation": "frequency_distribution",
        "field": field,
        "num_categories": len(categories),
        "computation_time_ms": round(elapsed * 1000, 2),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    return distribution, metadata
