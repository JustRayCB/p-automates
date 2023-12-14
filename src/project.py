from utils import *
from typing import List

from mytests import *

from automata.fa.fa import FA
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA

from pysat.solvers import Minisat22, Minicard
from pysat.formula import CNF, CNFPlus, IDPool

cnf = CNFPlus()
vpool = IDPool(start_from=1)

states = []
ACCEPTING: List = ["acceptant", "non-acceptant"]
A = 0  # Accepting
NA = 1  # Non-Accepting

q_a = lambda i: vpool.id((i, ACCEPTING[A]))  # Give the Accepting state an ID
q_na = lambda i: vpool.id((i, ACCEPTING[NA]))  # Give the Non-Accepting state an ID
d = lambda i, letter, j: vpool.id(
    (i, letter, j)
)  # Give the transition from i to j with letter an ID
e = lambda word, q, idx: vpool.id(
    (word, q, idx)
)  # Give the execution of a word that is on a state q at index idx of the word


# 1
def one_initial_state():
    """There is one and only one initial state which is Q_1."""
    global cnf, states
    cnf.append([q_a(states[0]), q_na(states[0])])


# 2
def exclusively_a_na():
    """Each state is accepting xor non-accepting."""
    global cnf, states
    for i in states:
        cnf.append([-q_a(i), -q_na(i)])


# 4
def at_most_one_transition_per_letter(alphabet: str):
    """Each state has at most one transition per letter of the alphabet."""
    global cnf, states
    for i in states:
        for j in states:
            for k in states:
                for letter in alphabet:
                    if j != k:
                        # If there is a transition from i to j with letter and a there should not
                        # be another transition from i with the same letter
                        cnf.append([-d(i, letter, j), -d(i, letter, k)])


# 6
def accepting_positive_examples(pos: list[str]):
    """Each state i is accepting if there is a final execution on i of a word form positive set."""
    global cnf, states
    for word in pos:
        for i in states:
            if word != "":
                cnf.append(
                    [-e(word, i, len(word)), q_a(i)]
                )  # if there is a final execution on i, i should be accepting
            else:
                cnf.append([q_a(states[0])])  # 0 should accept the empty word


# 7
def exec_and_transition_implies_next_exec(words: list[str]):
    """
    If there is an execution for the word m at step t on state i and a transition from i to j for letter l,
    then there is an execution for the word m at step t+1 on state j.
    """
    global cnf, states
    for word in words:
        for t in range(len(word)):
            for i in states:
                for j in states:
                    cnf.append(
                        [
                            -e(word, i, t),
                            -d(i, word[t], j),
                            e(word, j, t + 1),
                        ]
                    )


# 8
def executions_implies_transition(pos: list[str]):
    """
    If there is an execution for the word m at step t on state i and an execution for the same word m at step t+1
    on state j, then there is a transition from i to j for letter l.
    """
    global cnf, states
    for word in pos:
        for t in range(len(word)):
            for i in states:
                for j in states:
                    cnf.append(
                        [
                            -e(word, i, t),
                            -e(word, j, t + 1),
                            d(i, word[t], j),
                        ]
                        # execution on i at t and execution on j at t+1 implies a transition from i to j
                    )


# 9
def reject_non_positive_example(neg: list[str]):
    """Each executions (if there is ) of a negative word should finish on a non-accepting state."""
    global cnf, states
    for word in neg:
        for i in states:
            if word != "":
                cnf.append(
                    [-e(word, i, len(word)), q_na(i)]
                )  # if there is a final execution on i, i should be non-accepting
            else:
                cnf.append([q_na(states[0])])  # 0 should reject the empty word


# 10
def all_executions_start_from_initial_state(words: list[str]):
    """All executions start from the initial state."""
    global cnf, states
    for word in words:
        cnf.append([e(word, states[0], 0)])


# 11
def all_positive_exec_must_exist(pos: list[str]):
    """All executions on positive words must exist."""
    global cnf, states
    for word in pos:
        for t in range(len(word)):
            d = []  # disjonction
            for i in states:
                d.append(e(word, i, t + 1))
            cnf.append(d)


def complete_automaton(alphabet: str):
    """At least one transition per letter for each state."""
    global states
    for i in states:
        for letter in alphabet:
            disj = []
            for j in states:
                disj.append(d(i, letter, j))  # Transition de i vers j avec la lettre letter
            cnf.append(disj)


