from Solver import *

if __name__ == "__main__":
    Room = range(4)
    next_to_other = lambda a, b: a - b == 1 or b -a == 1
    create_proposition("at", [Room])
    create_proposition("has-key", [Room])
    create_proposition("unlocked", [Room, Room], [next_to_other])
    get_at = lambda room: proposition_lookup("at", room)
    get_has_key = lambda room: proposition_lookup("has-key", room)
    get_unlocked = lambda room : proposition_lookup("unlocked", room)
    get_on = lambda blocks: proposition_lookup("on", blocks)
    at_0 = lambda room: proposition_lookup("at", [0])
    create_action("move", [Room, Room], [Select(get_at, 0),
                                        get_unlocked ]
                                     , [Fnot(Select(get_at, 0)),
                                        Select(get_at, 1)], constraints=[next_to_other])

    create_action("unlock", [Room, Room], [Select(get_at, 0),
                                           Select(get_has_key, 1)]
                  , [get_unlocked,
                     Re_Order(get_unlocked, [1,0])
                     ], constraints=[next_to_other])

    create_action("swap-key", [Room, Room], [at_0,
                                              Select(get_has_key, 0)]
                  , [Select(get_has_key, 1), Fnot(Select(get_has_key, 0))])



    init = [proposition_lookup("at", [0]),
            proposition_lookup("has-key", [1]),
            ]

    goal = [proposition_lookup("at", [3])]


    solver = solver(3, init, goal, split=1)
    start = time.time()
    solver.interpolantion_solving(opt=False)
    print(time.time()-start)
    #solver.interpolantion_solving_union()