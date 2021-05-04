from z3 import  *
prop_impacted = dict()


all_act = []
all_props = []

class Action():
    collection = dict()
    def __init__(self, name, paras, precondition, effects):
        self.name = name
        self.paras = paras
        self.precondition = precondition
        self.effects = effects
        self.frame_var = []
        self.pre_to_effect = []

    def create_frame(self, n):
        self.frame_var = [Bool("{}_{}_{}".format(self.name, args_to_name(self.paras), i)) for i in range(n-1)]
        self.create_transition_frame(n)

    def create_transition_frame(self, n):
        self.pre_to_effect = [self._create_pre_to_effect_frame(i) for i in range(n-1)]

    def _create_pre_to_effect_frame(self, i):
        act = self.frame_var[i]
        precondition_frame = [prop.get_frame_var(i) for prop in self.precondition]
        effect_frame =  [prop.get_frame_var(i+1) for prop in self.effects]
        return Implies(act, And(precondition_frame + effect_frame))

    def analyze_effects(self):
        for prop in self.effects:
            add_to_impact(prop, self)

    def get_frame_var(self, i):
        return self.frame_var[i]



    def __str__(self):
        return "{}_{}".format(self.name, args_to_name(self.paras))

    def __repr__(self):
        return self.__str__()



def create_action(action_name, arg_type_list, pre_condition_funcs, effects_functions, constraints = []):
    collection = Action.collection.get(action_name, dict())
    _create_action([action_name], arg_type_list, pre_condition_funcs, effects_functions, constraints, collection)
    Action.collection[action_name] = collection


def _create_action(prefix, arg_type_list, pre_condition_funcs, effects_functions, constraints, collections):
    if arg_type_list == []:
        # check constraints
        args = prefix[1:]
        for fun in constraints:
            if not fun(*args):
                return
        preconditions = [func(args) for func in pre_condition_funcs]
        effects = [func(args) for func in effects_functions]
        collections[args_to_name(args)] = (Action(prefix[0], prefix[1:], preconditions, effects))
    else:
        cur_arg_type = arg_type_list[0]
        for arg in cur_arg_type:
            new_prefix = prefix + [arg]
            _create_action(new_prefix, arg_type_list[1:], pre_condition_funcs, effects_functions, constraints, collections)


class Proposition():
    collection = dict()
    def __init__(self, name, paramters, polarity = True):
        self.name = name
        self.para = paramters
        self.reverse = None
        self.polarity = polarity
        self.frame_var = []

    def create_frame(self, n):
        if self.polarity:
            self.frame_var = [Bool("{}_{}_{}".format(self.name, args_to_name(self.para), i)) for i in range(n)]
        else:
            self.frame_var = [Not(Bool("{}_{}_{}".format(self.name, args_to_name(self.para), i))) for i in range(n)]


    def get_frame_var(self, i):
        return self.frame_var[i]

    def get_frame_var_dur_act(self, i):
        return Bool("{}_{}_{}_DA".format(self.name, args_to_name(self.para), i))

    def __str__(self):
        if self.polarity:
            return "{}_{}".format(self.name, args_to_name(self.para))
        else:
            return "not_{}_{}".format(self.name, args_to_name(self.para))

    def __repr__(self):
        return self.__str__()


def reverse(prop):
    if prop.reverse is not None:
        return prop.reverse
    else:
        r_prop = Proposition(prop.name, prop.para, polarity=False)
        prop.reverse = r_prop
        r_prop.reverse = prop
        return prop.reverse

def proposition_lookup(name, args):
    res = Proposition.collection.get(name, dict()).get(args_to_name(args), None)
    return res

'''
forall arg in arg_list,  arg = (arg_type_list)
'''
def create_proposition(name, arg_type_list = [], constraints =[]):
    collection = Proposition.collection.get(name, dict())
    _create_proposition([name], arg_type_list, constraints, collection)
    Proposition.collection[name] =  collection

def args_to_name(args):
    return '_'.join([str(arg) for arg in args])


def add_to_impact(prop, action):
    res =  prop_impacted.get(prop, set())
    res.add(action)
    prop_impacted[prop] = res

