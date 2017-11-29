import math
from typing import Tuple

from extensions.qft_extended.cr import CRGate
from qiskit import QuantumCircuit, CompositeGate, QuantumRegister


class CRkGate(CRGate):

    def __init__(self, k, target: Tuple[QuantumRegister,int], control: Tuple[QuantumRegister,int], circ, cnot_back: bool = False):
        sign = -1 if k < 0 else 1
        λ = sign * 2 * math.pi / math.pow(2, abs(k))
        super().__init__(λ, target, control, circ, cnot_back)


def crk(self,  k: int, tgt, ctl, cnot_back: bool = False):
    self._check_qubit(ctl)
    self._check_qubit(tgt)
    self._check_dups([ctl, tgt])
    return self._attach(CRkGate(k, tgt, ctl, self, cnot_back))


QuantumCircuit.crk = crk
CompositeGate.crk = crk