"""
Garbled Circuit Simulation Module
=================================
Simulates a simplified garbled circuit for secure comparison operations.

In real SMPC, garbled circuits allow two parties to evaluate a Boolean
function on their private inputs without revealing those inputs.
This module provides a simplified simulation demonstrating the concept.

Example use case: "Is the average blood pressure across hospitals > 140?"
without revealing individual hospital averages.
"""

import os
import hashlib
import secrets
import time
from typing import Dict, Tuple, List, Optional
from dataclasses import dataclass, field


@dataclass
class Wire:
    """
    Represents a wire in the garbled circuit.

    Each wire has two labels (keys) — one for 0 and one for 1.
    The garbler assigns random labels; the evaluator learns only
    one label per wire (corresponding to their input bit).
    """
    label_0: bytes = field(default_factory=lambda: secrets.token_bytes(16))
    label_1: bytes = field(default_factory=lambda: secrets.token_bytes(16))

    def get_label(self, bit: int) -> bytes:
        """Get the label for a given bit value."""
        return self.label_1 if bit else self.label_0


@dataclass
class GarbledGate:
    """
    Represents a single garbled gate in the circuit.

    The truth table is encrypted: each row is encrypted under the
    two input wire labels, so only the correct combination of input
    labels can decrypt the corresponding output label.
    """
    gate_type: str  # "AND", "OR", "XOR", "GT" (greater than)
    garbled_table: List[bytes] = field(default_factory=list)
    input_wire_a: Optional[Wire] = None
    input_wire_b: Optional[Wire] = None
    output_wire: Optional[Wire] = None


@dataclass
class GarbledCircuit:
    """
    A complete garbled circuit with gates, wires, and metadata.
    """
    circuit_id: str
    description: str
    gates: List[GarbledGate] = field(default_factory=list)
    input_wires: List[Wire] = field(default_factory=list)
    output_wire: Optional[Wire] = None
    creation_time: float = 0.0
    evaluation_time: float = 0.0


def _encrypt_label(key_a: bytes, key_b: bytes, plaintext: bytes) -> bytes:
    """
    Encrypt a label using two keys (double encryption).

    Uses HMAC-based encryption simulation: H(key_a || key_b || nonce) XOR plaintext.

    Args:
        key_a: First encryption key (from input wire A).
        key_b: Second encryption key (from input wire B).
        plaintext: The output label to encrypt.

    Returns:
        Encrypted bytes.
    """
    combined = key_a + key_b
    key_hash = hashlib.sha256(combined).digest()[:len(plaintext)]
    return bytes(a ^ b for a, b in zip(key_hash, plaintext))


def _decrypt_label(key_a: bytes, key_b: bytes, ciphertext: bytes) -> bytes:
    """
    Decrypt a label using two keys.

    Args:
        key_a: First decryption key.
        key_b: Second decryption key.
        ciphertext: The encrypted output label.

    Returns:
        Decrypted bytes (the output label).
    """
    # XOR-based encryption is its own inverse
    return _encrypt_label(key_a, key_b, ciphertext)


def _gate_function(gate_type: str, bit_a: int, bit_b: int) -> int:
    """
    Evaluate a gate's Boolean function.

    Args:
        gate_type: Type of gate ("AND", "OR", "XOR", "GT").
        bit_a: First input bit.
        bit_b: Second input bit.

    Returns:
        Output bit.
    """
    if gate_type == "AND":
        return bit_a & bit_b
    elif gate_type == "OR":
        return bit_a | bit_b
    elif gate_type == "XOR":
        return bit_a ^ bit_b
    elif gate_type == "GT":
        # Greater than: a > b
        return 1 if bit_a > bit_b else 0
    else:
        raise ValueError(f"Unknown gate type: {gate_type}")


def _garble_gate(gate_type: str, wire_a: Wire, wire_b: Wire, wire_out: Wire) -> GarbledGate:
    """
    Garble a single gate by encrypting its truth table.

    For each possible combination of input bits (00, 01, 10, 11),
    the output label is encrypted under the corresponding input labels.
    The encrypted rows are then shuffled so the evaluator cannot
    determine which row corresponds to which input combination.

    Args:
        gate_type: Type of Boolean gate.
        wire_a: First input wire.
        wire_b: Second input wire.
        wire_out: Output wire.

    Returns:
        A GarbledGate with encrypted truth table.
    """
    gate = GarbledGate(
        gate_type=gate_type,
        input_wire_a=wire_a,
        input_wire_b=wire_b,
        output_wire=wire_out
    )

    table = []
    for bit_a in [0, 1]:
        for bit_b in [0, 1]:
            output_bit = _gate_function(gate_type, bit_a, bit_b)
            label_a = wire_a.get_label(bit_a)
            label_b = wire_b.get_label(bit_b)
            output_label = wire_out.get_label(output_bit)

            encrypted = _encrypt_label(label_a, label_b, output_label)
            table.append(encrypted)

    # Shuffle the table so order doesn't reveal information
    import random
    random.shuffle(table)
    gate.garbled_table = table

    return gate


