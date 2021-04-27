from z3 import *
def atMostOne(candidates):
    if candidates == []:
        return True
    else:
        head = candidates[0]
        rst = candidates[1:]
        return And(Implies(head, Not(Or(rst))), Implies(Not(head), atMostOne(rst)))