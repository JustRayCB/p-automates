from utils import *
from mytests import *

from automata.fa.fa import FA
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA

from pysat.solvers import Minisat22, Minicard
from pysat.formula import CNF, CNFPlus, IDPool


def variable_names(alphabet: str, k: int, vpools) -> dict:
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

    return variables


# Q2
def gen_aut(alphabet: str, pos: list[str], neg: list[str], k: int) -> DFA:
    # À COMPLÉTER
    affichage_sol = True
    vpools = IDPool(start_from=1)
    cnf = CNF()
    """Acceptation d'état -> Acceptant , Pas acceptant { A, NA}
    Type d'état -> Initial, Pas initial {I, NI}
    Etat -> {Qi,a,t | Si Qi,a,t est vrai alors Q  est l'état i de l'automate avec acceptation a de type t}
    """
    # Un état peut être acceptant ou non
    # Un type d'état peut être initial ou non
    states = [nb for nb in range(1, k + 1)]
    acceptation = ["non-acceptant", "acceptant"]  # 1:= Non-Acceptant, 2:= Acceptant
    # initial = ["non-initial", "initial"]  # 1:= Pas Initial, 2:= Initial
    NA = 0  # Non Acceptant et Non Initial
    A = 1  # Acceptant et Initial
    nb_transition = len(alphabet)
    varnames = variable_names(alphabet, k, vpools)
    # display keys and values
    for key, value in varnames.items():
        print(key, value)

    # 1 et 1 seul état initial
    cnf.append([vpools.id((states[0], acceptation[NA])), vpools.id((states[0], acceptation[A]))])

    # Au plus k états dans notre automate
    for i in range(len(states)):
        for j in range(i + 1, len(states)):
            for accept in acceptation:
                for accept2 in acceptation:
                    cnf.append(
                        [
                            -vpools.id((states[i], accept)),
                            -vpools.id((states[j], accept2)),
                        ]
                    )
    # Si un état est acceptant, il n'est pas non-acceptant
    for i in states:
        cnf.append(
            [
                -vpools.id((i, acceptation[NA])),
                -vpools.id((i, acceptation[A])),
            ]
        )

    # Il y a au moins un état acceptant
    disj = []
    for i in states:
        disj.append(vpools.id((i, acceptation[A])))
    cnf.append(disj)

    # Chaque état doit avoir au plus 1 transition pour chaque lettre de l'alphabet
    for i in states:
        for letter in alphabet:
            for j in states:
                for l in states:
                    if j != l:
                        cnf.append([-vpools.id((i, letter, j)), -vpools.id((i, letter, l))])

    # S'il y a une transition de i à j pour une lettre de l'alphabet, alors i est un état
    # et j est un état
    for i in states:
        for letter in alphabet:
            for j in states:
                cnf.append(
                    [
                        -vpools.id((i, letter, j)),
                        vpools.id((i, acceptation[A])),
                        vpools.id((i, acceptation[NA])),
                    ]
                )
                cnf.append(
                    [
                        -vpools.id((i, letter, j)),
                        vpools.id((j, acceptation[A])),
                        vpools.id((j, acceptation[NA])),
                    ]
                )
    # Il faut que l’ensemble des mots positifs soient inclus dans l’ensemble des mots acceptés par l’automate
    for word in pos:
        if word == "":
            cnf.append([vpools.id((states[0], acceptation[A]))])
            cnf.append([-vpools.id((states[0], acceptation[NA]))])
        for idx, char in enumerate(word):
            for i in states:
                for j in states: 







# Q3
def gen_minaut(alphabet: str, pos: list[str], neg: list[str]) -> DFA:
    # À COMPLÉTER
    ...


# Q4
def gen_autc(alphabet: str, pos: list[str], neg: list[str], k: int) -> DFA:
    # À COMPLÉTER
    ...


# Q5
def gen_autr(alphabet: str, pos: list[str], neg: list[str], k: int) -> DFA:
    # À COMPLÉTER
    ...


# Q6
def gen_autcard(alphabet: str, pos: list[str], neg: list[str], k: int, ell: int) -> DFA:
    # À COMPLÉTER
    ...


# Q7
def gen_autn(alphabet: str, pos: list[str], neg: list[str], k: int) -> NFA:
    # À COMPLÉTER
    ...


def main():
    test_aut()
    test_minaut()
    test_autc()
    test_autr()
    test_autcard()
    test_autn()


if __name__ == "__main__":
    main()
