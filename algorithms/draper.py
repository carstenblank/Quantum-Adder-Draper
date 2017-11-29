from datetime import datetime
import json
from typing import Dict, Tuple, Callable, Any

from qiskit import QuantumProgram, QuantumRegister, QuantumCircuit, Result
import qft_extended
from qiskit.tools.qcvv.tomography import build_state_tomography_circuits

from qiskit.extensions.standard import barrier

token = "ca665158a6f8d6515e9b8a7d1502e3ebce140b217f896df0e82cf343f71e922c5ee7c6a24ded23c5d7def3241ce06a265f95f499b0b1b912a2c366b6e1d70f18"
url = 'https://quantumexperience.ng.bluemix.net/api'

backend_local_simulator = "local_qasm_simulator"
backend_real_processor = "ibmqx4"
backend_online_simulator = "ibmqx_qasm_simulator"


def algorithm_regular(qc: QuantumCircuit, a1: Tuple[QuantumRegister,int], a2: Tuple[QuantumRegister,int],
                      b1: Tuple[QuantumRegister,int], b2: Tuple[QuantumRegister,int]) -> QuantumCircuit:
    qc.comment(["BEGIN QFT"])
    qc.h(a1)
    qc.crk(2, a1, a2, cnot_back=True)
    qc.h(a2)
    qc.comment(["END QFT"])

    qc.crk(1, a2, b2)
    qc.crk(2, a1, b2)
    qc.crk(1, a1, b1, cnot_back=True)

    qc.comment(["BEGIN QFT†"])
    qc.h(a2)
    qc.crk(-2, a1, a2, cnot_back=True)
    qc.h(a1)
    qc.comment(["END QFT†"])
    return qc


def algorithm_test(qc: QuantumCircuit, a1: Tuple[QuantumRegister,int], a2: Tuple[QuantumRegister,int],
                      b1: Tuple[QuantumRegister,int], b2: Tuple[QuantumRegister,int]) -> QuantumCircuit:
    #qc.h(a1)
    #qc.crk(2, a1, a2, cnot_back=True)
    # qc.h(a2)
    #
    qc.crk(1, a2, b2)
    # qc.crk(2, a1, b2)
    # qc.crk(1, a1, b1, cnot_back=True)
    #
    # qc.h(a2)
    # qc.crk(-2, a1, a2, cnot_back=True)
    # qc.h(a1)
    return qc


def create_experiment(Q_program: QuantumProgram, a: str, b: str, name:str, backend: str,
                      algorithm: Callable[[QuantumCircuit,Tuple[QuantumRegister,int],Tuple[QuantumRegister,int],Tuple[QuantumRegister,int],Tuple[QuantumRegister,int]],QuantumCircuit] = algorithm_regular,
                      silent=True) \
        -> Tuple[str,str, dict]:
    # qubit mapping
    index_a1 = 2
    index_a2 = 4
    index_b1 = 0
    index_b2 = 3

    # input build
    q: QuantumRegister = Q_program.create_quantum_register("q", 5)
    ans = Q_program.create_classical_register("ans", 5)
    qc: QuantumCircuit = Q_program.create_circuit(name, [q], [ans])

    a1: Tuple[QuantumRegister,int] = q[index_a1]
    a2: Tuple[QuantumRegister,int] = q[index_a2]
    b1: Tuple[QuantumRegister,int] = q[index_b1]
    b2: Tuple[QuantumRegister,int] = q[index_b2]
    expected = list("00000")
    expected_result = (int(a, 2) + int(b, 2)) % 4
    expected[index_a1] = str(int(expected_result / 2) % 2)
    expected[index_a2] = str(int(expected_result / 1) % 2)
    expected[index_b1] = b[2]
    expected[index_b2] = b[3]
    expected = "".join(reversed(expected))
    if not silent:
        print("Job: %s + %s = %s. Expecting answer: %s" % (a, b, bin(expected_result), expected))

    # circuit setup
    if a[2] == "1":
        if not silent: print("a1 setting to 1")
        qc.x(a1)
    if a[3] == "1":
        if not silent: print("a2 setting to 1")
        qc.x(a2)
    if b[2] == "1":
        if not silent: print("b1 setting to 1")
        qc.x(b1)
    if b[3] == "1":
        if not silent: print("b2 setting to 1")
        qc.x(b2)

    algorithm(qc,a1,a2,b1,b2)

    qc.measure(q, ans)

    # job parameters
    processor = "ibmqx4"
    #print("Compile & Run manually for '%s' using backend '%s':" % (processor, backend))

    qobj_id = "@%s: %s(%s,%s) -> %s" % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), name, a, b, expected)

    conf = Q_program.get_backend_configuration(processor, list_format=False)
    qobj = Q_program.compile(name_of_circuits=[name], backend=backend, config=conf,
                             max_credits=3, qobjid=qobj_id)

    qasm = "\n".join(filter(lambda x: len(x) > 0, qc.qasm().split("\n")))#Q_program.get_compiled_qasm(qobj, name)
    # measurements = list(filter(lambda r: "measure" in r, qasm.split('\n')))
    # instructions = list(filter(lambda r: "measure" not in r, qasm.split('\n')))
    #
    # qasm = "\n".join(["// draper(%s,%s)->%s" % (a, b, expected)] + instructions + measurements)
    return qasm, expected, qobj


if __name__ == "__main__":
    Q_program: QuantumProgram = QuantumProgram()
    Q_program.set_api(token, url)

    qasm, expected, _ = create_experiment(Q_program, "0b11", "0b01", "draper",
                                       "local_qasm_simulator", algorithm_regular)

    print(len(qasm.split("\n")))
    print(qasm)
