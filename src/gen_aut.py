from typing import List, Tuple
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


def _gen_aut(alphabet: str, pos: list[str], neg: list[str], k: int) -> Tuple[List | None, IDPool]:
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

    # 1. Il y a un unique état initial
    cnf.append([vpools.id((states[0], acceptant[A])), vpools.id((states[0], acceptant[NA]))])

    # 2. Un état est exclusivement acceptant ou non-acceptant
    for i in states:
        cnf.append(
            [
                -vpools.id((i, acceptant[A])),
                -vpools.id((i, acceptant[NA])),
            ]
        )

    # 3. Chaque état est acceptant ou non-acceptant
    for i in states:
        cnf.append([vpools.id((i, acceptant[A])), vpools.id((i, acceptant[NA]))])

    # 4. Chaque état a au plus une transition par lettre de l'alphabet
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

    # 5. S'il y a une transition pour la lettre l d'un état i à un état j, alors i et
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

    # 6. Un état i est acceptant si et seulement s'il existe une exécution d'un mot m de P qui se termine
    # sur i à l'étape t = len(m) - 1
    for word in pos:
        for i in states:
            if word != "":
                cnf.append([-vpools.id((word, i, len(word) - 1)), vpools.id((i, acceptant[A]))])
            else:
                cnf.append([vpools.id((states[0], acceptant[A]))])

    # 7. Si on a une exécution pour le mot m à l'étape t sur l'état i et une transition de i vers j pour la lettre l,
    # alors, on a une exécution pour le mot m à l'étape t+1 sur l'état j.
    # ------------------------ PAS SSI ------------------------
    # for word in pos:
    #     for t in range(len(word)):
    #         for i in states:
    #             for j in states:
    #                     cnf.append(
    #                         [
    #                             -vpools.id((word, i, t-1)),
    #                             -vpools.id((i, word[t], j)),
    #                             vpools.id((word, j, t)),
    #                         ]
    #                     )

    # ------------------------ SSI ------------------------
    for word in pos:
        for t in range(len(word)):
            for i in states:
                for j in states:
                    cnf.append(
                        [
                            -vpools.id((word, i, t - 1)),
                            -vpools.id((i, word[t], j)),
                            vpools.id((word, j, t)),
                        ]
                    )
                    cnf.append(
                        [
                            -vpools.id((word, j, t)),
                            -vpools.id((word, i, t - 1)),
                        ]
                    )
                    cnf.append(
                        [
                            -vpools.id((word, j, t)),
                            vpools.id((i, word[t], j)),
                        ]
                    )

    # 8. Si on a une exécution pour le mot m à l'étape t sur l'état i et une exécution pour le même mot m à l'étape t+1
    # sur l'état j, alors il existe une transition de i vers j pour la lettre l.
    # ------------------------ PAS SSI ------------------------
    for word in pos:
        for t in range(len(word)):
            for i in states:
                for j in states:
                    cnf.append(
                        [
                            -vpools.id((word, i, t - 1)),
                            -vpools.id((word, j, t)),
                            vpools.id((i, word[t], j)),
                        ]
                    )
                    cnf.append(
                        [
                            -vpools.id((i, word[t], j)),
                            vpools.id((word, i, t - 1)),
                        ]
                    )
                    cnf.append(
                        [
                            -vpools.id((i, word[t], j)),
                            vpools.id((word, j, t)),
                        ]
                    )

    # ------------------------ SSI ------------------------
    # for word in pos:
    #     for t in range(len(word)):
    #         for i in states:
    #             for j in states:
    #                     cnf.append(
    #                         [
    #                             -vpools.id((word, i, t-1)),
    #                             -vpools.id((word, j, t)),
    #                             vpools.id((i, word[t], j)),
    #                         ]
    #                     )

    # 9. Toutes les exécutions de N doivent finir sur un état non-acceptant
    for word in neg:
        for i in states:
            if word != "":
                cnf.append([-vpools.id((word, i, len(word) - 1)), vpools.id((i, acceptant[NA]))])
            else:
                cnf.append([vpools.id((states[0], acceptant[NA]))])

    # 10. Toutes les exécutions doivent commencer à l'état initial
    all_words = neg + pos
    for word in all_words:
        cnf.append([vpools.id((word, states[0], -1))])

    # 11. Toutes les exécutions sur P doivent exister
    for word in pos:
        for t in range(len(word)):
            d = []
            for i in states:
                d.append(vpools.id((word, i, t - 1)))
            cnf.append(d)

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
    return model, vpools


def gen_aut(alphabet: str, pos: list[str], neg: list[str], k: int) -> DFA | None:
    acceptation = ["acceptant", "non-acceptant"]  # 1:= Non-Acceptant, 2:= Acceptant
    states = [nb for nb in range(1, k + 1)]
    A = 0
    NA = 1
    model, vpools = _gen_aut(alphabet, pos, neg, k)
    if model is None:
        return None
    states_dfa = set()
    final = set()
    initial = "q" + str(states[0])
    transit = dict()
    symbols = set(alphabet)
    for state in states:
        for accept in acceptation:
            if vpools.id((state, accept)) in model:
                if accept == acceptation[A]:
                    final.add("q" + str(state))
                states_dfa.add("q" + str(state))

    for i in states:
        s = "q" + str(i)
        transit[s] = dict()
        for letter in alphabet:
            for j in states:
                if vpools.id((i, letter, j)) in model:
                    transit[s][letter] = "q" + str(j)

    dfa = DFA(
        states=states_dfa,
        input_symbols=symbols,
        transitions=transit,
        initial_state=initial,
        final_states=final,
    )
    return dfa


t = ("a", ["", "aa", "aaaaaa"], ["a", "aaa", "aaaaa"], 2)
# t = ("ab", ["", "a", "aa", "aaa", "aaaa"], ["b", "ab", "ba", "bab", "aba"], 1)
# t = ("ab", ["b", "ab", "ba", "abbb", "abba"], ["", "aaa", "a", "aa"], 2)  #

dfa = gen_aut(t[0], t[1], t[2], t[3])
if dfa is not None:
    show_automaton(dfa)
else:
    print("NOPE")
# gen_aut(t[0], t[1], t[2], t[3])
