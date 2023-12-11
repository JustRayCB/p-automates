from utils import *
from mytests import *

from automata.fa.fa import FA
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA

from pysat.solvers import Minisat22, Minicard
from pysat.formula import CNF, CNFPlus, IDPool


def variable_names(alphabet: str, k: int, vpools, pos, neg) -> dict:
    states = [nb for nb in range(1, k + 1)]
    acceptation = ["acceptant", "non-acceptant"]  # 1:= Non-Acceptant, 2:= Acceptant
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

    # for word in pos:
    #     for t in range(len(word)):
    #         for i in states:
    #             variables[vpools.id((word, i, t))] = (
    #                 "Etat Q"
    #                 + str(i)
    #                 + " pour la lettre "
    #                 + word[t]
    #                 + "("
    #                 + str(t)
    #                 + ") sur le mot "
    #                 + word
    #                 + " positif"
    #             )

    # for word in neg:
    #     for t in range(len(word)):
    #         for i in states:
    #             variables[vpools.id((word, i, t))] = (
    #                 "Etat Q"
    #                 + str(i)
    #                 + " pour la lettre "
    #                 + word[t]
    #                 + "("
    #                 + str(t)
    #                 + ") sur le mot "
    #                 + word
    #                 + " (négatif)"
    #             )

    return variables


def gen_aut(alphabet: str, pos: list[str], neg: list[str], k: int) -> DFA:

    cnf = CNFPlus()
    vpools = IDPool(start_from=1)
    acceptant = ["acceptant", "non-acceptant"]
    states = [nb for nb in range(1, k + 1)]
    A = 0
    NA = 1
    varnames = variable_names(alphabet, k, vpools, pos, neg)
    # display keys and values
    for key, value in varnames.items():
        print(key, value)

    # Il y a un unique état initial
    cnf.append([vpools.id((states[0], acceptant[A])), vpools.id((states[0], acceptant[NA]))])

    # Un état est exclusivement acceptant ou non-acceptant
    for i in states:
        cnf.append(
            [
                -vpools.id((i, acceptant[A])),
                -vpools.id((i, acceptant[NA])),
            ]
        )

    # Chaque état est acceptant ou non-acceptant
    for i in states:
        cnf.append([vpools.id((i, acceptant[A])), vpools.id((i, acceptant[NA]))])

    # Il y a au moins un état acceptant
    # d = []
    # for i in states:
    #     d.append(vpools.id((i, acceptant[A])))
    # cnf.append(d)

    # Chaque état a au plus une transition par lettre de l'alphabet
    for i in states:
        for j in states:
            for k in states:
                for letter in alphabet:
                    if j != k:
                        cnf.append(
                            [
                                -vpools.id((i, letter, j)),
                                -vpools.id((i, letter, k)),
                            ]
                        )


    # S'il y a une transition pour la lettre l d'un état i à un état j, alors i et
    # j sont des états existants
    for i in states:
        for j in states:
            for letter in alphabet:
                cnf.append(
                    [
                        -vpools.id((i, letter, j)),
                        vpools.id((i, acceptant[A])),
                        vpools.id((i, acceptant[NA])),
                    ]
                )
                if i != j:
                    cnf.append(
                        [
                            -vpools.id((i, letter, j)),
                            vpools.id((j, acceptant[A])),
                            vpools.id((j, acceptant[NA])),
                        ]
                    )
    
    # Un état i est acceptant si et seulement s'il existe une exécution d'un mot m de P qui se termine 
    # sur i à l'étape t = len(m) - 1
    for word in pos:
        for i in states:
            if word != "":
                cnf.append([-vpools.id((word, i, len(word) - 1)), vpools.id((i, acceptant[A]))])
            else:
                cnf.append([vpools.id((states[0], acceptant[A]))])

    # Si on a une exécution pour le mot m à l'étape t sur l'état i et une transition de i vers j pour la lettre l,
    # alors, on a une exécution pour le mot m à l'étape t+1 sur l'état j.
    for word in pos:
        for t in range(len(word)-1):
            for i in states:
                for j in states:
                        cnf.append(
                            [
                                -vpools.id((word, i, t)),
                                -vpools.id((i, word[t+1], j)),
                                vpools.id((word, j, t + 1)),
                            ]
                        )

    # Si on a une exécution pour le mot m à l'étape t sur l'état i et une exécution pour le même mot m à l'étape t+1
    # sur l'état j, alors il existe une transition de i vers j pour la lettre l.
    for word in pos:
        for t in range(len(word)-1):
            for i in states:
                for j in states:
                        cnf.append(
                            [
                                -vpools.id((word, i, t)),
                                -vpools.id((word, j, t+1)),
                                vpools.id((i, word[t+1], j)),
                            ]
                        )
    # Toutes les exécutions de N doivent finir sur un état non-acceptant
    for word in neg:
        for i in states:
            if word != "":
                cnf.append([-vpools.id((word, i, len(word) - 1)), vpools.id((i, acceptant[NA]))])
            else:
                cnf.append([vpools.id((states[0], acceptant[NA]))])
    
    # Toutes les exécutions doivent commencer à l'état initial
    all_words = neg + pos
    for word in all_words:
        cnf.append([vpools.id((word, states[0], 0))])
    
    





    
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


t = ("a", ["", "aa", "aaaaaa"], ["a", "aaa", "aaaaa"], 2)
# t = ("ab", ["", "a", "aa", "aaa", "aaaa"], ["b", "ab", "ba", "bab", "aba"], 1)
# t = ("ab", ["b", "ab", "ba", "abbb", "abba"], ["", "aaa", "a", "aa"], 2)  #

gen_aut(t[0], t[1], t[2], t[3])