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
    initial = ["non-initial", "initial"]  # 1:= Pas Initial, 2:= Initial
    variables = dict()
    for i in states:
        for accept in acceptation:
            for init in initial:
                variables[vpools.id((i, accept, init))] = "Q" + str(i) + " " + accept + " " + init

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
    initial = ["non-initial", "initial"]  # 1:= Pas Initial, 2:= Initial
    NAOI = 0  # Non Acceptant et Non Initial
    AOI = 1  # Acceptant et Initial
    nb_transition = len(alphabet)
    varnames = variable_names(alphabet, k, vpools)
    # display keys and values
    for key, value in varnames.items():
        print(key, value)

    # On assume que l'état 0 est initial est toujours dans l'automate
    # Soit l'état 0 est acceptant, soit il ne l'est pas mais dans tous les cas il est présent
    cnf.append(
        [
            vpools.id(
                (states[0], acceptation[NAOI], initial[AOI])
            ),  # Etat 1 is not Accept and INIT
            vpools.id((states[0], acceptation[AOI], initial[AOI])),  # Or accept and INIT
        ]
    )

    # Il n'existe qu'un seul état initial
    for k in states[1:]:
        for accept in acceptation:
            # Seul l'état 0 peut être initial
            cnf.append([-vpools.id((k, accept, initial[AOI]))])

    # Il existe au moins un état acceptant
    d = []
    for k in states:
        if k != 1:
            d.append(vpools.id((k, acceptation[AOI], initial[NAOI])))
    print(d)
    d.append(vpools.id((states[0], acceptation[AOI], initial[AOI])))
    cnf.append(d)
    # Chaque état doit avoir toutes les transitions possibles (automate complet)
    for i in states:
        for letter in alphabet:
            d = []
            for j in states:
                d.append(vpools.id((i, letter, j)))  # Transition de i vers j avec la lettre letter
            cnf.append(d)

    # Si un état est acceptant et initial alors il n'est pas non acceptant et non initial et
    # il n'est pas non acceptant et initial et il n'est pas acceptant et non initial
    for i in states:
        for accept in acceptation:
            for init in initial:
                for accept2 in acceptation:
                    for init2 in initial:
                        # if (init != "non-initial" or init2 != "non-initial") and i != 1:
                        if init == "non-initial" and i == 1:
                            continue
                        elif accept != accept2 or init != init2:
                            cnf.append(
                                [
                                    -vpools.id((i, accept, init)),
                                    -vpools.id((i, accept2, init2)),
                                ]
                            )

    # Chaque état doit avoir au plus 1 transition pour chaque lettre de l'alphabet
    for i in states:
        for letter in alphabet:
            for j in states:
                for l in states:
                    # Si i va vers j avec la lettre letter alors i ne peut pas aller vers l avec la lettre letter
                    if j != l:
                        cnf.append([-vpools.id((i, letter, j)), -vpools.id((i, letter, l))])

    # Il faut que l’ensemble des mots positifs soient inclus dans l’ensemble des mots acceptés par l’automate
    print(cnf.clauses)
    print("Before starting transitions : ", len(cnf.clauses))
    for word in pos:
        idx = 0
        size = len(word)
        if word == "":
            # Si le mot est vide alors l'état 0 doit être acceptant
            cnf.append([vpools.id((states[0], acceptation[AOI], initial[AOI]))])
            cnf.append([-vpools.id((states[0], acceptation[NAOI], initial[AOI]))])
        for char in word:
            if char not in alphabet:
                raise Exception(
                    "Le mot contient un caractère qui n'est pas dans l'alphabet : ", char
                )
            if idx == 0:
                # Si c'est le premier caractère du mot alors l'état 0 doit aller vers un état avec la lettre char
                for j in states:
                    if idx == size - 1:
                        # Si c'est le dernier caractère du mot alors l'état de la transition doit être acceptant
                        for init in initial:
                            if j == 1 and init == "non-initial":
                                continue
                            elif init == "initial" and j != 1:
                                continue
                            else:
                                cnf.append(
                                    [
                                        -vpools.id((states[0], char, j)),
                                        vpools.id((j, acceptation[AOI], init)),
                                    ]
                                )
                    else:
                        # Sinon l'état de la transition doit être non acceptant
                        for init in initial:
                            if j == 1 and init == "non-initial":
                                continue
                            elif init == "initial" and j != 1:
                                continue
                            else:
                                cnf.append(
                                    [
                                        -vpools.id((states[0], char, j)),
                                        vpools.id((j, acceptation[NAOI], init)),
                                    ]
                                )
                print("Find first char ", len(cnf.clauses))
                print(cnf.clauses)
            else:
                for j in states:
                    if idx == size - 1:
                        for l in states:
                            # Si l'état j va vers l avec la lettre char alors l'état l doit être acceptant et non initial
                            for init in initial:
                                if l == 1 and init == "non-initial":
                                    continue
                                elif init == "initial" and l != 1:
                                    continue
                                else:
                                    cnf.append(
                                        [
                                            -vpools.id((j, char, l)),
                                            vpools.id((l, acceptation[AOI], init)),
                                        ]
                                    )
                    else:
                        for l in states:
                            for init in initial:
                                # S'il existe un état j qui va vers l avec la lettre char alors l'état j doit être dans l'automate étant non acceptant et non initial
                                if l == 1 and init == "non-initial":
                                    continue
                                elif init == "initial" and l != 1:
                                    continue
                                else:
                                    cnf.append(
                                        [
                                            -vpools.id((j, char, l)),
                                            vpools.id((l, acceptation[NAOI], init)),
                                        ]
                                    )
            idx += 1
        print("End of the word : ", word, " := ", len(cnf.clauses))
        print(cnf.clauses)

    print("============after first part transitions : ", len(cnf.clauses), "==========")
    print(cnf.clauses)
    print("===================")

    # Il faut que l’ensemble des mots négatif ne soit pas inclus dans l’ensemble des mots acceptés par l’automate
    for word in neg:
        idx = 0
        size = len(word)
        if word == "":
            # Si le mot est vide alors l'état 0 ne doit pas être acceptant
            cnf.append([-vpools.id((states[0], acceptation[AOI], initial[AOI]))])
            cnf.append([vpools.id((states[0], acceptation[NAOI], initial[AOI]))])
        for char in word:
            if word[: idx + 1] in pos:
                continue
            else:
                # Si c'est le premier caractère du mot alors l'état 0 doit aller vers un état avec la lettre char
                if idx == 0:
                    for j in states:
                        if idx == size - 1:
                            # Si c'est le dernier caractère du mot alors l'état de la transition doit être non acceptant
                            for init in initial:
                                if j == 1 and init == "non-initial":
                                    continue
                                elif init == "initial" and j != 1:
                                    continue
                                else:
                                    cnf.append(
                                        [
                                            -vpools.id((states[0], char, j)),
                                            vpools.id((j, acceptation[NAOI], init)),
                                        ]
                                    )
                        else:
                            # Sinon l'état de la transition doit être non acceptant
                            for init in initial:
                                if j == 1 and init == "non-initial":
                                    continue
                                elif init == "initial" and j != 1:
                                    continue
                                else:
                                    cnf.append(
                                        [
                                            -vpools.id((states[0], char, j)),
                                            vpools.id((j, acceptation[NAOI], init)),
                                        ]
                                    )
                else:
                    for j in states:
                        if idx == size - 1:
                            for l in states:
                                # Si l'état j va vers l avec la lettre char alors l'état l doit être non acceptant et non initial
                                for init in initial:
                                    if l == 1 and init == "non-initial":
                                        continue
                                    elif init == "initial" and l != 1:
                                        continue
                                    else:
                                        cnf.append(
                                            [
                                                -vpools.id((j, char, l)),
                                                vpools.id((l, acceptation[NAOI], init)),
                                            ]
                                        )
                        else:
                            for l in states:
                                for init in initial:
                                    # S'il existe un état j qui va vers l avec la lettre char alors l'état j doit être dans l'automate étant non acceptant et non initial
                                    if l == 1 and init == "non-initial":
                                        continue
                                    elif init == "initial" and l != 1:
                                        continue
                                    else:
                                        cnf.append(
                                            [
                                                -vpools.id((j, char, l)),
                                                vpools.id((l, acceptation[NAOI], init)),
                                            ]
                                        )

            idx += 1

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
    for i in states:
        for a in acceptation:
            for init in initial:
                if vpools.id((i, a, init)) in model:
                    print("Q" + str(i) + " " + a + " " + init)
    for i in states:
        for letter in alphabet:
            for j in states:
                if vpools.id((i, letter, j)) in model:
                    print("Q" + str(i) + " -" + letter + "-> Q" + str(j))
    return None


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
