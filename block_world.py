from z3 import *

prop_impacted = dict()

class Block_world():
    def __init__(self, n):
        object_size = n



class State():
    def __init__(self, objects):
        self.objects = objects
        self.p_on = self.init_predicate_ons()
        self.p_ontable = self.init_unary("ontable")
        self.clear = self.init_unary("clear")
        self.holding = self.init_unary("holding")
        self.empty = "empty"
        self.all_predicates = self.p_on + self.p_ontable +self.clear + self.holding + [self.empty]

    def init_predicate_ons(self):
        state_var = []
        for ob1 in self.objects:
            for ob2 in self.objects:
                state_var.append(self.predicate_on(ob1, ob2))
        return state_var

    def init_unary(self, key_word):
        return [self.unary(key_word, ob1) for ob1 in self.objects]


    def predicate_on(self, ob1, ob2):
        return "on_{}_{}".format(ob1, ob2)

    def unary(self, keyword, ob1):
        return "{}_{}".format(keyword, ob1)


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
        return Implies(And(precondition_frame + [act]), And(effect_frame))

    def analyze_effects(self):
        for prop in self.effects:
            add_to_impact(prop, self)

    def get_frame_var(self, i):
        return self.frame_var[i]



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


def reverse(prop):
    if prop.reverse is not None:
        return prop.reverse
    else:
        r_prop = Proposition("not_{}".format(prop.name), prop.para, polarity=False)
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
    return lambda arg: func([arg[index]])


class Block():
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "Block_{}".format(self.name)

    def __repr__(self):
        return self.__str__()

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

def explanatory_frame(n):
    return [explanatory_frame_per_i(i) for i in range(n-1)]

def explanatory_frame_per_i(i):
    res = []
    for key, actions in prop_impacted.items():
        impacted_prop = key.get_frame_var(i)
        next_prop = key.get_frame_var(i+1)
        constraints = []
        for act in actions:
            act_var = act.get_frame_var(i)
            preconditions = [prop.get_frame_var(i) for prop in act.precondition]
            constraints.append(And(preconditions + [act_var]))
        res.append(Implies(And(Not(impacted_prop), next_prop),  Or(constraints)))

    return And(res)





if __name__ == "__main__":
    Blocks = (Block("A"), Block("B"), Block("C"))
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
                     get_on], [lambda arg1, arg2: arg1 != arg2])

    create_action("unstack", [Blocks, Blocks], [get_on,
                                              get_empty,
                                                Select(get_clear, 0) ]
                  , [Select(get_holding, 0),
                     Select(get_clear, 1),
                     Fnot(Select(get_clear, 0)),
                     Fnot(get_empty),
                     Fnot(get_on)], [lambda arg1, arg2: arg1 != arg2])

    create_prop_frames(5)
    create_action_frames(5)
    exp = explanatory_frame(5)

    print("Hi")