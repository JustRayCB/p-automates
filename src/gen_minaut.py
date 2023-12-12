from typing import List, Tuple
from utils import *
from mytests import *
from gen_aut import gen_aut

from automata.fa.fa import FA
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA

from pysat.solvers import Minisat22, Minicard
from pysat.formula import CNF, CNFPlus, IDPool


def gen_minaut(alphabet: str, pos: list[str], neg: list[str]) -> DFA | None:
    ...
