from qiskit import CompositeGate, QuantumRegister, InstructionSet, QuantumCircuit


class RZGate_ibm(CompositeGate):

    def __init__(self, θ, q, circ=None):
        super().__init__("rz_ibm", [θ], [q], circ)
        self.x(q)
        self.u1(- θ / 2, q)
        self.x(q)
        self.u1(θ / 2, q)



def rz_ibm(self,  θ: float, q):
    if isinstance(q, QuantumRegister):
        gs = InstructionSet()
        for j in range(q.size):
            gs.add(self.rz_ibm(θ, (q, j)))
        return gs
    else:
        self._check_qubit(q)
        return self._attach(RZGate_ibm(θ, q, self))

QuantumCircuit.rz_ibm = rz_ibm
CompositeGate.rz_ibm = rz_ibm