from z3 import *

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

def create_action(action_name, arg_type_list, pre_condition_funcs, effects_functions, constraints = []):
    collection = Action.collection.get(action_name, dict())
    _create_action([action_name], arg_type_list, pre_condition_funcs, effects_functions, constraints, collection)
    Action.collection[action_name] = collection


def _create_action(prefix, arg_type_list, pre_condition_funcs, effects_functions, constraints, collections):
    if arg_type_list == []:
        # check constraints
        args = prefix[1:]
        for fun in constraints:
            if not fun(args):
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
    def __init__(self, name, paramters):
        self.name = name
        self.para = paramters
        self.reverse = None


def reverse(prop):
    r_prop = Proposition("not_{}".format(prop.name), prop.para)
    prop.reverse = r_prop
    r_prop.reverse = prop

def proposition_lookup(name, args):
    return Proposition.collection.get(name, dict()).get(args_to_name(args), None)

'''
forall arg in arg_list,  arg = (arg_type_list)
'''
def create_proposition(name, arg_type_list = [], constraints =[]):
    collection = Proposition.collection.get(name, dict())
    _create_proposition([name], arg_type_list, constraints, collection)
    Proposition.collection[name] =  collection

def args_to_name(args):
    return '_'.join([str(arg) for arg in args])


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
    return lambda arg : func(arg)


class Block():
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "Block_{}".format(self.name)

    def __repr__(self):
        return self.__str__()

if __name__ == "__main__":
    Blocks = (Block("A"), Block("B"), Block("C"))
    create_proposition("on", [Blocks, Blocks], [lambda arg1, arg2: arg1 != arg2])
    create_proposition("on-table", [Blocks])
    create_proposition("holding", [Blocks])
    create_proposition("clear", [Blocks])
    create_proposition("empty", [])
    get_clear = lambda block: proposition_lookup("clear", [block])
    get_on_table = lambda block: proposition_lookup("on-table", [block])
    get_holding = lambda block : proposition_lookup("holding", [block])
    create_action("pick-up", [Blocks], [(lambda block: proposition_lookup("clear", [block])),
                                        (lambda block: proposition_lookup("on-table", [block]))
                                        (lambda block: proposition_lookup("empty", []))]
                                     , [lambda block : reverse(proposition_lookup("on-table", [block])),
                                        lambda block : reverse(proposition_lookup("clear", [block])),
                                        lambda block : reverse(proposition_lookup("empty", [])),
                                        lambda block : proposition_lookup("holding", [block])])