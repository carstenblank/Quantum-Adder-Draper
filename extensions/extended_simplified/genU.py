from qiskit import CompositeGate, QuantumRegister, InstructionSet, QuantumCircuit


class GenUGate(CompositeGate):

    def __init__(self, α: float, β: float, γ: float, δ: float, q, circ = None):
        super().__init__("genU", [α, β, γ, δ], [q], circ)
        self.rz_ibm( δ, q)
        self.ry_ibm(γ, q)
        self.rz_ibm(β, q)
        self.phase(α, q)


def genU(self,  α: float, β: float, γ: float, δ: float, q):
    if isinstance(q, QuantumRegister):
        gs = InstructionSet()
        for j in range(q.size):
            gs.add(self.genU(α, β, γ, δ, (q, j)))
        return gs
    else:
        self._check_qubit(q)
        return self._attach(GenUGate(α, β, γ, δ, q, self))

QuantumCircuit.genU = genU
CompositeGate.genU = genU