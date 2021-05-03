from problem_domain import *
import time

solving_time = 0

class solver():
    def __init__(self,  depth,  init_prop, goal_prop, split=1 ):
        self.depth = depth
        self.split = split
        create_prop_frames(depth)
        create_action_frames(depth)

        #Transition System: T
        action_frames = collect_all_frames(depth)
        exp = explanatory_frame(depth)
        exclusive_constraints = get_exclusion_constraints(depth)
        print("start1")

        #TODO optimize it with subs
        self.p1 = action_frames[:split] + exp[:split] + exclusive_constraints[:split]
        self.pn = action_frames[split:] + exp[split:] + exclusive_constraints[split:]
        print("start over")
        #I and G
        self.init =init_condition(init_prop)
        self.goal = final_condition(goal_prop, depth)
        #the list of finals under consideration
        self.inter_final = [self.goal]

        #init the solver
        self.solver = Solver()

        #stable constraints
        self.solver.add(self.p1 + self.pn)

        #non-stable constraints
        self.solver.push()
        self.solver.add(self.init)

        #invaraints
        self.tmp_i1 = True
        self.tmp_in = True

        print("start Done")


    def solve(self):
        global solving_time
        start = time.time()
        goal = self.goal
        self.solver.push()
        self.solver.add(goal)
        print("start solving")
        res = self.solver.check()
        if (res == sat):
           solving_time += (time.time() - start)
           return True
        else:
           solving_time += (time.time() - start)
           return False