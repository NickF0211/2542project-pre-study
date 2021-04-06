from z3 import *
import time

intepolantion_cost = 0
interpolant_time = 0


goal_condition = []
goal_distance =dict()
name_to_list = dict()
parent_child = dict()

def OneOf(selections):
    if len(selections) == 0:
        return False
    else:
        head = selections[0]
        return And(Implies(head, Not(Or(selections[1:]))), Implies(Not(head), OneOf(selections[1:])))



def add_if_not_subsumed(Ls, target, steps, parent, update_parent = True):
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
    add_to_goal_distance(target, steps, parent, update_parent = update_parent)
    return Ls


def add_to_goal_distance(Ls, steps, parent=None, update_parent= True, default_gap = 4):
    key = str(Ls)
    name_to_list[key] = Ls
    goal_distance[key] = steps
    if update_parent:
        while parent is not None:
            parent_key = str(parent)
            parent_child[key]  = parent_key
            goal_distance[parent_key] += (steps + default_gap)
            parent = parent_child.get(parent_key, None)


def remove_from_goal_distance(target):
    key = str(target)
    goal_distance[key] = 9999
    parent = parent_child.get(key, None)
    if parent is not None:
        children = get_live_child(parent)
        if len(children) == 0:
            remove_from_goal_distance(parent)


def get_live_child(target):
    target_key = str(target)
    return [child for child, parent in parent_child.items() if parent == target_key and goal_distance.get(child, 9999) < 9999]

def get_one_with_the_least_step():
    least_step = min(goal_distance.values())
    min_size = 10000
    target = None
    v = min_size
    for k in goal_condition[::-1]:
        k = str(k)
        v = goal_distance.get(k, -1)
        if v == least_step:
            size = len(name_to_list[k])
            if size < min_size:
                target = name_to_list[k]
                min_size = size

    return target, least_step

def get_other_constraints(target):
    rest = [Not(And(rst)) for rst in goal_condition if rst != target]
    return And(rest)






def main():
    start = time.time()
    steps = 5
    world_size = 7
    h = Hallway(world_size, steps, split=1, extended_goals=goal_condition)
    while True:
        new_steps = h.interpolants()
        print(new_steps)
        if steps == new_steps:
            print("valid solution")
            break
        else:
            h.recon_goals()
            steps = steps
    end = time.time()
    print(start-end)

    steps = 2
    start = time.time()
    while True:
        h = Hallway(world_size, steps)
        print(steps)
        if h.solve():
            print("valid solution")
            break
        else:
            steps +=1
    end = time.time()
    print(start-end)