def _create_proposition(prefix, arg_type_list, constraints, collections):
    #if we have processed all the arguments
    if arg_type_list == []:
        #check constraints
        args = prefix[1:]
        for fun in constraints:
            if not fun(*args):
                return
        collections[args_to_name(args)] =(Proposition(prefix[0], prefix[1:]))
    else:
        cur_arg_type = arg_type_list[0]
        for arg in cur_arg_type:
            new_prefix = prefix + [arg]
            _create_proposition(new_prefix, arg_type_list[1:], constraints, collections)

def Fnot(func):
    return lambda arg : reverse(func(arg))

def Select(func, index):
    if type(index) is int:
        return lambda arg: func([arg[index]])
    elif type(index) is list:
        return lambda arg: func([arg[i] for i in index])

def Re_Order(func,  indexes):
    def new_func(args):
        new_args = []
        for index in indexes:
            new_args.append(args[index])
        return func(new_args)
    return new_func


'''
For SAT encoding function
'''
def create_prop_frames(n):
    for prop_values in Proposition.collection.values():
        for prop in prop_values.values():
            prop.create_frame(n)
            if prop.reverse is not None:
                prop.reverse.create_frame(n)

def create_action_frames(n):
    for act_values in Action.collection.values():
        for act in act_values.values():
            act.create_frame(n)
            act.analyze_effects()

def collect_all_frames(n):
    return [collect_action_frame(i) for i in range(n-1)]

def collect_action_frame(i):
    res = []
    for act_values in Action.collection.values():
        for act in act_values.values():
            res.append(act.pre_to_effect[i])
    return And(res)

def explanatory_frame(n):
    res = [explanatory_frame_per_i(i) for i in range(n - 1)]
    return res

def explanatory_frame_per_i(i):
    res = []
    for key, actions in prop_impacted.items():
        impacted_prop = key.get_frame_var(i)
        next_prop = key.get_frame_var(i+1)
        constraints = []
        for act in actions:
            act_var = act.get_frame_var(i)
            #preconditions = [prop.get_frame_var(i) for prop in act.precondition]
            constraints.append(act_var)
        res.append(Implies(And(Not(impacted_prop), next_prop),  Or(constraints)))

    return And(res)

def is_exclusive(act1, act2):
    for pre_act1 in act1.precondition:
        r = pre_act1.reverse
        if r is not None and r in act2.precondition:
            return True
    return False

def is_dependent(act1, act2):
    for pre_act2 in act2.precondition:
        r = pre_act2.reverse
        if r is not None and r in act1.effects:
            return False

    return True

def get_all_acts():
    if all_act == []:
        acts = []
        for act_values in Action.collection.values():
            for act in act_values.values():
                acts.append(act)
        return acts
    else:
        return all_act

def get_all_props():
    if all_props == []:
        props = []
        for prop_values in Proposition.collection.values():
            for prop in prop_values.values():
                props.append(prop)
        return props
    else:
        return all_props

def get_exclusion_constraints(n):
    print("start1")
    all_act = get_all_acts()
    #exclusive_acts = get_exclusive_actions()
    f0 = analyze_actions_for_exclusion(0)
    zero_vars = [act.get_frame_var(0) for act in all_act] + [prop.get_frame_var_dur_act(0)  for prop in get_all_props()]
    print("start1")
    return [f0] + [substitute(f0, [(p1_var, p0_var) for p1_var, p0_var in
                                              zip(zero_vars, [act.get_frame_var(i) for act in all_act] + [prop.get_frame_var_dur_act(i)  for prop in get_all_props()])] ) for i in range(1, n-1)]

def analyze_actions_for_exclusion(i):
    all_act = get_all_acts()
    constraints = []
    flip = dict()
    for act in all_act:
        act_constraint = []
        flipped = set([flip_act for flip_act in act.precondition if (flip_act.reverse is not None and flip_act.reverse in act.effects)])
        collect_flipped(flip, act, flipped)
        consequence = [precond.get_frame_var_dur_act(i) for precond in act.precondition if precond not in flipped] +\
                      [eff.get_frame_var_dur_act(i) for eff in act.effects]
        act_constraint.append(Implies(act.get_frame_var(i), And(consequence)))
        constraints += act_constraint

    constraints += generate_mutex(flip, i)

    return And(constraints)

mutex = set()

def collect_flipped(flipped, act, flipping):
    for prop in flipping:
        p_res = flipped.get(prop, set())
        p_res.add(act)
        flipped[prop] = p_res

