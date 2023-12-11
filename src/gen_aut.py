from utils import *
from mytests import *

from automata.fa.fa import FA
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA

from pysat.solvers import Minisat22, Minicard
from pysat.formula import CNF, CNFPlus, IDPool


def variable_names(alphabet: str, k: int, vpools, pos, neg) -> dict:
    states = [nb for nb in range(1, k + 1)]
    acceptation = ["non-acceptant", "acceptant"]  # 1:= Non-Acceptant, 2:= Acceptant
    # initial = ["non-initial", "initial"]  # 1:= Pas Initial, 2:= Initial
    variables = dict()
    for i in states:
        for accept in acceptation:
            # for init in initial:
            variables[vpools.id((i, accept))] = "Q" + str(i) + " " + accept

    for i in states:
        for letter in alphabet:
            for j in states:
                variables[vpools.id((i, letter, j))] = (
                    "Q" + str(i) + " -" + letter + "-> Q" + str(j)
                )

    for word in pos:
        for t in range(len(word)):
            for i in states:
                variables[vpools.id((word, i, t))] = (
                    "Etat Q"
                    + str(i)
                    + " pour la lettre "
                    + word[t]
                    + "("
                    + str(t)
                    + ") sur le mot "
                    + word
                    + " positif"
                )

    for word in neg:
        for t in range(len(word)):
            for i in states:
                variables[vpools.id((word, i, t))] = (
                    "Etat Q"
                    + str(i)
                    + " pour la lettre "
                    + word[t]
                    + "("
                    + str(t)
                    + ") sur le mot "
                    + word
                    + " (négatif)"
                )

    return variables


def gen_aut(alphabet: str, pos: list[str], neg: list[str], k: int) -> DFA:
    cnf = CNFPlus()

    vpools = IDPool()

    acceptant = ["acceptant", "non-acceptant"]
    states = [nb for nb in range(1, k + 1)]
    A = 0
    NA = 1

    # Il y a un unique état initial
    cnf.append([vpools.id((1, "non-acceptant"))])
