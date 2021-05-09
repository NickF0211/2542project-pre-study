This is a repository for CSC2542 final project.
We define an interface for define "pddl".ish problem. Examples could be found in the problem files:  Hallway_new.py, Block_world.py or Sokoban.py.
Our planner is based on Propostional Interpolation. We use Z3 (verison 4.5.1 post 2) for testing satisfiability and use iz3 for deriving interpolant. 


Use "pip3 install z3-solver==4.5.1.0.post2" to isntall z3 with python binding.

Launch python on one of the problem: Hallway_new.py, Block_world.py or Sokoban.py

To run with Alg. 2 , launch the problem with solver.interpolantion_solving_union()
To run with Alg. 1 , launch the problem with solver.interpolantion_solving(opt = False)
