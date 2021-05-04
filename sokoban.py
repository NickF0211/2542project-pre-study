from problem_domain import *
from Solver import *

if __name__ == "__main__":
	print("running")
	Direction = ["dir-down", "dir-left", "dir-right", "dir-up"]
	Player = ["player-01"]
	Location = ["pos-1-1", "pos-1-2", "pos-1-3", "pos-1-4", "pos-1-5", "pos-1-6", "pos-1-7", 
				"pos-2-1", "pos-2-2", "pos-2-3", "pos-2-4", "pos-2-5", "pos-2-6", "pos-2-7", 
				"pos-3-1", "pos-3-2", "pos-3-3", "pos-3-4", "pos-3-5", "pos-3-6", "pos-3-7", 
				"pos-4-1", "pos-4-2", "pos-4-3", "pos-4-4", "pos-4-5", "pos-4-6", "pos-4-7", 
				"pos-5-1", "pos-5-2", "pos-5-3", "pos-5-4", "pos-5-5", "pos-5-6", "pos-5-7", 
				"pos-6-1", "pos-6-2", "pos-6-3", "pos-6-4", "pos-6-5", "pos-6-6", "pos-6-7", 
				"pos-7-1", "pos-7-2", "pos-7-3", "pos-7-4", "pos-7-5", "pos-7-6", "pos-7-7"]
	Stone = ["stone-01", "stone-02"]
	Thing = Player + Stone
	create_proposition("clear", [Location])
	create_proposition("at", [Thing, Location])
	create_proposition("at-goal", [Stone])
	create_proposition("IS-GOAL", [Location])
	create_proposition("IS-NONGOAL", [Location])
	create_proposition("MOVE-DIR", [Location, Location, Direction])
	print("finished creating proposition")
	get_clear = lambda loc: proposition_lookup("clear", loc)
	get_at = lambda thing_and_loc: proposition_lookup("at", thing_and_loc)
	get_at_goal = lambda stone: proposition_lookup("at-goal", stone)
	get_IS_GOAL = lambda loc: proposition_lookup("IS-GOAL", loc)
	get_IS_NONGOAL = lambda loc: proposition_lookup("IS-NONGOAL", loc)
	get_MOVE_DIR = lambda locs_and_dir: proposition_lookup("MOVE-DIR", locs_and_dir)
	#print("finished get blah")
	create_action("move", [Player, Location, Location, Direction], 
							[Select(get_at, [0, 1]), Select(get_clear, 2), Select(get_MOVE_DIR, [1, 2, 3])],
							[Fnot(Select(get_at, [0, 1])), Fnot(Select(get_clear, 2)), Select(get_at, [0, 2]), Select(get_clear, 1)])
	print("finished creating move")
	create_action("push-to-nongoal", [Player, Stone, Location, Location, Location, Direction], 
									[Select(get_at, [0, 2]), Select(get_at, [1, 3]), Select(get_clear, 4), Select(get_MOVE_DIR, [2, 3, 5]), 
									Select(get_MOVE_DIR, [3, 4, 5]), Select(get_IS_NONGOAL, 4)], 
									[Fnot(Select(get_at, [0, 2])), Fnot(Select(get_at, [1, 3])), Fnot(Select(get_clear, 4)), 
									Select(get_at, [0, 3]), Select(get_at, [1, 4]), Select(get_clear, 2), Fnot(Select(get_at_goal, 1))])
	print("finished creating push-to-nongoal")
	create_action("push-to-goal", [Player, Stone, Location, Location, Location, Direction], 
									[Select(get_at, [0, 2]), Select(get_at, [1, 3]), Select(get_clear, 4), Select(get_MOVE_DIR, [2, 3, 5]), 
									Select(get_MOVE_DIR, [3, 4, 5]), Select(get_IS_GOAL, 4)], 
									[Fnot(Select(get_at, [0, 2])), Fnot(Select(get_at, [1, 3])), Fnot(Select(get_clear, 4)), 
									Select(get_at, [0, 3]), Select(get_at, [1, 4]), Select(get_clear, 2), Select(get_at_goal, 1)])
	print("finish creating action")
	init = [proposition_lookup("IS-GOAL", "pos-3-6"),
			proposition_lookup("IS-GOAL", "pos-5-6"),
			proposition_lookup("IS-NONGOAL", "pos-1-1"),
			proposition_lookup("IS-NONGOAL", "pos-1-2"),
			proposition_lookup("IS-NONGOAL", "pos-1-3"),
			proposition_lookup("IS-NONGOAL", "pos-1-4"),
			proposition_lookup("IS-NONGOAL", "pos-1-5"),
			proposition_lookup("IS-NONGOAL", "pos-1-6"),
			proposition_lookup("IS-NONGOAL", "pos-1-7"),
			proposition_lookup("IS-NONGOAL", "pos-2-1"),
			proposition_lookup("IS-NONGOAL", "pos-2-2"),
			proposition_lookup("IS-NONGOAL", "pos-2-3"),
			proposition_lookup("IS-NONGOAL", "pos-2-4"),
			proposition_lookup("IS-NONGOAL", "pos-2-5"),
			proposition_lookup("IS-NONGOAL", "pos-2-6"),
			proposition_lookup("IS-NONGOAL", "pos-2-7"),
			proposition_lookup("IS-NONGOAL", "pos-3-1"),
			proposition_lookup("IS-NONGOAL", "pos-3-2"),
			proposition_lookup("IS-NONGOAL", "pos-3-3"),
			proposition_lookup("IS-NONGOAL", "pos-3-4"),
			proposition_lookup("IS-NONGOAL", "pos-3-5"),
			proposition_lookup("IS-NONGOAL", "pos-3-7"),
			proposition_lookup("IS-NONGOAL", "pos-4-1"),
			proposition_lookup("IS-NONGOAL", "pos-4-2"),
			proposition_lookup("IS-NONGOAL", "pos-4-3"),
			proposition_lookup("IS-NONGOAL", "pos-4-4"),
			proposition_lookup("IS-NONGOAL", "pos-4-5"),
			proposition_lookup("IS-NONGOAL", "pos-4-6"),
			proposition_lookup("IS-NONGOAL", "pos-4-7"),
			proposition_lookup("IS-NONGOAL", "pos-5-1"),
			proposition_lookup("IS-NONGOAL", "pos-5-2"),
			proposition_lookup("IS-NONGOAL", "pos-5-3"),
			proposition_lookup("IS-NONGOAL", "pos-5-4"),
			proposition_lookup("IS-NONGOAL", "pos-5-5"),
			proposition_lookup("IS-NONGOAL", "pos-5-7"),
			proposition_lookup("IS-NONGOAL", "pos-6-1"),
			proposition_lookup("IS-NONGOAL", "pos-6-2"),
			proposition_lookup("IS-NONGOAL", "pos-6-3"),
			proposition_lookup("IS-NONGOAL", "pos-6-4"),
			proposition_lookup("IS-NONGOAL", "pos-6-5"),
			proposition_lookup("IS-NONGOAL", "pos-6-6"),
			proposition_lookup("IS-NONGOAL", "pos-6-7"),
			proposition_lookup("IS-NONGOAL", "pos-7-1"),
			proposition_lookup("IS-NONGOAL", "pos-7-2"),
			proposition_lookup("IS-NONGOAL", "pos-7-3"),
			proposition_lookup("IS-NONGOAL", "pos-7-4"),
			proposition_lookup("IS-NONGOAL", "pos-7-5"),
			proposition_lookup("IS-NONGOAL", "pos-7-6"),
			proposition_lookup("IS-NONGOAL", "pos-7-7"),
			proposition_lookup("MOVE-DIR", ["pos-1-2", "pos-2-2", "dir-right"]),
			proposition_lookup("MOVE-DIR", ["pos-2-1", "pos-2-2", "dir-down"]),
			proposition_lookup("MOVE-DIR", ["pos-2-2", "pos-1-2", "dir-left"]),
			proposition_lookup("MOVE-DIR", ["pos-2-2", "pos-2-1", "dir-up"]),
			proposition_lookup("MOVE-DIR", ["pos-2-4", "pos-2-5", "dir-down"]),
			proposition_lookup("MOVE-DIR", ["pos-2-4", "pos-3-4", "dir-right"]),
		    proposition_lookup("MOVE-DIR", ["pos-2-5", "pos-2-4", "dir-up"]),
		    proposition_lookup("MOVE-DIR", ["pos-2-5", "pos-2-6", "dir-down"]),
		    proposition_lookup("MOVE-DIR", ["pos-2-5", "pos-3-5", "dir-right"]),
		    proposition_lookup("MOVE-DIR", ["pos-2-6", "pos-2-5", "dir-up"]),
		    proposition_lookup("MOVE-DIR", ["pos-2-6", "pos-3-6", "dir-right"]),
		    proposition_lookup("MOVE-DIR", ["pos-3-4", "pos-2-4", "dir-left"]),
		    proposition_lookup("MOVE-DIR", ["pos-3-4", "pos-3-5", "dir-down"]),
		    proposition_lookup("MOVE-DIR", ["pos-3-4", "pos-4-4", "dir-right"]),
		    proposition_lookup("MOVE-DIR", ["pos-3-5", "pos-2-5", "dir-left"]),
		    proposition_lookup("MOVE-DIR", ["pos-3-5", "pos-3-4", "dir-up"]),
		    proposition_lookup("MOVE-DIR", ["pos-3-5", "pos-3-6", "dir-down"]),
		    proposition_lookup("MOVE-DIR", ["pos-3-5", "pos-4-5", "dir-right"]),
		    proposition_lookup("MOVE-DIR", ["pos-3-6", "pos-2-6", "dir-left"]),
		    proposition_lookup("MOVE-DIR", ["pos-3-6", "pos-3-5", "dir-up"]),
		    proposition_lookup("MOVE-DIR", ["pos-3-6", "pos-4-6", "dir-right"]),
		    proposition_lookup("MOVE-DIR", ["pos-4-2", "pos-4-3", "dir-down"]),
		    proposition_lookup("MOVE-DIR", ["pos-4-2", "pos-5-2", "dir-right"]),
		    proposition_lookup("MOVE-DIR", ["pos-4-3", "pos-4-2", "dir-up"]),
		    proposition_lookup("MOVE-DIR", ["pos-4-3", "pos-4-4", "dir-down"]),
		    proposition_lookup("MOVE-DIR", ["pos-4-3", "pos-5-3", "dir-right"]),
		    proposition_lookup("MOVE-DIR", ["pos-4-4", "pos-3-4", "dir-left"]),
		    proposition_lookup("MOVE-DIR", ["pos-4-4", "pos-4-3", "dir-up"]),
		    proposition_lookup("MOVE-DIR", ["pos-4-4", "pos-4-5", "dir-down"]),
		    proposition_lookup("MOVE-DIR", ["pos-4-5", "pos-3-5", "dir-left"]),
		    proposition_lookup("MOVE-DIR", ["pos-4-5", "pos-4-4", "dir-up"]),
		    proposition_lookup("MOVE-DIR", ["pos-4-5", "pos-4-6", "dir-down"]),
		    proposition_lookup("MOVE-DIR", ["pos-4-5", "pos-5-5", "dir-right"]),
		    proposition_lookup("MOVE-DIR", ["pos-4-6", "pos-3-6", "dir-left"]),
		    proposition_lookup("MOVE-DIR", ["pos-4-6", "pos-4-5", "dir-up"]),
		    proposition_lookup("MOVE-DIR", ["pos-4-6", "pos-5-6", "dir-right"]),
		    proposition_lookup("MOVE-DIR", ["pos-5-2", "pos-4-2", "dir-left"]),
		    proposition_lookup("MOVE-DIR", ["pos-5-2", "pos-5-3", "dir-down"]),
		    proposition_lookup("MOVE-DIR", ["pos-5-2", "pos-6-2", "dir-right"]),
		    proposition_lookup("MOVE-DIR", ["pos-5-3", "pos-4-3", "dir-left"]),
		    proposition_lookup("MOVE-DIR", ["pos-5-3", "pos-5-2", "dir-up"]),
		    proposition_lookup("MOVE-DIR", ["pos-5-3", "pos-6-3", "dir-right"]),
		    proposition_lookup("MOVE-DIR", ["pos-5-5", "pos-4-5", "dir-left"]),
		    proposition_lookup("MOVE-DIR", ["pos-5-5", "pos-5-6", "dir-down"]),
		    proposition_lookup("MOVE-DIR", ["pos-5-5", "pos-6-5", "dir-right"]),
		    proposition_lookup("MOVE-DIR", ["pos-5-6", "pos-4-6", "dir-left"]),
		    proposition_lookup("MOVE-DIR", ["pos-5-6", "pos-5-5", "dir-up"]),
		    proposition_lookup("MOVE-DIR", ["pos-5-6", "pos-6-6", "dir-right"]),
		    proposition_lookup("MOVE-DIR", ["pos-6-2", "pos-5-2", "dir-left"]),
		    proposition_lookup("MOVE-DIR", ["pos-6-2", "pos-6-3", "dir-down"]),
		    proposition_lookup("MOVE-DIR", ["pos-6-3", "pos-5-3", "dir-left"]),
		    proposition_lookup("MOVE-DIR", ["pos-6-3", "pos-6-2", "dir-up"]),
		    proposition_lookup("MOVE-DIR", ["pos-6-5", "pos-5-5", "dir-left"]),
		    proposition_lookup("MOVE-DIR", ["pos-6-5", "pos-6-6", "dir-down"]),
		    proposition_lookup("MOVE-DIR", ["pos-6-6", "pos-5-6", "dir-left"]),
		    proposition_lookup("MOVE-DIR", ["pos-6-6", "pos-6-5", "dir-up"]),
		    proposition_lookup("at", ["player-01", "pos-6-3"]),
		    proposition_lookup("at", ["stone-01", "pos-4-3"]),
		    proposition_lookup("at", ["stone-02", "pos-5-3"]),
		    proposition_lookup("clear", "pos-1-2"),
		    proposition_lookup("clear", "pos-2-1"),
		    proposition_lookup("clear", "pos-2-2"),
		    proposition_lookup("clear", "pos-2-4"),
		    proposition_lookup("clear", "pos-2-5"),
		    proposition_lookup("clear", "pos-2-6"),
		    proposition_lookup("clear", "pos-3-4"),
		    proposition_lookup("clear", "pos-3-5"),
		    proposition_lookup("clear", "pos-3-6"),
		    proposition_lookup("clear", "pos-4-2"),
		    proposition_lookup("clear", "pos-4-4"),
		    proposition_lookup("clear", "pos-4-5"),
		    proposition_lookup("clear", "pos-4-6"),
		    proposition_lookup("clear", "pos-5-2"),
		    proposition_lookup("clear", "pos-5-5"),
		    proposition_lookup("clear", "pos-5-6"),
		    proposition_lookup("clear", "pos-6-2"),
		    proposition_lookup("clear", "pos-6-5"),
		    proposition_lookup("clear", "pos-6-6")]
	goal = [proposition_lookup("at-goal", "stone-01"),
			proposition_lookup("at-goal", "stone-02")]
	print("finish setting init and goal")
	solver = solver(3, init, goal, 1)
	solver.interpolantion_solving_union()




