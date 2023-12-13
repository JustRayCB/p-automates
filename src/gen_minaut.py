from typing import List, Tuple
from utils import *
from mytests import *
from gen_aut import _gen_aut

from automata.fa.fa import FA
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA

from pysat.solvers import Minisat22, Minicard
from pysat.formula import CNF, CNFPlus, IDPool


def gen_minaut(alphabet: str, pos: list[str], neg: list[str]) -> DFA | None:
    acceptation = ["acceptant", "non-acceptant"]
    found = False
    e = 0
    model, vpool = None, None
    found = False
    k = 0
    while not found:
        solver = Minisat22()
        cnf, vpool = _gen_aut(alphabet, pos, neg, 2**e)
        solver.append_formula(cnf.clauses, no_return=False)
        _ = solver.solve()
        model = solver.get_model()
        if model:
            found = True
        e += 1

    states = [nb for nb in range(1, k + 1)]
    A = 0
    dfa = build_dfa(states, alphabet, acceptation, model, vpool)
    return dfa


def main():
    test_minaut()


if __name__ == "__main__":
    main()
