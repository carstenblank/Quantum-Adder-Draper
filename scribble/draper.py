from datetime import datetime
import json
from typing import Dict, Tuple

from qiskit import QuantumProgram, QuantumRegister, QuantumCircuit, Result
import qft_extended
from qiskit.tools.qcvv.tomography import build_state_tomography_circuits

token = "a6c65f024279c033c9368bd14e6f9079b71fdfd00625b1f3d3573475c97d84d429c8b4316aa572709dd2670e9a069e735f127342360a7ec6bd8f17f82a997ba2"
url = 'https://quantumexperience.ng.bluemix.net/api'

def create_experiment(Q_program: QuantumProgram, inputA: str, inputB: str, name:str, backend: str) -> Tuple[str,str]:
    # qubit mapping
    index_a1 = 2
    index_a2 = 4
    index_b1 = 0
    index_b2 = 3

    # input build
    q = Q_program.create_quantum_register("q", 5)
    ans = Q_program.create_classical_register("ans", 5)
    qc: QuantumCircuit = Q_program.create_circuit(name, [q], [ans])

    a1 = q[index_a1]
    a2 = q[index_a2]
    b1 = q[index_b1]
    b2 = q[index_b2]
    expected = list("00000")
    expected_result = (int(a, 2) + int(b, 2)) % 4
    expected[index_a1] = str(int(expected_result / 2) % 2)
    expected[index_a2] = str(int(expected_result / 1) % 2)
    expected[index_b1] = b[2]
    expected[index_b2] = b[3]
    expected = "".join(reversed(expected))
    print("Job: %s + %s = %s. Expecting answer: %s" % (a, b, bin(expected_result), expected))

    # circuit setup
    if a[2] == "1":
        print("a1 setting to 1")
        qc.x(a1)
    if a[3] == "1":
        print("a2 setting to 1")
        qc.x(a2)
    if b[2] == "1":
        print("b1 setting to 1")
        qc.x(b1)
    if b[3] == "1":
        print("b2 setting to 1")
        qc.x(b2)

    # circuit algorithm
    qc.h(a1)
    qc.crk(2, a1, a2, cnot_back=True)
    qc.h(a2)

    qc.crk(1, a2, b2)
    qc.crk(2, a1, b2)
    qc.crk(1, a1, b1, cnot_back=True)

    qc.h(a2)
    qc.crk(-2, a1, a2, cnot_back=True)
    qc.h(a1)

    qc.measure(q, ans)

    # job parameters
    processor = "ibmqx4"
    print("Compile & Run manually for '%s' using backend '%s':" % (processor, backend))

    qobj_id = "@%s: %s(%s,%s) -> %s" % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), name, a, b, expected)

    conf = Q_program.get_backend_configuration(processor, list_format=False)
    qobj = Q_program.compile(name_of_circuits=[name], backend=backend, shots=shots, config=conf,
                             max_credits=3, qobj_id=qobj_id)
    qasm = Q_program.get_compiled_qasm(qobj, name)
    measurements = list(filter(lambda r: "measure" in r, qasm.split('\n')))
    instructions = list(filter(lambda r: "measure" not in r, qasm.split('\n')))

    qasm = "\n".join(["// draper(%s,%s)->%s" % (a, b, expected)] + instructions + measurements)
    return qasm, expected

if __name__ == '__main__':
    Q_program: QuantumProgram = QuantumProgram()

    Q_program.set_api(token, url)
    print(Q_program.available_backends())

    # Backend parameters
    #backend = "local_qasm_simulator"
    #backend = "ibmqx4"
    backend = "ibmqx_qasm_simulator"

    # input
    name = "draper"
    shots = 1000
    max_credits = 3
    a = "0b10"
    b = "0b00"

    qasm, expected = create_experiment(Q_program,a ,b ,name, backend)

    result: Dict[str, str] = Q_program.get_api().run_job([{"qasm": qasm}], backend, shots, max_credits=max_credits, seed=None)

    print()
    print("Result Dump:")
    print(result)

