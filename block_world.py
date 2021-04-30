from problem_domain import *
from Solver import *


class Block():
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "Block_{}".format(self.name)

    def __repr__(self):
        return self.__str__()



if __name__ == "__main__":
    bA, bB, bC, bD, bE, bF, bG, bH, bI, bJ = \
        Block("A"), Block("B"), Block("C"), Block("D"), Block("E"), Block("F"), Block("G"), Block("H"), Block("I"),  Block("J")
    Blocks = (bA, bB, bC, bD, bE, bF, bG, bH, bI, bJ)
    create_proposition("on", [Blocks, Blocks], [lambda arg1, arg2: arg1 != arg2])
    create_proposition("on-table", [Blocks])
    create_proposition("holding", [Blocks])
    create_proposition("clear", [Blocks])
    create_proposition("empty", [])
    get_clear = lambda block: proposition_lookup("clear", block)
    get_on_table = lambda block: proposition_lookup("on-table", block)
    get_holding = lambda block : proposition_lookup("holding", block)
    get_empty = lambda block: proposition_lookup("empty", [])
    get_on = lambda blocks: proposition_lookup("on", blocks)
    create_action("pick-up", [Blocks], [get_clear,
                                        get_on_table,
                                        get_empty]
                                     , [Fnot(get_on_table),
                                        Fnot(get_clear),
                                        Fnot(get_empty),
                                        get_holding])

    create_action("put-down", [Blocks], [get_holding]
                  , [Fnot(get_holding),
                     get_clear,
                     get_empty,
                     get_on_table])

    create_action("stack", [Blocks, Blocks], [Select(get_holding, 0),
                                              Select(get_clear, 1)]
                  , [Fnot(Select(get_holding, 0)),
                     Fnot(Select(get_clear, 1)),
                     get_empty,
                     get_on], [lambda arg1, arg2: arg1 != arg2])

    create_action("unstack", [Blocks, Blocks], [get_on,
                                              get_empty,
                                                Select(get_clear, 0) ]
                  , [Select(get_holding, 0),
                     Select(get_clear, 1),
                     Fnot(Select(get_clear, 0)),
                     Fnot(get_empty),
                     Fnot(get_on)], [lambda arg1, arg2: arg1 != arg2])


    init = [proposition_lookup("clear", [bC]),
            proposition_lookup("clear", [bF]),
            proposition_lookup("on-table", [bI]),
            proposition_lookup("on-table", [bF]),
            proposition_lookup("on", [bC, bE]),
            proposition_lookup("on", [bE, bJ]),
            proposition_lookup("on", [bJ, bB]),
            proposition_lookup("on", [bB, bG]),
            proposition_lookup("on", [bG, bH]),
            proposition_lookup("on", [bH, bA]),
            proposition_lookup("on", [bA, bD]),
            proposition_lookup("on", [bD, bI]),
            proposition_lookup("empty", [])]

    goal = [proposition_lookup("on", [bD, bC]),
            proposition_lookup("on", [bC, bF]),
            proposition_lookup("on", [bF, bJ]),
            proposition_lookup("on", [bJ, bE]),
            proposition_lookup("on", [bE, bH]),
            proposition_lookup("on", [bH, bB]),
            proposition_lookup("on", [bB, bA]),
            proposition_lookup("on", [bA, bG]),
            proposition_lookup("on", [bG, bI])]


    solver = solver(100, init, goal, 1)
    res = solver.solve()
    if res:
        print("hi")
    else:
        print("not yet")


    #print("Hi")