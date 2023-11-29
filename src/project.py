from utils import *
from mytests import *

from automata.fa.fa import FA
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA

from pysat.solvers import Minisat22, Minicard
from pysat.formula import CNF, CNFPlus, IDPool


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
    acceptation = [1, 2]  # 1:= Non-Acceptant, 2:= Acceptant
    initial = [1, 2]  # 1:= Pas Initial, 2:= Initial
    nb_transition = len(alphabet)

    # On assume que l'état 0 est initial est toujours dans l'automate
    # Soit l'état 0 est acceptant, soit il ne l'est pas mais dans tous les cas il est présent
    cnf.append([vpools.id((1, 1, 1)), vpools.id((1, 2, 1))])

    # Il n'existe qu'un seul état initial
    for k in range(2, k + 1):
        for accept in acceptation:
            # Seul l'état 0 peut être initial
            cnf.append([-vpools.id((k, accept, 1))])

    # Il existe au moins un état acceptant
    d = []
    for k in range(1, k + 1):
        d.append(vpools.id((k, 2, 1)))
    cnf.append(d)
    # Chaque état doit avoir toutes les transitions possibles (automate complet)
    for i in range(1, k + 1):
        for letter in alphabet:
            d = []
            for j in range(1, k + 1):
                d.append(vpools.id((i, letter, j)))  # Transition de i vers j avec la lettre letter
            cnf.append(d)

    # Chaque état doit avoir au plus 1 transition pour chaque lettre de l'alphabet
    for i in range(1, k + 1):
        for letter in alphabet:
            for j in range(1, k + 1):
                for l in range(j + 1, k + 1):
                    # Si i va vers j avec la lettre letter alors i ne peut pas aller vers l avec la lettre letter
                    cnf.append([-vpools.id((i, letter, j)), -vpools.id((i, letter, l))])

    # Il faut que l’ensemble des mots positifs soit inclus dans l’ensemble des mots acceptés par l’automate


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
