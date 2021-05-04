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
    Blocks = ("A", "B", "C", "D" ,"E", "F", "G", "H", "I", "J")
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

    init = [pl("clear", "C"),
            pl("clear", "F"),
            pl("on-table", "I"),
            pl("on-table", "F"),
            pl("on", ["C", "E"]),
            pl("on", ["E", "J"]),
            pl("on", ["J", "B"]),
            pl("on", ["B", "G"]),
            pl("on", ["G", "H"]),
            pl("on", ["H", "A"]),
            pl("on", ["A", "D"]),
            pl("on", ["D", "I"]),
            proposition_lookup("empty", [])]



    goal = [proposition_lookup("on", ["D", "C"]),
            proposition_lookup("on", ["C", "F"]),
            proposition_lookup("on", ["F", "J"]),
            proposition_lookup("on", ["J", "E"]),
            proposition_lookup("on", ["E", "H"]),
            proposition_lookup("on", ["H", "B"]),
            proposition_lookup("on", ["B", "A"]),
            proposition_lookup("on", ["A", "G"]),
            proposition_lookup("on", ["G", "I"]),
            reverse(proposition_lookup("on-table", ["D"])),
            reverse(proposition_lookup("on-table", ["C"])),
            reverse(proposition_lookup("on-table", ["F"])),
            reverse(proposition_lookup("on-table", ["J"])),
            reverse(proposition_lookup("on-table", ["E"])),
            reverse(proposition_lookup("on-table", ["H"])),
            reverse(proposition_lookup("on-table", ["B"])),
            reverse(proposition_lookup("on-table", ["A"])),
            reverse(proposition_lookup("on-table", ["G"]))]

    mutexes = []
    for b1 in Blocks:
        l_mutex = []
        for b2 in Blocks:
            prop = pl("on", [b1, b2])
            if prop is not None:
                l_mutex.append(prop)
        l_mutex.append(pl("on-table", b1))

        mutexes.append(l_mutex)

    for b2 in Blocks:
        l_mutex = []
        for b1 in Blocks:
            prop = pl("on", [b1, b2])
            if prop is not None:
                l_mutex.append(prop)
        l_mutex.append(pl("clear", b2))

        mutexes.append(l_mutex)

    solver = solver(3, init, goal, mutexes=mutexes, split=1)
    solver.interpolantion_solving()



    #print("Hi")