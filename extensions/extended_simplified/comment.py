from typing import List

from qiskit import CompositeGate, QuantumRegister, InstructionSet, QuantumCircuit, Instruction


class CommentGate(Instruction):
    def __init__(self, comments: List[str], circ=None):
        super().__init__("comment", comments, [], circ)

    def qasm(self):
        """Return OPENQASM string."""
        return "\n".join(["// %s" % x for x in self.param])

    def inverse(self):
        """Invert this gate."""
        return self


def comment(self,  comments: List[str]):
        return self._attach(CommentGate(comments, self))

QuantumCircuit.comment = comment
CompositeGate.comment = comment
