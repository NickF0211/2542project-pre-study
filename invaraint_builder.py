from problem_domain import *

class Invaraint_builder():
    def __init__(self, split=1):
        depth = 2
        self.depth = 2
        self.act_length = 1
        self.split = split

        self.state_vars = [[prop.get_frame_var(i) for prop in get_all_props()] for i in range(self.depth)]
        self.acts_vars = [[prop.get_frame_var(i) for prop in get_all_acts()] for i in range(self.act_length)]

        # Transition System: T
        action_frames = collect_all_frames(depth)
        exp = explanatory_frame(depth)
        # exclusive_constraints = get_exclusion_constraints_old(depth)
        exclusive_constraints = []
        m_constraints = monotone_constraint(self.depth)

        # I and G
        #self.init = init_condition(init_prop)
        #self.goal = final_condition(goal_prop, depth)
        # the list of finals under consideration
        #self.inter_final = [self.goal]

        # For exploring and learning
        #self.goal_condition = [init_condition(init_prop, concat=False)]
        #self.blocked = []

        # init the solver
        self.solver = Solver()

        # stable constraints
        self.solver.add(action_frames + exclusive_constraints+ m_constraints)

        ## non-stable constraints
        #self.solver.add(self.init)

    def test_mutex(self):
        inv =[]
        props = get_all_props()
        for prop1 in props:
            for prop2 in props:
                if prop1 == prop2:
                    continue
                init = And(prop1.get_frame_var(0), prop2.get_frame_var(0))
                goal = And(prop1.get_frame_var(1), prop2.get_frame_var(1))
                if self.check_inductive(init, goal):
                    inv.append(init)

                init = And(Not(prop1.get_frame_var(0)), Not(prop2.get_frame_var(0)))
                goal = And(Not(prop1.get_frame_var(1)), Not(prop2.get_frame_var(1)))
                if self.check_inductive(init, goal):
                    inv.append(init)





    def check_inductive(self,init, goal):
        self.solver.push()
        self.solver.add(init)
        self.solver.add(Not(goal))

        res = self.solver.check()
        self.solver.pop()
        return self.solver == unsat

    def seq_encoding(self):
        f0 = AtLeastOneOf(self.get_act_vars(0))
        zero_vars = self.get_act_vars(0)
        return [f0] + [substitute(f0, [(p1_var, p0_var) for p1_var, p0_var in
                                       zip(zero_vars, self.get_act_vars(i))]) for i in
                       range(1, self.act_length)]


    def get_act_vars(self, i):
        return self.acts_vars[i]