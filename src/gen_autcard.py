from utils import *
from mytests import *
from gen_aut import _gen_aut

from automata.fa.fa import FA
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA

from pysat.solvers import Minisat22, Minicard
from pysat.formula import CNF, CNFPlus, IDPool


def gen_autcard(alphabet: str, pos: list[str], neg: list[str], k: int, ell: int) -> DFA | None:
    # À COMPLÉTER
    cnf, vpool = _gen_aut(alphabet, pos, neg, k)
    acceptation = ["acceptant", "non-acceptant"]
    states = [nb for nb in range(1, k + 1)]
    A = 0
    # Complet
    for i in states:
        for letter in alphabet:
            d = []
            for j in states:
                d.append(vpool.id((i, letter, j)))  # Transition de i vers j avec la lettre letter
            cnf.append(d)
    # Au plus ell acceptant
    d = []
    for i in states:
        for accept in acceptation:
            if accept == acceptation[A]:
                d.append(vpool.id((i, accept)))

    solver = Minicard()
    solver.append_formula(cnf.clauses, no_return=False)
    solver.add_atmost(d, ell, no_return=False)
    _ = solver.solve()
    model = solver.get_model()
    if model is None:
        return None
    dfa = build_dfa(states, alphabet, acceptation, model, vpool)
    return dfa


def main():
    test_autcard()


if __name__ == "__main__":
    main()
