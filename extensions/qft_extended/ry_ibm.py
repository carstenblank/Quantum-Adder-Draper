from qiskit import CompositeGate, QuantumRegister, InstructionSet, QuantumCircuit


class RYGate_ibm(CompositeGate):

    def __init__(self, θ, q, circ=None):
        super().__init__("ry_ibm", [θ], [q], circ)
        if θ != 0.0:
            self.u3(θ,0,0, q)
        #else:
        #    self.iden(q)


def ry_ibm(self,  θ: float, q):
    if isinstance(q, QuantumRegister):
        gs = InstructionSet()
        for j in range(q.size):
            gs.add(self.ry_ibm(θ, (q, j)))
        return gs
    else:
        self._check_qubit(q)
        return self._attach(RYGate_ibm(θ, q, self))

QuantumCircuit.ry_ibm = ry_ibm
CompositeGate.ry_ibm = ry_ibm