class Hallway():
    def __init__(self, n, depth, split=1, extended_goals=[]):
        self.solver = Solver()
        self.depth = depth
        self.length = n
        self.split = split
        self.ats = [[Bool("at_{}_{}".format(str(i), str(k))) for i in range(n)] for k in range(depth)]
        self.unlocked = [[ Bool("unlocked_{}_{}_{}".format(str(i), str(i+1), str(k))) for i in range(n-1)] + [Bool("unlocked_{}_{}_{}".format(str(i+1), str(i), str(k) )) for i in range(n-1)] for k in range(depth)]
        self.have_key =  [[Bool("have_key_{}_{}".format(str(i), str(k))) for i in range(n)] for k in range(depth)]

        self.move= [[ Bool("move_{}_{}_{}".format(i, i+1, k )) for i in range(n-1)] + [Bool("move_{}_{}_{}".format(i+1, i, k )) for i in range(n-1)] for k in range(depth)]
        self.unlock = [[ Bool("unlock_{}_{}_{}".format(str(i), str(i+1), str(k))) for i in range(n-1)] + [Bool("unlock_{}_{}_{}".format(str(i+1), str(i), str(k) )) for i in range(n-1)] for k in range(depth)]

        self.swap_key = []
        for k in range(depth):
            collect_i = []
            for fr in range(n):
                collect_i_j = []
                for to in range(n):
                    collect_i_j.append(Bool("swap_key_{}_{}_{}".format(str(fr), str(to), str(k) )))
                collect_i.append(collect_i_j)
            self.swap_key.append(collect_i)
        goal = self.ats[-1][-1]
        p1, pn = self.get_all_frames(self.split)
        self.p1 = p1
        self.p1_states = self.get_all_state_variable(1)
        self.p0_states = self.get_all_state_variable(0)
        i_1, i_n=  self.get_invaraints(split)
        self.i_1 = i_1
        self.i_n = i_n
        self.solver.add(self.i_1)
        self.pn = pn
        self.solver.add(And(p1, pn))
        self.simply_goal = goal
        self.pre_goals = True
        self.goal = self.obtain_goals(goal, extended_goals)
        self.solver.push()
        self.solver.add(self.goal)
        self.solver.add(self.pre_goals)
        self.inter_init = [self.set_init()]
        self.other_init = True
        self.goal_parent = self.simply_goal
        goal_distance[str(self.simply_goal)] = 1

    def get_invaraints(self, split):
        return And([self.get_invaraint(i) for i in range(split)]), And(
            [self.get_invaraint(i) for i in range(split, self.depth - 1)])

    def get_invaraint(self, frame):
        return And(OneOf(self.ats[frame]), OneOf(self.have_key[frame]))

    def recon_goals(self):
        goals = [self.simply_goal]
        pre_goals = []
        for e_g in goal_condition:
            e_g = And(e_g)
            for j in range(self.split, self.depth-1):
                extended_goals = substitute(e_g, [ (p1_var, p0_var) for p1_var, p0_var in zip(self.p0_states, self.get_all_state_variable(j))])
                goals.append(extended_goals)

            for j in range(self.split):
                extended_goals = substitute(e_g, [ (p1_var, p0_var) for p1_var, p0_var in zip(self.p0_states, self.get_all_state_variable(j))])
                pre_goals.append(extended_goals)

        self.goal = Or(goals)
        self.pre_goals = True
        self.solver.pop()
        self.solver.push()
        self.solver.add(self.goal)
        self.solver.add(self.pre_goals)
        return

    def recon_goals_min(self):
        goals  = []
        pre_goals = []
        e_g, v = get_one_with_the_least_step()
        self.goal_parent = e_g
        e_g = And(e_g)
        print("now consider goal {} with distance {}".format(e_g, v))
        for j in range(self.split+1, self.depth - 1):
            extended_goals = substitute(e_g, [(p1_var, p0_var) for p1_var, p0_var in
                                              zip(self.p0_states, self.get_all_state_variable(j))])
            goals.append(extended_goals)

        for j in range( self.split):
            extended_goals = substitute(e_g, [(p1_var, p0_var) for p1_var, p0_var in
                                              zip(self.p0_states, self.get_all_state_variable(j))])
            pre_goals.append(extended_goals)

        self.goal = Or(goals)
        self.pre_goals = Or(pre_goals)
        self.solver.pop()
        self.solver.push()
        self.solver.add(self.goal)
        self.solver.add(self.pre_goals)
        self.other_init = get_other_constraints(self.goal_parent)
        self.solver.add(self.other_init)
        return

    def obtain_goals(self, original_goal, extended_goals= []):
        goals = [original_goal]
        for e_g in extended_goals:
            e_g = And(e_g)
            for j in range(2, self.depth-1):
                extended_goals = substitute(e_g, [ (p1_var, p0_var) for p1_var, p0_var in zip(self.p0_states, self.get_all_state_variable(self.depth-1))])
                goals.append(extended_goals)
        return Or(goals)

    def print_all_executed_actions(self, model):
        for i in range(self.depth):
            self.print_actions(i, model)

    def print_actions(self, frame, model):
        acts = self.get_all_act(frame)
        for act in acts:
            val = model[act]
            if val:
                print (act)

    def get_all_state_variable(self, frame):
        return self.ats[frame] + self.unlocked[frame] + self.have_key[frame]

    def get_swap_key(self, frame, fr, to):
        return self.swap_key[frame][fr][to]

    def get_unlocked(self, frame, fr, to):
        if fr < to:
            return self.unlocked[frame][fr]
        else:
            return self.unlocked[frame][self.length-1 + to]

    def get_unlock(self, frame, fr, to):
        if fr < to:
            return self.unlock[frame][fr]
        else:
            return self.unlock[frame][self.length-1 + to]

    def set_init(self):
        init_constraints = []
        for i in range(self.length):
            v = self.ats[0][i]
            if i != 0:
                init_constraints.append(Not(v))
            else:
                init_constraints.append(v)

        for i in range(self.length):
            v = self.have_key[0][i]
            if i != 1:
                init_constraints.append(Not(v))
            else:
                init_constraints.append(v)

        for i in range(len(self.unlocked[0])):
            v = self.unlocked[0][i]
            init_constraints.append(Not(v))
        return And(init_constraints)

    def set_goal(self):
        return Or([self.ats[i][self.length-1] for i in range(self.depth)])

    def set_goal_i(self, i):
        return Or([self.ats[j][self.length-1] for j in range(i, self.depth)])

    def get_all_act(self, i):
        all_act = self.move[i] + self.unlock[i]
        for k_list in self.swap_key[i]:
            all_act += k_list
        return all_act

    def get_all_frames(self, split):
        return And([self.get_frame_constraint(i) for i in range(split)]), And([self.get_frame_constraint(i) for i in range(split, self.depth-1)])


    def get_frame_constraint(self, i):
        constraint = []
        #for move
        at_i_prime = self.ats[i+1]
        at_i = self.ats[i]
        unlocked_i = self.unlocked[i]
        unlocked_i_prime = self.unlocked[i+1]
        have_key_i = self.have_key[i]
        have_key_i_prime = self.have_key[i+1]
        move = self.move[i]
        for j in range(self.length-1):
            fr = j
            to = j + 1
            reverse_index = self.length-1 + fr
            constraint.append(Implies(move[fr],  And([at_i[fr], unlocked_i[fr], Not(at_i_prime[fr]), at_i_prime[to]])))
            constraint.append(Implies(move[reverse_index], And([at_i[to], unlocked_i[reverse_index], Not(at_i_prime[to]), at_i_prime[fr]])))
            #print(Implies(move[reverse_index], And([at_i[to], unlocked_i[reverse_index], Not(at_i_prime[to]), at_i_prime[fr]])))

        #explantory frame for at
        for j in range(self.length):
            forward_move = []
            backward_move = []
            if j > 0:
                forward_move = [move[j-1]]
            if j < self.length-1:
                backward_move = [move[self.length-1 + j]]
            constraint.append(Implies(And(at_i_prime[j], Not(at_i[j])), Or(forward_move+ backward_move)))
            #print(Implies(And(at_i_prime[j], Not(at_i[j])), Or(forward_move+ backward_move)))

        for j in range(self.length-1):
            fr = j
            to = j + 1
            cons_f = Implies(self.get_unlock(i, fr, to) , And([at_i[fr], have_key_i[to] , self.get_unlocked(i+1,fr, to), self.get_unlocked(i+1,to, fr)]))
            constraint.append(cons_f)
            cons_b = Implies(self.get_unlock(i, to, fr),And([at_i[to], have_key_i[fr], self.get_unlocked(i+1,fr, to), self.get_unlocked(i+1,to, fr)]))
            constraint.append(cons_b)

        # explantory frame for unlock
        for j in range(self.length-1):
            forward_unlock = []
            forward_unlock.append(self.get_unlock(i, j, j+1))
            forward_unlock.append(self.get_unlock(i, j+1, j))
            constraint.append(Implies(And(unlocked_i_prime[j], Not(unlocked_i[j])), Or(forward_unlock)))
            #print(Implies(And(unlocked_i_prime[j], Not(unlocked_i[j])), Or(forward_unlock)))

        for j in range(self.length-1):
            backward_unlock = []
            fr = self.length - 1 - j
            to = fr -1
            backward_unlock.append(self.get_unlock(i, fr, to))
            backward_unlock.append(self.get_unlock(i, to, fr))
            constraint.append(Implies(And(self.get_unlocked(i+1, fr, to), Not(self.get_unlocked(i, fr, to))), Or(backward_unlock)))
            #print(Implies(And(self.get_unlocked(i+1, fr, to), Not(self.get_unlocked(i, fr, to))), Or(backward_unlock)))

        for j in range(self.length):
            for k in range(self.length):
                fr = j
                to = k
                constraint.append(Implies( self.get_swap_key(i, fr, to),
                                          And([at_i[0], have_key_i[fr], Not(have_key_i_prime[fr]), have_key_i_prime[to]])))
                #print(Implies( self.get_swap_key(i, fr, to), And([at_i[0], have_key_i[fr], Not(have_key_i_prime[fr]), have_key_i_prime[to]])))


        #explaintory frame
            constraint.append(Implies(And(have_key_i_prime[j], Not(have_key_i[j])), Or([self.get_swap_key(i, fr, j) for fr in range(self.length) ]) ))
            #print(Implies(And(have_key_i_prime[j], Not(have_key_i[j])), Or([self.get_swap_key(i, fr, j) for fr in range(self.length) ]) ))

        #constraint.append(AtLeast(*self.get_all_act(i), 1))
        #constraint.append(AtMost(*self.get_all_act(i), 1))
        constraint.append(OneOf(self.get_all_act(i)))
        #print(OneOf(self.get_all_act(i)))
        return And(constraint)


    def solve(self):
        init = self.set_init()
        self.solver.push()
        self.solver.add(init)
        res = self.solver.check()
        if (res == sat):
           return True
        else:
           return False

    def interpolants(self):
        global goal_condition
        init = self.set_init()
        steps = 0
        while True:
            self.solver.push()
            self.solver.add(init)
            res = self.solver.check()
            if (res == sat):
                #analyze the model
                m = self.solver.model()
                self.find_minimized_solutions(m, steps, upper=5)
                self.solver.pop()
                return steps + self.depth
            else:
                self.solver.pop()
                assert res == unsat
                '''
                sanity_check = Solver()
                sanity_check.add(init, self.p1, self.pn, self.goal)
                if sanity_check.check() == unsat:
                    print("okay")
                '''
                R = binary_interpolant(And(init, self.p1, self.other_init, self.i_1, self.pre_goals), And(self.pn, self.goal))
                #print(R)
                new_init = substitute(R, [ (p1_var, p0_var) for p1_var, p0_var in zip(self.p1_states, self.p0_states)])
                s = Solver()
                s.add(Not(Implies(new_init, init)))
                if (s.check() == unsat):
                   print("fix point, no more")
                   remove_from_goal_distance(self.goal_parent)
                   return -1
                #init = new_init
                #print("new init from interpol: {}".format(new_init))
                #self.inter_init.append(new_init)
                #init = Or(self.inter_init)
                init = new_init
                steps +=1
                print("progress")

    def find_minimized_solutions(self, m, steps, upper=5):
        global goal_condition
        counter = 0
        pos, neg = mk_lit_spilit(m, self.p0_states)
        min_L = minimize_L(self.solver, pos, neg)
        print(min_L)
        goal_condition = add_if_not_subsumed(goal_condition, min_L, steps, self.goal_parent)
        self.init_clean_up(And(min_L))
        while counter < upper:
            self.solver.add(Not(And(min_L)))
            res = self.solver.check()
            if (res == sat):
                m = self.solver.model()
                pos, neg = mk_lit_spilit(m, self.p0_states)
                min_L = minimize_L(self.solver, pos, neg)
                self.init_clean_up(And(min_L))
                print(min_L)
                goal_condition = add_if_not_subsumed(goal_condition, min_L, steps, self.goal_parent, update_parent=False)
                counter+=1
                continue
            else:
                return


    def init_clean_up(self, L):
        i = 0
        check_solver = Solver()
        check_solver.add(L)
        count = 0
        while i < len(self.inter_init):
            check_solver.push()
            current = self.inter_init[i]
            check_solver.add(current)
            res = check_solver.check()
            check_solver.pop()
            if res == sat:
                self.inter_init = self.inter_init[:i] + self.inter_init[i+1:]
                count += 1
            else:
                i+=1
        print("removed {}".format(count))


