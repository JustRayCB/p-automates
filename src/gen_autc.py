from utils import *
from mytests import *
from gen_aut import _gen_aut

from automata.fa.fa import FA
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA

from pysat.solvers import Minisat22, Minicard
from pysat.formula import CNF, CNFPlus, IDPool


def gen_autc(alphabet: str, pos: list[str], neg: list[str], k: int) -> DFA | None:
    # À COMPLÉTER
    cnf, vpool = _gen_aut(alphabet, pos, neg, k)
    acceptation = ["acceptant", "non-acceptant"]
    states = [nb for nb in range(1, k + 1)]
    A = 0

    for i in states:
        for letter in alphabet:
            d = []
            for j in states:
                d.append(vpool.id((i, letter, j)))  # Transition de i vers j avec la lettre letter
            cnf.append(d)

    solver = Minisat22()
    solver.append_formula(cnf.clauses, no_return=False)
    _ = solver.solve()
    model = solver.get_model()
    if model is None:
        return None
    dfa = build_dfa(states, alphabet, acceptation, model, vpool)
    return dfa


def main():
    test_autc()


if __name__ == "__main__":
    main()
