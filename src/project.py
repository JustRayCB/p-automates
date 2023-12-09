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
                    + "positif"
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
    varnames = variable_names(alphabet, k, vpools, pos, neg)
    # display keys and values
    for key, value in varnames.items():
        print(key, value)

    # 1 et 1 seul état initial
    cnf.append([vpools.id((states[0], acceptation[NA])), vpools.id((states[0], acceptation[A]))])

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
                if i != j:
                    cnf.append(
                        [
                            -vpools.id((i, letter, j)),
                            vpools.id((j, acceptation[A])),
                            vpools.id((j, acceptation[NA])),
                        ]
                    )
    for word in pos:
        for j in states:
            if word != "":
                cnf.append([-vpools.id((word, j, len(word) - 1)), vpools.id((j, acceptation[A]))])
    #
    # Il faut que l’ensemble des mots positifs soient inclus dans l’ensemble des mots acceptés par l’automate
    for word in pos:
        if word == "":
            cnf.append([vpools.id((states[0], acceptation[A]))])
            cnf.append([-vpools.id((states[0], acceptation[NA]))])
        for t in range(len(word) - 1):
            for i in states:
                for j in states:
                    # ¬ X(m, i, j, t+1) ∨ d(i, m[t+1], j)
                    cnf.append([-vpools.id((word, i, j, t + 1), vpools.id((i, word[t + 1], j)))])
                    # ¬ d(i, m[t+1], j) ∨ X(m, i, j, t+1)
                    cnf.append([vpools.id((word, i, j, t + 1), -vpools.id((i, word[t + 1], j)))])
                    # ¬ X(m, i, j, t+1) ∨ E(m, i, t)
                    cnf.append([-vpools.id((word, i, j, t + 1), vpools.id((word, i, t)))])
                    # ¬ X(m, i, j, t+1) ∨ E(m, j, t+1)
                    cnf.append([-vpools.id((word, i, j, t + 1), vpools.id((word, j, t + 1)))])
                    # ¬ E(m, i, t) ∨ ¬ E(m, j, t+1) ∨ X(m, i, j, t+1)
                    cnf.append(
                        [
                            -vpools.id((word, i, t)),
                            -vpools.id((word, j, t + 1)),
                            vpools.id((word, i, j, t + 1)),
                        ]
                    )

    # Toutes les exécutions pour les mots positifs doivent exister
    for word in pos:
        # Eijt,
        for t in range(len(word)):
            d = []
            for j in states:
                d.append(vpools.id((word, j, t)))
            cnf.append(d)

    # # Il faut que l’ensemble des mots négatifs soient exclus de l’ensemble des mots acceptés par l’automate
    for word in neg:
        if word == "":
            cnf.append([vpools.id((states[0], acceptation[NA]))])
            cnf.append([-vpools.id((states[0], acceptation[A]))])
        for t in range(len(word)):
            for i in states:
                for j in states:
                    cnf.append([-vpools.id((word, i, t)), vpools.id((j, word[t], i))])
                cnf.append([-vpools.id((word, i, len(word) - 1)), vpools.id((i, acceptation[NA]))])

    print("Clauses construites:\n", len(cnf.clauses))
    print(cnf.clauses)  # pour afficher les clauses
    print("\n")
    # On résout le problème SAT
    solver = Minisat22()
    solver.append_formula(cnf.clauses, no_return=False)
    print("Resolution...")
    resultat = solver.solve()
    print("satisfaisable : " + str(resultat))
    print("\n")
    print("Interpretation :")
    model = solver.get_model()
    print(model)
    # for i in states:
    #     for accept in acceptation:
    #         if vpools.id((i, accept)) in model:
    #             print("Q" + str(i) + " " + accept + " : ")

    # return None


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
