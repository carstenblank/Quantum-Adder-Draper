# from typing import List
#
# import math
# import tkinter
# from IBMQuantumExperience.IBMQuantumExperience import IBMQuantumExperience

from qiskit import QuantumProgram, QuantumCircuit, QuantumRegister, CompositeGate

from qft_extended import *

token = "a6c65f024279c033c9368bd14e6f9079b71fdfd00625b1f3d3573475c97d84d429c8b4316aa572709dd2670e9a069e735f127342360a7ec6bd8f17f82a997ba2"
url = 'https://quantumexperience.ng.bluemix.net/api'

QPS_SPECS = {
    "name": "Program",
    "circuits": [{
        "name": "adder",
        "quantum_registers": [
            {"name": "a",
             "size": 2},
            {"name": "b",
             "size": 2}
        ],
        "classical_registers": [
            {"name": "ans",
             "size": 4},
        ]}]
}

qp: QuantumProgram = QuantumProgram(specs=QPS_SPECS)
qc: QuantumCircuit = qp.get_circuit("adder")
a: QuantumRegister = qp.get_quantum_registers("a")
b:QuantumRegister = qp.get_quantum_registers("b")
ans = qp.get_classical_registers("ans")

#qc.x(a[0])
#qc.x(a[1])
qc.x(b[1])
qc.x(b[0])

qc.qft(a)
#qc.h(a)
qc.crk(1,a[1],b[1])
qc.crk(2,a[1],b[0])
qc.crk(1,a[0],b[0])
qc.qft(a).inverse()
qc.measure(a[0],ans[0])
qc.measure(a[1],ans[1])
qc.measure(b[0],ans[2])
qc.measure(b[1],ans[3])

devices = [ "local_qasm_simulator", "simulator", "ibmqx_qasm_simulator" ]

#qp.execute(["adder"],coupling_map={ 0: [1], 1: [2], 2: [3], 3: [4], 4: [] })
#qp.execute(["adder"],coupling_map={ 0: [1,2], 1: [2], 2: [], 3: [2,4], 4: [2] })
qp.execute(["adder"], devices[2])

qsm = qp.get_qasm("adder")
print("qasm raw:\n%s" % qsm)

qsm = qp.get_compiled_qasm("adder", devices[2])
print("qasm compiled\n%s" % qsm)

result = qp.get_result("adder", devices[2])
print(result)