from qiskit import CompositeGate, QuantumCircuit, QuantumRegister, InstructionSet


class GencUGate(CompositeGate):

    def __init__(self, α: float, β: float, γ: float, δ: float, target, control, circ, cnot_back: bool = False):
        super().__init__("gencU", [α, β, γ, δ], [target, control], circ)
        self._c(target)
        self._cx(control, target, cnot_back)
        self._b(target)
        self._cx(control, target, cnot_back)
        self._a(target)
        self.u1(α, control)

    def _cx(self, control, target, bachward):
        if bachward:
            self.h(control)
            self.h(target)

        if bachward:
            self.cx(target, control)
        else:
            self.cx(control, target)

        if bachward:
            self.h(control)
            self.h(target)

    def _a(self, target):
        β = self.param[1]
        γ = self.param[2]
        self.ry_ibm(γ / 2, target)
        self.rz_ibm(β, target)

    def _b(self, target):
        β = self.param[1]
        γ = self.param[2]
        δ = self.param[3]
        self.rz_ibm(-(δ + β) / 2, target)
        self.ry_ibm(-γ / 2, target)

    def _c(self, target):
        β = self.param[1]
        δ = self.param[3]
        self.rz_ibm((δ - β) / 2, target)


def gencU(self,  α: float, β: float, γ: float, δ: float, tgt, ctl, cnot_back: bool = False):
    self._check_qubit(ctl)
    self._check_qubit(tgt)
    self._check_dups([ctl, tgt])
    return self._attach(GencUGate(α, β, γ, δ, tgt, ctl, self, cnot_back))

QuantumCircuit.gencU = gencU
CompositeGate.gencU = gencU