def get_bmutex_from_col(col, i ):
    if len(col) == 0:
        return []
    else:
        head = col[0]
        rst = col[1:]
        return [Not(And(head.get_frame_var(i), prop.get_frame_var(i))) for prop in rst if not add_bmutex_if_not_exists(head, prop)]+get_bmutex_from_col(rst, i)

def add_bmutex_if_not_exists(p1, p2):
    if (p1, p2) in mutex or (p2, p1) in mutex:
        return True
    else:
        mutex.add((p1, p2))
        return False


def generate_mutex(flipped, i):
    constraints = []
    for key, value in flipped.items():
        constraints += get_bmutex_from_col(list(value), i)
    return constraints


def get_exclusion_constraints_old(n):
    all_act = get_all_acts()
    exclusive_acts = get_exclusive_actions()
    f0 = _get_exclusion_constraint(exclusive_acts, 0)
    zero_vars = [act.get_frame_var(0) for act in all_act]
    return [f0] + [substitute(f0, [(p1_var, p0_var) for p1_var, p0_var in
                                              zip(zero_vars, [act.get_frame_var(i) for act in all_act])]) for i in range(1, n-1)]


def _get_exclusion_constraint(exclusive_acts, i):
    return And([ Implies(act1.get_frame_var(i), Not(Or([act2.get_frame_var(i) for act2 in act2s] ))) for (act1, act2s) in exclusive_acts])


def init_condition(pos_prop, concat = True):
    constraints = []
    for prop in get_all_props():
        if prop in pos_prop:
            constraints.append(prop.get_frame_var(0))
        else:
            constraints.append(Not(prop.get_frame_var(0)))
    if concat:
        return And(constraints)
    else:
        return constraints

def final_condition(pos_props, n):
    return And([pos_prop.get_frame_var(n-1) for pos_prop in pos_props])




def monotone_constraint(n):
    m_prop = find_monotone()
    return [inductive_constraints(m_prop, i) for i in range(n-1)]


def build_mutexes_constraint(mutexes, n):
    all_prop = get_all_props()
    f0 = define_mutexes(mutexes, 0)
    zero_vars = [prop.get_frame_var(0) for prop in all_prop]
    return [f0] + [substitute(f0, [(p1_var, p0_var) for p1_var, p0_var in
                                   zip(zero_vars, [prop.get_frame_var(i) for prop in all_prop])]) for i in range(1, n)]

def define_mutexes(mutexes, i):
    constraints = []
    for mutex in mutexes:
        constraints.append(AtLeastOneOf([prop.get_frame_var(i) for prop in mutex]))
    return And(constraints)


def inductive_constraints(props, i):
    cons = []
    for prop in props:
        old_v = prop.get_frame_var(i)
        new_v = prop.get_frame_var(i+1)
        cons.append(Implies(old_v, new_v))
    return And(cons)





def find_monotone():
    props = prop_impacted.keys()
    mon =[]
    for prop in props:
        r_prop = prop.reverse
        if r_prop is None:
            mon.append(prop)
        else:
            if r_prop not in props:
                mon.append(prop)
    return mon



def build_action_inv():
    shared_effects = []
    for prop, actions in prop_impacted.items():
        common_effect = None
        for action in actions:
            if common_effect is None:
                common_effect = set(action.effects)
            else:
                common_effect = common_effect - set(action.effects)

        filter_common_act = []
        for se in common_effect:
            if se == prop:
                continue
            should_include = True
            #check the effect negats them, if prop is in them, then we can say they are invaraints
            se_n_acts = prop_impacted.get(reverse(se), [])
            for action in se_n_acts:
                if not reverse(prop) in action.effects:
                    should_include = False
                    break
            if should_include:
                filter_common_act.append(se)

        if filter_common_act != []:
            shared_effects.append((prop, filter_common_act))
    return shared_effects



def get_exclusive_actions():
    all_acts = get_all_acts()
    constrainted = []
    for act1 in all_acts:
        disabled = []
        for act2 in all_acts:
            if act1 != act2:
                if not is_exclusive(act1, act2):
                    if is_dependent(act1, act2):
                        disabled.append(act2)
        if len(disabled) > 0:
            constrainted.append((act1, disabled))
    return constrainted


def AtLeastOneOf(selections):
    if len(selections) == 0:
        return True
    else:
        head = selections[0]
        return And(Implies(head, Not(Or(selections[1:]))), AtLeastOneOf(selections[1:]))
