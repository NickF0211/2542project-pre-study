from problem_domain import *
import time
from invaraint_builder import Invaraint_builder

solving_time = 0

class solver():
    def __init__(self,  depth,  init_prop, goal_prop, split=1 ):
        self.depth = depth
        self.act_length = depth-1
        self.split = split
        create_prop_frames(depth)
        create_action_frames(depth)

        self.state_vars = [[prop.get_frame_var(i) for prop in get_all_props()] for i in range(self.depth)]
        self.acts_vars = [[prop.get_frame_var(i) for prop in get_all_acts()] for i in range(self.act_length)]

        #Transition System: T
        action_frames = collect_all_frames(depth)
        exp = explanatory_frame(depth)
        #exclusive_constraints = get_exclusion_constraints_old(depth)
        exclusive_constraints = self.seq_encoding()
        m_constraints = monotone_constraint(self.depth)


        #TODO optimize it with subs
        self.p1 = action_frames[:split] + exp[:split] + exclusive_constraints[:split] + m_constraints[:split]
        self.pn = action_frames[split:] + exp[split:] + exclusive_constraints[split:]+ m_constraints[split:]
        self.p1c = And(self.p1)
        self.pnc = And(self.pn)

        self.inv = []
        #I and G
        self.init =init_condition(init_prop)
        self.goal = final_condition(goal_prop, depth)
        #the list of finals under consideration
        self.inter_final = [self.goal]

        # For exploring and learning
        self.goal_condition = [init_condition(init_prop, concat=False)]
        self.blocked = []

        #init the solver
        self.solver = Solver()

        #stable constraints
        self.solver.add(self.p1 + self.pn)

        # invaraints
        self.tmp_i1 = True
        self.tmp_in = True

        self.goal_inv_1 = True
        self.goal_inv_n = True

        #non-stable constraints
        #self.build_invaraints(attempts=1000)

        self.solver.push()
        self.solver.add(self.init)




    def get_state_vars(self, i):
        return self.state_vars[i]

    def get_act_vars(self, i):
        return self.acts_vars[i]

    def build_invaraints(self, attempts = 1000):
        tested  = 0
        mapping = [(p1_var, p0_var) for p1_var, p0_var in zip(self.state_vars[0], self.state_vars[self.depth - 1])]
        for literal1 in self.goal_condition[0]:
            for literal2 in self.goal_condition[0]:
                target = Or(literal1, literal2)
                inv = self.test_invaraint(target, mapping)
                if inv  is not None:
                    self.add_invaraint(inv)
                    print("find inv {}".format(target))
        if tested > attempts:
            return


    def add_invaraint(self, inv):
        final_states = self.state_vars[-1]
        rest = [substitute(inv, [(p1_var, p0_var) for p1_var, p0_var in zip(final_states, self.get_state_vars(i))]) for i in range(self.depth-1)]
        total = rest + [inv]
        self.p1c = And(self.p1c, And(total[:self.split]))
        self.pnc = And(self.pnc, And(total[self.split:]))
        self.solver.add(total)
        self.inv += total[0]




    def test_invaraint(self, inv_goal, mapping):
        steps = 0
        goal = Not(substitute(inv_goal, mapping))
        while True:
            self.solver.push()
            self.solver.add(self.init)
            self.solver.add(goal)
            res = self.solver.check()
            self.solver.pop()
            if (res == sat):
                return None
            else:
                assert res == unsat
                '''
                sanity_check = Solver()
                sanity_check.add(self.init, And(self.p1), self.tmp_i1, self.goal_inv_1, And(self.pn), goal, self.tmp_in, self.goal_inv_n)
                if not sanity_check.check() == unsat:
                    print("oops")
                '''

                front = And(self.init, self.p1c, self.tmp_i1)
                back = And(self.pnc, goal, self.tmp_in)
                R = simplify(binary_interpolant(back, front))
                new_final = substitute(R, [(p1_var, p0_var) for p1_var, p0_var in
                                           zip(self.get_state_vars(1), self.get_state_vars(self.depth - 1))])
                s = Solver()
                s.add(And(Not(goal), new_final))
                if (s.check() == unsat):
                    return simplify(new_final)
                else:
                    pass
                #self.inter_final.append(new_final)
                goal = Or(goal, new_final)
                # goal = simplify(Or(new_final, goal))
                steps += 1


    def solve(self):
        global solving_time
        start = time.time()
        goal = self.goal
        self.solver.push()
        self.solver.add(goal)
        print("start solving")
        res = self.solver.check()
        if (res == sat):
            m = self.solver.model()
            self.print_all_executed_actions(m)
            solving_time += (time.time() - start)
            return True
        else:
           print("nope")
           solving_time += (time.time() - start)
           return False

    def interpolantion_solving_union(self):
        steps = self.depth
        while True:
            new_steps = self.interpolants()
            #print(new_steps)
            if steps == new_steps:
                print("valid solution")
                break
            elif new_steps == -1:
                print("unreachable goal")
                break
            else:
                self.recon_goals()
                steps = steps

    def interpolantion_solving(self, opt=True):
        steps = self.depth
        while True:
            new_steps = self.interpolants()
            # print(new_steps)
            if steps == new_steps:
                print("valid solution")
                break
            elif new_steps == -1:
                if (self.recon_single_goal(failed=True, opt=opt)):
                    continue
                else:
                    print("unreachable goal")
                    break
            else:
                self.recon_single_goal(opt=opt)
                steps = steps


    def interpolants(self):
        goal = self.inter_final[-1]
        steps = 0
        while True:
            self.solver.push()
            self.solver.add(goal)
            res = self.solver.check()
            if (res == sat):
                #analyze the model
                m = self.solver.model()
                m_min = self.minimize_number_of_action()
                if m_min is not None:
                    m = m_min
                frame_step = self.find_minimized_solutions(m, steps, upper=0)
                self.solver.pop()
                return frame_step * (self.depth-self.split) + self.depth
            else:
                self.solver.pop()
                assert res == unsat
                '''
                sanity_check = Solver()
                sanity_check.add(self.init, And(self.p1), self.tmp_i1, self.goal_inv_1, And(self.pn), goal, self.tmp_in, self.goal_inv_n)
                if not sanity_check.check() == unsat:
                    print("oops")
                '''

                front = And(self.init, self.p1c, self.tmp_i1)
                back = And(self.pnc, goal, self.tmp_in)
                R = simplify(binary_interpolant(back, front))
                new_final = substitute(R, [ (p1_var, p0_var) for p1_var, p0_var in zip(self.get_state_vars(1), self.get_state_vars(self.depth-1))])
                s = Solver()
                s.add(And(Not(goal), new_final))
                if (s.check() == unsat):
                   print("fix point, no more")
                   #print(R)
                   #global_inv.append(R)
                   self.inter_final = [self.goal]
                   return -1
                else:
                    pass
                self.inter_final.append(new_final)
                goal = new_final
                #goal = simplify(Or(new_final, goal))
                steps +=1


    '''
    helper function
    '''

    def seq_encoding(self):
        f0 = AtLeastOneOf(self.get_act_vars(0))
        zero_vars = self.get_act_vars(0)
        return [f0] + [substitute(f0, [(p1_var, p0_var) for p1_var, p0_var in
                                       zip(zero_vars, self.get_act_vars(i))]) for i in
                       range(1, self.act_length)]

    def recon_goals(self):
        inits = []
        for e_g in self.goal_condition:
            e_g = And(e_g)
            inits.append(e_g)

        self.init = Or(inits)
        self.solver.pop()
        self.solver.push()
        self.solver.add(self.init)
        return

    def recon_single_goal(self, failed = False, opt = True):
        considered_history = 999 #only consider the past 20 child
        max_failure = 999
        inits = self.goal_condition
        if failed:
            failed = self.goal_condition.pop()
            self.blocked.append(failed)
            if len(self.blocked) > max_failure:
                self.blocked.pop(0)
            if len(self.goal_condition) == 0:
                return False

        target = inits[-1]
        others = self.blocked + inits[max(0, len(inits)-1-considered_history):len(inits)-1]
        inv_i1 = []
        inv_in = []
        pfirst = self.get_state_vars(0)
        plast = self.get_state_vars(self.depth-1)
        if opt:
            for i in range(self.split):
                swap_map =  [(p1_var, p0_var) for p1_var, p0_var in
                                                  zip(pfirst, self.get_state_vars(i))]
                for other in others:
                    inv_i1.append(substitute(Not(And(other)), swap_map))

            for i in range(self.split, self.depth):
                swap_map =  [(p1_var, p0_var) for p1_var, p0_var in
                                                  zip(pfirst, self.get_state_vars(i))]
                for other in others:
                    inv_in.append(substitute(Not(And(other)), swap_map))

            inv_in.append(substitute(Not(And(target)),  [(p1_var, p0_var) for p1_var, p0_var in
                                                  zip(pfirst, plast)]))
            self.tmp_i1 = And(inv_i1)
            self.tmp_in = And(inv_in)
        else:
            swap_map = [(p1_var, p0_var) for p1_var, p0_var in
                        zip(pfirst, plast)]
            for other in others:
                inv_in.append(substitute(Not(And(other)), swap_map))
            inv_in.append(substitute(Not(And(target)), swap_map))

            self.tmp_i1 = True
            self.tmp_in = And(inv_in)


        self.init = And(target)
        self.solver.pop()

        #time to add global inv
        '''
        if len(self.global_inv) > 0:
            g1 , gn = self.prepare_transitive_invaraint()
            self.goal_inv_1 = And(And(g1), self.goal_inv_1)
            self.goal_inv_n = And(And(gn), self.goal_inv_n)
            self.solver.add(self.goal_inv_1, self.goal_inv_n)
        '''

        self.solver.push()
        self.solver.add(self.init)
        self.solver.add(self.tmp_i1, self.tmp_in)
        return True

    def print_all_executed_actions(self, model):
        for i in range(self.act_length):
            self.print_actions(i, model)

    def print_actions(self, frame, model):
        acts = self.get_act_vars(frame)
        for act in acts:
            val = model[act]
            if val:
                print (act)

    def minimize_number_of_action(self):
        self.solver.push()
        self.solver.add(self.forbid_action(0))
        res = self.solver.check()
        if res == unsat:
            self.solver.pop()
            return None
        else:
            model = self.solver.model()
            self.solver.pop()
            return model




    def find_minimized_solutions(self, m, steps, upper=99):
        counter = 0
        plast_state = self.get_state_vars(self.depth-1)
        pfirst_state = self.get_state_vars(0)
        pos, neg = mk_lit_spilit(m, plast_state)
        min_L = pos+ neg
        self.print_all_executed_actions(m)
        swap_dict= [(p1_var, p0_var) for p1_var, p0_var in
                                              zip(plast_state, pfirst_state)]
        self.goal_condition = add_if_not_subsumed(self.goal_condition, self.state_project(min_L, swap_dict))
        step = self.init_clean_up(And(min_L))
        while counter < upper:
            self.solver.add(Not(And(min_L)))
            res = self.solver.check()
            if (res == sat):
                m = self.solver.model()
                pos, neg = mk_lit_spilit(m, plast_state)
                min_L = pos+ neg
                other_step = self.init_clean_up(And(min_L))
                step += other_step
                print("solution:")
                self.print_all_executed_actions(m)
                self.goal_condition = add_if_not_subsumed(self.goal_condition, self.state_project(min_L, swap_dict))
                counter+=1
                continue
            else:
                break

        return step

    def init_clean_up(self, L):
        i = 0
        check_solver = Solver()
        check_solver.add(L)
        count = 0
        while i < len(self.inter_final):
            check_solver.push()
            current = self.inter_final[i]
            check_solver.add(current)
            res = check_solver.check()
            check_solver.pop()
            if res == sat:
                old_len = len(self.inter_final)
                self.inter_final = self.inter_final[:i]
                count += (old_len - len(self.inter_final))
                break
            else:
                i+=1
        return i

    def state_project(self, target_lst, sources_to_target):
        res_lst = []
        for target in target_lst:
            res_lst.append(substitute(target, sources_to_target))
        return res_lst

    def forbid_action(self, i):
        return Not(Or(self.get_act_vars(i)))