def reversible_automaton(alphabet: str):
    """There should not be two transitions from two different states to the same state with the same letter."""
    global states
    for letter in alphabet:
        for i in states:
            for j in states:
                for q in states:
                    if q != i:
                        cnf.append([-d(i, letter, j), -d(q, letter, j)])
                        # If there is a transition from i to j with letter and a there should not
                        # be another transition from a state to j with the same letter


def params_to_cnf(alphabet: str, pos: list[str], neg: list[str], k: int):
    """Build a CNF with the given parameters. The cnf should reprensents a DFA."""
    global cnf, states
    cnf = CNFPlus()
    states = [i for i in range(1, k + 1)]
    one_initial_state()
    exclusively_a_na()
    at_most_one_transition_per_letter(alphabet)
    accepting_positive_examples(pos)
    exec_and_transition_implies_next_exec(pos + neg)
    executions_implies_transition(pos)
    reject_non_positive_example(neg)
    all_executions_start_from_initial_state(pos + neg)
    all_positive_exec_must_exist(pos)


def build_dfa(alphabet, model) -> DFA | None:
    """Build dfa from solution model given by theh SAT solver."""
    global states, vpool
    if model is None:
        return None
    states_dfa = set()
    final = set()
    symbols = set(alphabet)
    initial = "q" + str(states[0])
    transit = dict()
    # Stats that should be in the automaton
    for i in states:
        if q_a(i) in model:
            final.add("q" + str(i))
            states_dfa.add("q" + str(i))
        if q_na(i) in model:
            states_dfa.add("q" + str(i))

    # Transitions of the automaton
    for i in states:
        s = "q" + str(i)
        transit[s] = dict()
        for letter in alphabet:
            for j in states:
                if d(i, letter, j) in model:
                    transit[s][letter] = "q" + str(j)

    dfa = DFA(
        states=states_dfa,
        input_symbols=symbols,
        transitions=transit,
        initial_state=initial,
        final_states=final,
        allow_partial=True,
    )
    return dfa


def get_model():
    """Solve the CNF with the SAT solver and return the model."""
    global cnf
    solver = Minisat22()
    solver.append_formula(cnf.clauses, no_return=False)
    _ = solver.solve()
    model = solver.get_model()
    return model


# Q2
def gen_aut(alphabet: str, pos: list[str], neg: list[str], k: int) -> DFA | None:
    params_to_cnf(alphabet, pos, neg, k)
    model = get_model()
    return build_dfa(alphabet, model)


# Q3
def gen_minaut(alphabet: str, pos: list[str], neg: list[str]) -> DFA | None:
    found = False
    e = 0
    low = 2**e
    high = 2 ** (e + 1)
    model = None
    while not found:
        params_to_cnf(alphabet, pos, neg, high)
        if get_model():
            found = True
        else:
            e += 1
            low = high
            high = 2 ** (e + 1)
    # Binary search between 2^(k-1) and 2^k
    while low < high - 1:
        mid = (low + high) // 2
        params_to_cnf(alphabet, pos, neg, mid)
        model = get_model()
        if model:
            high = mid
        else:
            low = mid
    if model is None:
        # The upper bound is the k
        params_to_cnf(alphabet, pos, neg, high)
        model = get_model()
    return build_dfa(alphabet, model)


# Q4
def gen_autc(alphabet: str, pos: list[str], neg: list[str], k: int) -> DFA | None:
    params_to_cnf(alphabet, pos, neg, k)
    complete_automaton(alphabet)
    model = get_model()
    return build_dfa(alphabet, model)


# Q5
def gen_autr(alphabet: str, pos: list[str], neg: list[str], k: int) -> DFA | None:
    global states
    params_to_cnf(alphabet, pos, neg, k)
    reversible_automaton(alphabet)
    model = get_model()
    return build_dfa(alphabet, model)


# Q6
def gen_autcard(alphabet: str, pos: list[str], neg: list[str], k: int, ell: int) -> DFA | None:
    global states
    params_to_cnf(alphabet, pos, neg, k)
    complete_automaton(alphabet)
    # Au plus ell acceptant
    solver = Minicard()
    solver.append_formula(cnf.clauses, no_return=False)
    solver.add_atmost([q_a(i) for i in states], ell, no_return=False)
    _ = solver.solve()
    model = solver.get_model()
    return build_dfa(alphabet, model)


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
    # test_autn()


if __name__ == "__main__":
    main()
