from utils import *
from mytests import *
from gen_aut import _gen_aut

from automata.fa.fa import FA
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA

from pysat.solvers import Minisat22, Minicard
from pysat.formula import CNF, CNFPlus, IDPool


def gen_autr(alphabet: str, pos: list[str], neg: list[str], k: int) -> DFA | None:
    # À COMPLÉTER
    cnf, vpool = _gen_aut(alphabet, pos, neg, k)
    acceptation = ["acceptant", "non-acceptant"]
    states = [nb for nb in range(1, k + 1)]
    A = 0

    # for i in states:
    #     for j in states:
    #         for letter in alphabet:
    #             cnf.append([-vpool.id((i, letter, j)), vpool.id((j, letter, i))])
                # cnf.append([vpool.id((i, letter, j)), -vpool.id((j, letter, i))])
    # for word in pos:
    #     for t in range(len(word)):
    #         for i in states:
    #             for j in states:
    #                 cnf.append([-vpool.id((word, j, t+1)), vpool.id((word, i, t))])
    for letter in alphabet:
        for i in states:
            for j in states:
                for q in states:
                    if q != i:
                        cnf.append([-vpool.id((i, letter, j)), -vpool.id((q, letter, j))])


    solver = Minisat22()
    solver.append_formula(cnf.clauses, no_return=False)
    _ = solver.solve()
    model = solver.get_model()
    if model is None:
        return None
    dfa = build_dfa(states, alphabet, acceptation, model, vpool)
    return dfa


def main():
    test_autr()
    # t = (
    #     "ab",
    #     ["b", "ab", "ba", "aba", "abbba", "bbababab"],
    #     ["", "a", "bba", "aaa", "aa", "abab"],
    #     2,
    # )
    # # t = ("ab", ["aa", "ab", "ba"], ["", "a", "b", "bb", "aaa", "aba", "bba"], 5)
    # gen_autr(t[0], t[1], t[2], t[3])


if __name__ == "__main__":
    main()