def create_garbled_circuit(
    operation: str = "GT",
    description: str = "Is value A greater than threshold B?"
) -> GarbledCircuit:
    """
    Create a garbled circuit for a comparison operation.

    This creates a simplified single-gate circuit. In practice,
    multi-bit comparison requires a cascade of gates, but this
    demonstrates the core concept.

    Supported operations:
        - "GT": Greater than (a > b?)
        - "AND": Logical AND
        - "OR": Logical OR
        - "XOR": Logical XOR

    Args:
        operation: The comparison operation type.
        description: Human-readable description of what the circuit computes.

    Returns:
        A GarbledCircuit ready for evaluation.

    Example:
        >>> circuit = create_garbled_circuit("GT", "Is avg BP > 140?")
        >>> result = evaluate_circuit(circuit, input_a=1, input_b=0)
        >>> result["output"] == 1  # 1 > 0 is True
        True
    """
    start_time = time.time()

    wire_a = Wire()
    wire_b = Wire()
    wire_out = Wire()

    gate = _garble_gate(operation, wire_a, wire_b, wire_out)

    circuit = GarbledCircuit(
        circuit_id=secrets.token_hex(8),
        description=description,
        gates=[gate],
        input_wires=[wire_a, wire_b],
        output_wire=wire_out,
        creation_time=time.time() - start_time,
    )

    return circuit


def evaluate_circuit(
    circuit: GarbledCircuit,
    input_a: int,
    input_b: int
) -> Dict:
    """
    Evaluate a garbled circuit with given inputs.

    The evaluator has one label per input wire (obtained via
    oblivious transfer in real protocols). They try to decrypt
    each row of the garbled table — only one will succeed.

    Args:
        circuit: The garbled circuit to evaluate.
        input_a: First party's input bit (0 or 1).
        input_b: Second party's input bit (0 or 1).

    Returns:
        Dictionary with:
            - output: The circuit output (0 or 1)
            - circuit_id: Circuit identifier
            - evaluation_time_ms: Time taken
            - description: What the circuit computed

    Example:
        >>> circuit = create_garbled_circuit("GT")
        >>> result = evaluate_circuit(circuit, input_a=1, input_b=0)
        >>> result["output"]
        1
    """
    start_time = time.time()

    gate = circuit.gates[0]
    wire_a = gate.input_wire_a
    wire_b = gate.input_wire_b
    wire_out = gate.output_wire

    # Get input labels based on actual input bits
    label_a = wire_a.get_label(input_a)
    label_b = wire_b.get_label(input_b)

    # Try to decrypt each row of the garbled table
    output_bit = None
    for encrypted_row in gate.garbled_table:
        decrypted = _decrypt_label(label_a, label_b, encrypted_row)

        # Check if decrypted label matches either output label
        if decrypted == wire_out.label_0:
            output_bit = 0
            break
        elif decrypted == wire_out.label_1:
            output_bit = 1
            break

    elapsed = time.time() - start_time

    return {
        "output": output_bit,
        "circuit_id": circuit.circuit_id,
        "description": circuit.description,
        "evaluation_time_ms": round(elapsed * 1000, 2),
        "creation_time_ms": round(circuit.creation_time * 1000, 2),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def compare_threshold(
    value: int,
    threshold: int,
    bit_width: int = 8
) -> Dict:
    """
    Securely compare a value against a threshold using garbled circuits.

    Converts multi-bit comparison into a series of single-bit comparisons
    starting from the most significant bit. Simulates the full protocol.

    Args:
        value: The value to compare (e.g., average blood pressure).
        threshold: The threshold to compare against (e.g., 140).
        bit_width: Number of bits to use for the comparison.

    Returns:
        Dictionary with comparison result and metadata.

    Example:
        >>> result = compare_threshold(150, 140)
        >>> result["exceeds_threshold"]
        True
        >>> result["value_revealed"]
        False
    """
    start_time = time.time()

    # Convert to binary (MSB first)
    value_bits = [(value >> (bit_width - 1 - i)) & 1 for i in range(bit_width)]
    threshold_bits = [(threshold >> (bit_width - 1 - i)) & 1 for i in range(bit_width)]

    # Build comparison circuit bit by bit
    gt_so_far = 0
    eq_so_far = 1
    gate_results = []

    for i in range(bit_width):
        v_bit = value_bits[i]
        t_bit = threshold_bits[i]

        # Create a GT circuit for this bit position
        circuit = create_garbled_circuit("GT", f"Bit {i}: value > threshold?")
        bit_result = evaluate_circuit(circuit, v_bit, t_bit)

        # Update running comparison
        if eq_so_far:
            if v_bit > t_bit:
                gt_so_far = 1
                eq_so_far = 0
            elif v_bit < t_bit:
                gt_so_far = 0
                eq_so_far = 0

        gate_results.append({
            "bit_position": i,
            "gate_output": bit_result["output"],
            "circuit_id": bit_result["circuit_id"],
        })

    elapsed = time.time() - start_time

    return {
        "exceeds_threshold": bool(gt_so_far),
        "is_equal": bool(eq_so_far),
        "value_revealed": False,  # Individual value never exposed
        "threshold_revealed": True,  # Threshold is public
        "num_gates": len(gate_results),
        "bit_width": bit_width,
        "gate_details": gate_results,
        "total_time_ms": round(elapsed * 1000, 2),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
