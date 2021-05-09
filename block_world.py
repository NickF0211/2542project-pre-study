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
    pl = proposition_lookup
    #bA, bB, bC, bD, bE, bF, bG, bH, bI, bJ = \
        #Block("A"), Block("B"), Block("C"), Block("D"), Block("E"), Block("F"), Block("G"), Block("H"), Block("I"),  Block("J")
    Blocks = range(10)
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

    init = [pl("clear", [0]),
            pl("on-table", [9]),
            pl("on", [0, 1]),
            pl("on", [1, 2]),
            pl("on", [2, 3]),
            pl("on", [3, 4]),
            pl("on", [4, 5]),
            pl("on", [5, 6]),
            pl("on", [6, 7]),
            pl("on", [7, 8]),
            pl("on", [8, 9]),
            proposition_lookup("empty", [])]



    goal = [proposition_lookup("on", [4, 3]),
            proposition_lookup("on", [3, 1]),
            proposition_lookup("on", [1, 2]),
            proposition_lookup("on", [2, 0]),
            proposition_lookup("on", [5, 4]),
            proposition_lookup("on", [6, 5]),
            proposition_lookup("on", [7, 6]),
            proposition_lookup("on", [8, 7]),
            proposition_lookup("on", [9, 8]),

            ]

    mutexes = []
    for b1 in Blocks:
        l_mutex = []
        for b2 in Blocks:
            prop = pl("on", [b1, b2])
            if prop is not None:
                l_mutex.append(prop)
        l_mutex.append(pl("on-table", [b1]))

        mutexes.append(l_mutex)

    for b2 in Blocks:
        l_mutex = []
        for b1 in Blocks:
            prop = pl("on", [b1, b2])
            if prop is not None:
                l_mutex.append(prop)
        l_mutex.append(pl("clear", [b2]))

        mutexes.append(l_mutex)

    inv = [Or([pl("on-table", [b]).get_base_var() for b in Blocks])]

    solver = solver(3, init, goal, split=1)
    #solver.interpolantion_solving_union()
    start = time.time()
    solver.interpolantion_solving_union()
    print(time.time() - start)


    #print("Hi")