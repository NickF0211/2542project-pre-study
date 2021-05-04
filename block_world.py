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
    #bA, bB, bC, bD, bE, bF, bG, bH, bI, bJ = \
        #Block("A"), Block("B"), Block("C"), Block("D"), Block("E"), Block("F"), Block("G"), Block("H"), Block("I"),  Block("J")
    Blocks = ("A", "B", "C")
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
                     Select(get_clear, 0),
                     get_on], [lambda arg1, arg2: arg1 != arg2])

    create_action("unstack", [Blocks, Blocks], [get_on,
                                              get_empty,
                                                Select(get_clear, 0) ]
                  , [Select(get_holding, 0),
                     Select(get_clear, 1),
                     Fnot(Select(get_clear, 0)),
                     Fnot(get_empty),
                     Fnot(get_on)], [lambda arg1, arg2: arg1 != arg2])


    init = [proposition_lookup("clear", "C"),
            proposition_lookup("on-table", "A"),
            proposition_lookup("on", ["C", "B"]),
            proposition_lookup("on", ["B", "A"]),
            proposition_lookup("empty", [])]

    goal = [proposition_lookup("on", ["B", "C"]),
            proposition_lookup("on", ["A", "B"])]


    solver = solver(3, init, goal, 1)
    solver.interpolantion_solving_union()



    #print("Hi")