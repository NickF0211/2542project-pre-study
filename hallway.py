from z3 import *
import time

intepolantion_cost = 0
interpolant_time = 0


goal_condition = []

def OneOf(selections):
    if len(selections) == 0:
        return False
    else:
        head = selections[0]
        return And(Implies(head, Not(Or(selections[1:]))), Implies(Not(head), OneOf(selections[1:])))



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
    return Ls



def main():
    start = time.time()
    steps = 3
    world_size = 6
    while True:
        h = Hallway(world_size, steps, split=1, extended_goals=goal_condition)
        new_steps = h.interpolants()
        print(new_steps)
        if steps == new_steps:
            print("valid solution")
            break
        else:
            steps = new_steps
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
        self.pn = pn
        self.solver.add(And(p1, pn))
        self.goal = self.obtain_goals(goal, extended_goals)
        self.solver.add(self.goal)

    def obtain_goals(self, original_goal, extended_goals= []):
        goals = [original_goal]
        for e_g in extended_goals:
            e_g = And(e_g)
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
                self.solver.pop()
                pos, neg = mk_lit_spilit(m, self.p0_states)
                self.solver.push()
                L = minimize_L(self.solver, pos, neg)
                self.solver.pop()
                print(L)
                goal_condition = add_if_not_subsumed(goal_condition, L)
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
                R = binary_interpolant(And(init, self.p1), And(self.pn, self.goal))
                #print(R)
                new_init = substitute(R, [ (p1_var, p0_var) for p1_var, p0_var in zip(self.p1_states, self.p0_states)])
                #s = Solver()
                #s.add(Not(Implies(new_init, init)))
                #if (s.check() == unsat):
                #    print("fix point, no more")
                #    return -1
                init = new_init
                #print(init)
                steps +=1
                print("progress")

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
                return L
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