def add_if_not_subsumed(Ls, target):
    i = 0
    while i < len(Ls):
        l = Ls[i]
        #if l subsumes target, then do nothing
        s_l = set(l)
        s_t = set(target)
        if len(s_l - s_t)==0:
            return Ls
        if len(s_t - s_l) == 0:
            Ls = Ls[:i] + Ls[i+1:]

        i +=1

    Ls.append(target)
    #add_to_goal_distance(target, steps, parent, update_parent = update_parent)
    return Ls

def minimize_L(B, pos, neg):
    B.push()
    L = neg
    tick = 0
    changed = True
    B.add(And(pos))
    while changed:
        changed = False
        for i in range(len(L)):
            tick+=1
            current = L[i]
            rst = L[:i] + [current.arg(0)] + L[i+1:]
            if sat == B.check(rst):
                L = L[:i]  + L[i+1:]
                B.add(Not(current))
                changed = True
                break
            if tick >= 100:
                print("wow")
                B.pop()
                return L+pos
    B.pop()
    return L+pos



def mk_lit_spilit(m, L):
    pos = []
    neg = []
    for l in L:
        res= m.eval(l)
        if is_true(res):
            pos.append(l)
        elif is_false(res):
            neg.append(Not(l))
        else:
            pass
            #pos.append(l)
    return pos, neg