from typing import Tuple

from qiskit import QuantumRegister, QuantumProgram


class Experiment(object):

    def __init__(self, name, backend, version, qubit_mapping, algorithm):
        self.name = name
        self.backend = backend
        self.version = version
        self.qubit_mapping = qubit_mapping
        self.algorithm = algorithm

    def create_experiment(self, qp: QuantumProgram, input) -> Tuple[str, dict, str]:
        pass

    def get_inputs(self):
        pass

    def get_shots(self):
        return 1024

    def qasm(self, input, output):
        return [
            "//@name={%s}" % self.name,
            "//@input={%s}" % str(input),
            "//@output={%s}" % str(output),
            "//@algorithm={%s}" % self.algorithm,
            "//@version{%s}" % self.version,
            "//@mapping{%s}" % self.qubit_mapping
        ]

    @staticmethod
    def coupling_direction(coupling_map: dict, a: Tuple[QuantumRegister, int], b: Tuple[QuantumRegister, int]) -> int:
        if b[1] in coupling_map and a[1] in coupling_map[b[1]]:
            return 1
        if a[1] in coupling_map and b[1] in coupling_map[a[1]]:
            return -1
        return 0


backend_local_simulator = "local_qasm_simulator"
backend_online_ibmqx5 = "ibmqx5"
backend_online_ibmqx4 = "ibmqx4"
backend_online_ibmqx2 = "ibmqx2"
backend_online_simulator = "ibmqx_qasm_simulator"