def mk_lit(m, x):
    if is_true(m.eval(x)):
       return x
    else:
       return Not(x) #we don't care about negated literal, at least for postive problem

def mk_lit_spilit(m, L):
    pos = []
    neg = []
    for l in L:
        if is_true(m.eval(l)):
            pos.append(l)
        else:
            neg.append(Not(l))
    return pos, neg





def minimize_L(B, L, neg):
    B.push()
    tick = 0
    changed = True
    B.add(And(neg))
    while changed:
        changed = False
        for i in range(len(L)):
            tick+=1
            current = L[i]
            rst = L[:i] + [Not(current)] + L[i+1:]
            if sat == B.check(rst):
                L = L[:i]  + L[i+1:]
                B.add(Not(current))
                changed = True
                break
            if tick >= 100:
                print("wow")
                B.pop()
                return L
    B.pop()
    return L



def pogo(A, B, xs):
    global interpolant_time
    start = time.time()
    ret = []
    model_num =0
    while sat == A.check():
       m = A.model()
       model_num+=1
       L = [mk_lit(m, x) for x in xs]
       L = minimize_L(B, L)
       if unsat == B.check(L):
          core = B.unsat_core()
          notL = Not(simplify(And(core)))
          ret.append(notL)
          A.add(notL)
       else:
          print("expecting unsat")
          break
    spent = time.time() - start
    interpolant_time += spent
    print(model_num)
    return (And(ret))
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
    print(interpolant_time)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
