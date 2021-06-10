# Copyright 2021 The Cirq Developers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest
import numpy as np

import cirq
from cirq.testing import assert_allclose_up_to_global_phase


def test_clifford_decompose_one_qubit():
    """Two random instance for one qubit decomposition."""
    qubits = cirq.LineQubit.range(1)
    args = cirq.ActOnCliffordTableauArgs(
        tableau=cirq.CliffordTableau(num_qubits=1),
        axes=[0],
        prng=np.random.RandomState(),
        log_of_measurement_results={},
    )
    cirq.act_on(cirq.X, args, allow_decompose=False)
    cirq.act_on(cirq.H, args, allow_decompose=False)
    cirq.act_on(cirq.S, args, allow_decompose=False)
    expect_circ = cirq.Circuit(cirq.X(qubits[0]), cirq.H(qubits[0]), cirq.S(qubits[0]))
    ops = cirq.decompose_clifford_tableau_to_operations(qubits, args.tableau)
    circ = cirq.Circuit(ops)
    assert_allclose_up_to_global_phase(cirq.unitary(expect_circ), cirq.unitary(circ), atol=1e-7)

    qubits = cirq.LineQubit.range(1)
    args = cirq.ActOnCliffordTableauArgs(
        tableau=cirq.CliffordTableau(num_qubits=1),
        axes=[0],
        prng=np.random.RandomState(),
        log_of_measurement_results={},
    )
    cirq.act_on(cirq.Z, args, allow_decompose=False)
    cirq.act_on(cirq.H, args, allow_decompose=False)
    cirq.act_on(cirq.S, args, allow_decompose=False)
    cirq.act_on(cirq.H, args, allow_decompose=False)
    cirq.act_on(cirq.X, args, allow_decompose=False)
    expect_circ = cirq.Circuit(
        cirq.Z(qubits[0]),
        cirq.H(qubits[0]),
        cirq.S(qubits[0]),
        cirq.H(qubits[0]),
        cirq.X(qubits[0]),
    )
    ops = cirq.decompose_clifford_tableau_to_operations(qubits, args.tableau)
    circ = cirq.Circuit(ops)
    assert_allclose_up_to_global_phase(cirq.unitary(expect_circ), cirq.unitary(circ), atol=1e-7)


def test_clifford_decompose_two_qubits():
    """Two random instance for one qubit decomposition."""
    qubits = cirq.LineQubit.range(2)
    args = cirq.ActOnCliffordTableauArgs(
        tableau=cirq.CliffordTableau(num_qubits=2),
        axes=[0],
        prng=np.random.RandomState(),
        log_of_measurement_results={},
    )
    cirq.act_on(cirq.H, args, allow_decompose=False)
    args.axes = [0, 1]
    cirq.act_on(cirq.CNOT, args, allow_decompose=False)
    expect_circ = cirq.Circuit(cirq.H(qubits[0]), cirq.CNOT(qubits[0], qubits[1]))
    ops = cirq.decompose_clifford_tableau_to_operations(qubits, args.tableau)
    circ = cirq.Circuit(ops)
    assert_allclose_up_to_global_phase(cirq.unitary(expect_circ), cirq.unitary(circ), atol=1e-7)

    qubits = cirq.LineQubit.range(2)
    args = cirq.ActOnCliffordTableauArgs(
        tableau=cirq.CliffordTableau(num_qubits=2),
        axes=[0],
        prng=np.random.RandomState(),
        log_of_measurement_results={},
    )
    cirq.act_on(cirq.H, args, allow_decompose=False)
    args.axes = [0, 1]
    cirq.act_on(cirq.CNOT, args, allow_decompose=False)
    args.axes = [0]
    cirq.act_on(cirq.H, args, allow_decompose=False)
    cirq.act_on(cirq.S, args, allow_decompose=False)
    args.axes = [1]
    cirq.act_on(cirq.X, args, allow_decompose=False)
    expect_circ = cirq.Circuit(
        cirq.H(qubits[0]),
        cirq.CNOT(qubits[0], qubits[1]),
        cirq.H(qubits[0]),
        cirq.S(qubits[0]),
        cirq.X(qubits[1]),
    )

    ops = cirq.decompose_clifford_tableau_to_operations(qubits, args.tableau)
    circ = cirq.Circuit(ops)
    assert_allclose_up_to_global_phase(cirq.unitary(expect_circ), cirq.unitary(circ), atol=1e-7)


def test_clifford_decompose_small_number_qubits_unitary():
    """Use unitary matrix to validate the decomposition of random Clifford Tableau.

    Due to the exponential increasing in dimension, it cannot validate very large number of qubits.
    """
    n, num_ops = 5, 20
    gate_candidate = [cirq.X, cirq.Y, cirq.Z, cirq.H, cirq.S, cirq.CNOT, cirq.CZ]
    for seed in range(150, 300):
        prng = np.random.RandomState(seed)
        t = cirq.CliffordTableau(num_qubits=n)
        qubits = cirq.LineQubit.range(n)
        expect_circ = cirq.Circuit()
        args = cirq.ActOnCliffordTableauArgs(
            tableau=t, axes=[], prng=prng, log_of_measurement_results={}
        )
        for _ in range(num_ops):
            g = prng.randint(len(gate_candidate))
            indices = (prng.randint(n),) if g < 5 else prng.choice(n, 2, replace=False)
            args.axes = indices
            cirq.act_on(gate_candidate[g], args, allow_decompose=False)
            expect_circ.append(gate_candidate[g].on(*[qubits[i] for i in indices]))
        ops = cirq.decompose_clifford_tableau_to_operations(qubits, args.tableau)
        circ = cirq.Circuit(ops)
        circ.append(cirq.I.on_each(qubits))
        expect_circ.append(cirq.I.on_each(qubits))
        assert_allclose_up_to_global_phase(cirq.unitary(expect_circ), cirq.unitary(circ), atol=1e-7)


def test_clifford_decompose_large_number_qubits_tableau():
    """Use tabeau inverse and then method to validate the decomposition of random Clifford Tableau.

    This approach can validate very large number of qubits.
    """
    pass


if __name__ == "__main__":
    test_clifford_decompose_small_number_qubits_unitary()
