from automata.fa.dfa import DFA
from project import gen_aut
from utils import show_automaton

# DFA which matches all binary strings ending in an odd number of '1's
# dfa = DFA(
#     states={"q0", "q1", "q2"},
#     input_symbols={"0", "1"},
#     transitions={
#         "q0": {"0": "q0", "1": "q1"},
#         "q1": {"0": "q0", "1": "q2"},
#         "q2": {"0": "q2", "1": "q1"},
#     },
#     initial_state="q0",
#     final_states={"q1"},
# )
#
# show_automaton(dfa)
t = ("a", ["", "aa", "aaaaaa"], ["a", "aaa", "aaaaa"], 2)

gen_aut(t[0], t[1], t[2], t[3])
