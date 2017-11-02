from typing import List, Tuple

from qiskit import CompositeGate, QuantumRegister, QuantumCircuit


class QFTGate(CompositeGate):
    def __init__(self, q: List[Tuple[QuantumRegister,int]], circ):
        super().__init__("qft", [], q, circ)
        #super().__init__("qft", [], [q[i] for i in range(q.size)], circ)

        self.registers = q

        for qr in q:
            self._check_qubit(qr)
        bla = q.copy()
        for qr in reversed(q):
            self.h(qr)
            print("H on %s[%d]" % qr)
            k = 2
            bla.remove(qr)
            for qj in reversed(bla):
                self.crk(k, qr, qj)
                print("cR_%d on %s[%d] controlled by %s[%d]" % (k, qr[0].name, qr[1], qj[0].name, qj[1]))
                k = k + 1
        print("qft done")

    def reapply(self, circ):
        """Reapply this gate to corresponding qubits in circ."""
        self._modifiers(circ.qft(self.registers))


def qft(self, q):
    return self._attach(QFTGate(q, self))

QuantumCircuit.qft = qft
CompositeGate.qft = qft