def old_main():
    # Backend parameters
    #backend = "local_qasm_simulator"
    #backend = "ibmqx4"
    backend = "ibmqx_qasm_simulator"

    name = "draper"

    # input
    a = "0b10"
    b = "0b00"
    # qubit mapping
    index_a1 = 2
    index_a2 = 4
    index_b1 = 0
    index_b2 = 3

    # input build
    Q_program: QuantumProgram = QuantumProgram()

    Q_program.set_api(token, url)
    print(Q_program.available_backends())

    q = Q_program.create_quantum_register("q", 5)
    ans = Q_program.create_classical_register("ans", 5)
    qc: QuantumCircuit = Q_program.create_circuit(name, [q], [ans])

    a1 = q[index_a1]
    a2 = q[index_a2]
    b1 = q[index_b1]
    b2 = q[index_b2]
    expected = list("00000")
    expected_result = (int(a, 2) + int(b, 2)) % 4
    expected[index_a1] = str(int(expected_result / 2) % 2)
    expected[index_a2] = str(int(expected_result / 1) % 2)
    expected[index_b1] = b[2]
    expected[index_b2] = b[3]
    expected = "".join(reversed(expected))
    print("Job: %s + %s = %s. Expecting answer: %s" % (a, b, bin(expected_result), expected))

    # circuit setup
    if a[2] == "1":
        print("a1 setting to 1")
        qc.x(a1)
    if a[3] == "1":
        print("a2 setting to 1")
        qc.x(a2)
    if b[2] == "1":
        print("b1 setting to 1")
        qc.x(b1)
    if b[3] == "1":
        print("b2 setting to 1")
        qc.x(b2)

    # circuit algorithm
    # qc.qft([a1,a2])
    qc.h(a1)
    qc.crk(2, a1, a2, cnot_back=True)
    qc.h(a2)

    added = []
    # added = added + build_state_tomography_circuits(Q_program, "draper", [0], a, ans)
    # added = added + build_state_tomography_circuits(Q_program, "draper", [1], a, ans)
    # added = added + build_state_tomography_circuits(Q_program, "draper", [0,1], a, ans)
    # print(added)

    qc.crk(1, a2, b2)
    qc.crk(2, a1, b2)
    qc.crk(1, a1, b1, cnot_back=True)

    qc.h(a2)
    qc.crk(-2, a1, a2, cnot_back=True)
    qc.h(a1)
    # qc.qft([a1,a2]).inverse()

    qc.measure(q, ans)

    # tomography setup
    if len(added) > 0: print("Tomography")
    for tomo_programm in added:
        result = Q_program.execute([tomo_programm], backend='local_qasm_simulator', shots=1000)
        print("%s: %s" % (tomo_programm, result.get_data(tomo_programm)))

    # job parameters
    shots = 1000
    processor = "ibmqx4"
    print("Compile & Run manually for '%s' @%d shots using backend '%s':" % (processor, shots, backend))

    qobj_id = "@%s: %s(%s,%s) -> %s" % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), name, a, b, expected)

    conf = Q_program.get_backend_configuration(processor, list_format=False)
    qobj = Q_program.compile(name_of_circuits=[name], backend=backend, shots=shots, config=conf,
                             max_credits=3, qobj_id=qobj_id)
    qasm = Q_program.get_compiled_qasm(qobj, name)
    measurements = list(filter(lambda r: "measure" in r, qasm.split('\n')))
    instructions = list(filter(lambda r: "measure" not in r, qasm.split('\n')))
    # qobj["circuits"][0]["compiled_circuit_qasm"] = "\n".join(instructions + measurements)
    # result: Result = Q_program.run(qobj, wait=10, timeout=3600)

    qasm = "\n".join(["// draper(%s,%s)->%s" % (a, b, expected)] + instructions + measurements)

    result: Dict[str, str] = Q_program.get_api().run_job([{"qasm": qasm}], backend, shots, max_credits=3, seed=None)

    # print("Status of job run (%s): %s" % (qobj_id,result.get_status()))

    # if result.get_status() == "COMPLETED":
    #    counts = result.get_counts(name)
    #    print("Expected result %s has probability: %.4f" % (expected,counts[expected]/float(shots)))
    #    print("Result of calculation (%s): %s" % (backend, result.get_data(name)))
