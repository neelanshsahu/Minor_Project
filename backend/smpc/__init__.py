"""
MediVault SMPC Modules
======================
Secure Multi-Party Computation modules for confidential healthcare data sharing.

Modules:
    - secret_sharing: Shamir's Secret Sharing over a prime field
    - aggregation: Secure aggregation (sum, average, count) on encrypted shares
    - garbled_circuit: Simplified garbled circuit simulation for comparisons
    - homomorphic: Homomorphic encryption using CKKS scheme (tenseal)
    - zkp: Zero-Knowledge Proof generation and verification
"""

from smpc.secret_sharing import split_secret, reconstruct_secret, verify_share
from smpc.aggregation import secure_sum, secure_average, secure_count
from smpc.garbled_circuit import create_garbled_circuit, evaluate_circuit
from smpc.homomorphic import he_encrypt, he_add, he_multiply, he_decrypt
from smpc.zkp import generate_proof, verify_proof
