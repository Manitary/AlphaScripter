import copy
import json
import random

from globals import (
    ACTIONS,
    BUILDABLE,
    FACTS,
    FORMATIONS,
    GOAL_FACTS,
    PARAMETERS,
    PLAYER_LIST,
    SIMPLE_COMPARE,
    SN,
    TRAINABLE,
)
from models import (
    Action,
    AttackRule,
    DUCSearch,
    Fact,
    Filter,
    GameTimeCondition,
    Goal,
    GoalFact,
    PopulationCondition,
    Rule,
    Simple,
)
from settings import *
import settings

if allow_towers:
    PARAMETERS["Buildable"] += ";watch-tower;guard-tower;keep"

with open("resign.txt", "r", encoding="utf-8") as f:
    RESIGN_RULE = f.read()


def generate_goal() -> Goal:
    goal_id = random.randint(1, 40)
    value = random.randint(0, 1)
    disable = random.choice([True, False])
    goal_num = random.randint(1, 40)
    use_goal = random.choice([True, False])
    fact_count = random.randint(1, 4)

    used_facts = [
        GoalFact(random.choice(GOAL_FACTS), generate_parameters()) for _ in range(4)
    ]

    return Goal(goal_id, value, disable, goal_num, use_goal, used_facts, fact_count)


def mutate_goal(goal: Goal, mutation_chance: float) -> Goal:
    if random.random() < mutation_chance:
        goal.goal_id = random.randint(1, 40)
    if random.random() < mutation_chance:
        goal.value = random.randint(0, 1)
    if random.random() < mutation_chance:
        goal.disable = random.choice([True, False])
    if random.random() < mutation_chance:
        goal.goal_num = random.randint(1, 40)
    if random.random() < mutation_chance:
        goal.use_goal = random.choice([True, False])
    if random.random() < mutation_chance:
        goal.fact_count = random.randint(1, 4)
    for fact in goal.used_facts:
        fact = GoalFact(
            random.choice(GOAL_FACTS),
            mutate_parameters(fact.parameters, mutation_chance),
        )

    return goal


def parse_params() -> dict[str, str]:
    with open("params.csv", "r", encoding="utf-8") as f:
        params = f.readlines()

    paramdict = {x[0]: x[1] for param in params if len(x := param.split(",")) > 1}
    print(paramdict)

    return paramdict


def mutate_parameters(
    parameters: dict[str, str | int], mutation_chance: float
) -> dict[str, str | int]:
    out = copy.deepcopy(parameters)
    for key in parameters:
        mutation_rules = PARAMETERS[key]
        if "|" in mutation_rules:
            if random.random() < mutation_chance:
                out[key] = random.randint(*tuple(map(int, mutation_rules)))
        elif ";" in mutation_rules:
            if random.random() < mutation_chance:
                out[key] = random.choice(mutation_rules.split(";"))
        else:
            out[key] = PARAMETERS[key]

    return out


def generate_parameters() -> dict[str, str | int]:
    out: dict[str, str | int] = {}
    for key, mutation_rules in PARAMETERS.items():
        if "|" in mutation_rules:
            out[key] = random.randint(*tuple(map(int, mutation_rules.split("|"))))
        elif ";" in mutation_rules:
            out[key] = random.choice(mutation_rules.split(";"))
        else:
            out[key] = mutation_rules

    return out


def generate_sn_values() -> dict[str, str | int]:
    out: dict[str, str | int] = {}
    for key, mutation_rules in SN.items():
        if "|" in mutation_rules:
            out[key] = random.randint(*tuple(map(int, mutation_rules)))
        elif ";" in mutation_rules:
            out[key] = random.choice(mutation_rules.split(";"))
        else:
            out[key] = mutation_rules

    return out


def mutate_sn_values(
    sn_values: dict[str, str | int], mutation_chance: float
) -> dict[str, str | int]:
    out = copy.deepcopy(sn_values)
    for key, mutation_rules in SN.items():
        if "|" in mutation_rules:
            if random.random() < mutation_chance:
                out[key] = random.randint(*tuple(map(int, mutation_rules)))
        elif ";" in mutation_rules:
            if random.random() < mutation_chance:
                out[key] = random.choice(mutation_rules.split(";"))

    return out


def generate_fact() -> Fact:
    fact_name = random.choice(list(FACTS))
    is_not = random.randint(0, 1)
    params = generate_parameters()
    and_or = random.choice(["and", "or", "nand", "nor"])

    return Fact(fact_name, is_not, params, and_or)


def generate_action() -> Action:
    action_name = random.choice(list(ACTIONS))
    parameters = generate_parameters()
    strategic_numbers = generate_sn_values()

    return Action(action_name, parameters, strategic_numbers)


def mutate_fact(fact: Fact, mutation_chance: float) -> Fact:
    if random.random() < mutation_chance:
        fact.fact_name = random.choice(list(FACTS))
    if random.random() < mutation_chance:
        fact.is_not = random.randint(0, 1)
    fact.parameters = mutate_parameters(fact.parameters, mutation_chance)
    if random.random() < mutation_chance:
        fact.and_or = random.choice(["and", "or", "nand", "nor"])

    return fact


def mutate_action(action: Action, mutation_chance: float) -> Action:
    if random.random() < mutation_chance:
        action.action_name = random.choice(list(ACTIONS))
    action.parameters = mutate_parameters(action.parameters, mutation_chance)
    action.strategic_numbers = mutate_sn_values(
        action.strategic_numbers, mutation_chance
    )

    return action


def generate_rule() -> Rule:
    fact_length = random.randint(1, max_fact_length)
    action_length = random.randint(1, max_action_length)
    # age_required = random.choice([["","","#load-if-not-defined DARK-AGE-END","#end-if","#load-if-not-defined FEUDAL-AGE-END","#end-if","#load-if-not-defined CASTLE-AGE-END","#end-if","#load-if-not-defined IMPERIAL-AGE-START","#end-if"]])
    age_required = ["", ""]
    local_facts = [generate_fact() for _ in range(max_fact_length)]
    local_actions = [generate_action() for _ in range(max_fact_length)]

    return Rule(fact_length, action_length, age_required, local_facts, local_actions)


def mutate_rule(rule: Rule, mutation_chance: float) -> Rule:
    if random.random() < mutation_chance:
        rule.fact_length = random.randint(1, max_fact_length)
    if random.random() < mutation_chance:
        rule.action_length = random.randint(1, max_action_length)
    if random.random() < mutation_chance:
        rule.age_required = random.choice(
            [
                [
                    "",
                    "",
                    "#load-if-not-defined DARK-AGE-END",
                    "#end-if",
                    "#load-if-not-defined FEUDAL-AGE-END",
                    "#end-if",
                    "#load-if-not-defined CASTLE-AGE-END",
                    "#end-if",
                    "#load-if-not-defined IMPERIAL-AGE-START",
                    "#end-if",
                ]
            ]
        )
    for fact in rule.local_facts:
        fact = mutate_fact(fact, mutation_chance)
    for action in rule.local_actions:
        action = mutate_action(action, mutation_chance)
    if random.random() < mutation_chance / 5:
        rule = generate_rule()

    return rule


def simple_to_complex(simple):
    rule = generate_rule()

    type = simple[0]
    params = copy.deepcopy(simple[1])
    threshold = simple[2]
    simple_age_required = simple[3].copy()
    requirement = simple[4]

    # print(params)

    fact_length = rule[0]
    action_length = rule[1]
    age_required = rule[2]
    local_facts = rule[3].copy()
    local_actions = rule[4].copy()

    for i in range(len(local_facts)):
        local_facts[i][1] = 0
        local_facts[i][3] = "and"

    action_length = 1
    fact_length = 0

    # fact = [fact_name, is_not, params, and_or]
    first_fact = 0

    if simple_age_required != [""]:
        fact_length += 1
        local_facts[first_fact][0] = "current-age"

        simple_age_required[0] = simple_age_required[0].replace("   ", " ")
        simple_age_required[0] = simple_age_required[0].replace("  ", " ")

        temp = simple_age_required[0].split(" ")

        local_facts[first_fact][2]["compareOp"] = temp[1]

        if temp[2] in ["0", "1", "2", "3", "4", "5"]:
            local_facts[first_fact][2]["Age"] = temp[2]
        else:
            local_facts[first_fact][2]["Age"] = "2"

        first_fact += 1

    if type == "train":
        fact_length += 2

        local_facts[first_fact][0] = "can-train"
        local_facts[first_fact][2]["UnitId"] = params["Trainable"]

        local_facts[first_fact + 1][0] = "unit-type-count"
        local_facts[first_fact + 1][2]["compareOp"] = "<"
        local_facts[first_fact + 1][2]["UnitId"] = params["Trainable"]
        local_facts[first_fact + 1][2]["0|50"] = threshold

        local_actions[0][0] = "train"
        local_actions[0][1]["Trainable"] = params["Trainable"]

    elif type == "build":
        fact_length += 2

        local_facts[first_fact][0] = "can-build"
        local_facts[first_fact][2]["BuildingId"] = params["Buildable"]

        local_facts[first_fact + 1][0] = "building-type-count"
        local_facts[first_fact + 1][2]["compareOp"] = "<"
        local_facts[first_fact + 1][2]["BuildingId"] = params["Buildable"]

        if params["Buildable"] != "farm":
            local_facts[first_fact + 1][2]["0|50"] = threshold % 10
        else:
            local_facts[first_fact + 1][2]["0|50"] = threshold

        local_actions[0][0] = "build"
        local_actions[0][1]["Buildable"] = params["Buildable"]

    elif type == "research":
        fact_length += 1

        local_facts[first_fact][0] = "can-research"
        local_facts[first_fact][2]["TechId"] = params["TechId"]
        local_actions[0][0] = "research"
        local_actions[0][1]["TechId"] = params["TechId"]

    elif type == "strategic_number":
        fact_length += 1
        local_facts[first_fact][0] = "true"
        action_length = 2
        local_actions[0][0] = "set-strategic-number"
        local_actions[0][1]["SnId"] = params["SnId"]
        local_actions[0][1]["SnValue"] = params["SnValue"]
        local_actions[1][0] = "disable-self"

    rule = [fact_length, action_length, age_required, local_facts, local_actions]

    return rule


def generate_ai():
    # print("generating")

    simple_list = []
    ai = []

    if villager_preset:
        # build villagers
        temp = generate_simple()
        temp[0] = "train"
        temp[1]["Trainable"] = "83"
        temp[2] = 30
        temp[3] = ["current-age  == 0"]

        simple_list.append(temp)

        temp = generate_simple()
        temp[0] = "train"
        temp[1]["Trainable"] = "83"
        temp[2] = 80
        temp[3] = ["current-age  == 1"]

        simple_list.append(temp)

    for i in range(simple_count):
        simple_list.append(generate_simple())

    for i in range(ai_length):
        ai.append(generate_rule())

    attack_rules = []
    for i in range(attack_rule_count):
        attack_rules.append(generate_attack_rule())

    DUC_search = []
    DUC_target = []
    for i in range(DUC_count):
        search = generate_DUC_search()
        target = generate_DUC_target()
        DUC_search.append(search)
        DUC_target.append(target)

    goal_rules = []
    for i in range(goal_rule_count):
        goal_rules.append(generate_goal())

    goal_actions = []
    for i in range(goal_action_count):
        goal_actions.append(generate_goal_action())

    return [
        simple_list,
        ai,
        attack_rules,
        DUC_search,
        DUC_target,
        goal_rules,
        goal_actions,
    ]


def mutate_ai(ai, mutation_chance):
    local = copy.deepcopy(ai)

    while local == ai:
        remove_list = []
        add_list = []

        for i in range(len(ai[0])):
            local[0][i] = mutate_simple(ai[0][i], mutation_chance)

            if allow_complex:
                if random.random() < mutation_chance / 2:
                    add_list.append(simple_to_complex(local[0][i]))
                    remove_list.append(local[0][i])

        for i in range(len(remove_list)):
            local[0].remove(remove_list[i])

        for i in range(4):
            if random.random() < mutation_chance:
                s = generate_simple()
                local[0].append(s)

        if random.random() < mutation_chance / 2:
            local[0].remove(random.choice(local[0]))

        for i in range(len(ai[1])):
            local[1][i] = mutate_rule(ai[1][i], mutation_chance)

        if random.random() < mutation_chance / 2:
            local[1].append(generate_rule())
        if random.random() < mutation_chance / 2:
            if len(local[1]) > 0:
                local[1].remove(random.choice(local[1]))

        for i in range(len(ai[2])):
            local[2][i] = mutate_attack_rule(ai[2][i], mutation_chance)

        for i in range(2):
            if random.random() < mutation_chance:
                local[2].append(generate_attack_rule())

        if random.random() < mutation_chance:
            if len(local[2]) > 0:
                local[2].remove(random.choice(local[2]))

        if random.random() < mutation_chance / 3:
            random.shuffle(local[0])

        if random.random() < mutation_chance / 3:
            random.shuffle(local[1])

        if random.random() < mutation_chance / 3:
            random.shuffle(local[2])

        if random.random() < mutation_chance / 3:
            random.shuffle(local[3])

        if random.random() < mutation_chance / 3:
            random.shuffle(local[4])

        if random.random() < mutation_chance / 3:
            random.shuffle(local[5])

        if random.random() < mutation_chance / 3:
            random.shuffle(local[6])

        remove_list_1 = []
        remove_list_2 = []
        for i in range(len(local[3])):
            local[3][i] = mutate_DUC_search(ai[3][i], mutation_chance)
            local[4][i] = mutate_DUC_target(ai[4][i], mutation_chance)
            if random.random() < mutation_chance / 3:
                remove_list_1.append(local[3][i])
                remove_list_2.append(local[4][i])

            if random.random() < mutation_chance / 2:
                local[3].append(generate_DUC_search())
                local[4].append(generate_DUC_target())

        for i in range(len(remove_list_1)):
            local[3].remove(remove_list_1[i])
            local[4].remove(remove_list_2[i])

        remove_list = []
        for i in range(len(local[5])):
            local[5][i] = mutate_goal(ai[5][i], mutation_chance)
            if random.random() < mutation_chance / 3:
                remove_list.append(local[5][i])

        for i in range(2):
            if random.random() < mutation_chance / 2:
                local[5].append(generate_goal())

        for i in range(len(remove_list)):
            local[5].remove(remove_list[i])

        remove_list = []
        for i in range(len(local[6])):
            local[6][i] = mutate_goal_action(ai[6][i], mutation_chance)
            if random.random() < mutation_chance / 3:
                remove_list.append(local[6][i])

        for i in range(4):
            if random.random() < mutation_chance:
                local[6].append(generate_goal_action())

        for i in range(len(remove_list)):
            local[6].remove(remove_list[i])

        local[1] = add_list + local[1]

    return local


def crossover(ai_one, ai_two, mutation_chance):
    out1 = []
    out2 = []
    out3 = []
    out4 = []
    out5 = []
    out6 = []
    out7 = []

    for i in range(len(ai_one[0])):
        try:
            if random.random() < mutation_chance / 5:
                if random.random() < 0.5:
                    out1.append(random.choice(ai_one[0]))

                else:
                    out1.append(random.choice(ai_two[0]))

            else:
                out1.append(random.choice([ai_one[0][i], ai_two[0][i]]))

        except IndexError:
            out1.append(random.choice(ai_one[0]))

    for i in range(len(ai_one[1])):
        try:
            if random.random() < mutation_chance / 5:
                if random.random() < 0.5:
                    out2.append(random.choice(ai_one[1]))

                else:
                    out2.append(random.choice(ai_two[1]))

            else:
                out2.append(random.choice([ai_one[1][i], ai_two[1][i]]))

        except IndexError:
            out2.append(random.choice(ai_one[1]))

    for i in range(len(ai_one[2])):
        try:
            if random.random() < mutation_chance / 5:
                if random.random() < 0.5:
                    out3.append(random.choice(ai_one[2]))

                else:
                    out3.append(random.choice(ai_two[2]))

            else:
                out3.append(random.choice([ai_one[2][i], ai_two[2][i]]))

        except IndexError:
            out3.append(random.choice(ai_one[2]))

    for i in range(len(ai_one[3])):
        try:
            out4.append(random.choice([ai_one[3][i], ai_two[3][i]]))

        except IndexError:
            out4.append(random.choice(ai_one[3]))

    for i in range(len(ai_one[4])):
        try:
            out5.append(random.choice([ai_one[4][i], ai_two[4][i]]))

        except IndexError:
            out5.append(random.choice(ai_one[4]))

    for i in range(len(ai_one[5])):
        try:
            out6.append(random.choice([ai_one[5][i], ai_two[5][i]]))

        except IndexError:
            out6.append(random.choice(ai_one[5]))

    for i in range(len(ai_one[6])):
        try:
            out7.append(random.choice([ai_one[6][i], ai_two[6][i]]))

        except IndexError:
            out7.append(random.choice(ai_one[6]))

    return [out1, out2, out3, out4, out5, out6, out7]


def write_ai(ai, ai_name):
    f = open(local_drive + ai_name + ".per", "w+")

    # default = "(defrule\n(true)\n=>\n(set-strategic-number sn-cap-civilian-builders -1)\n(set-strategic-number sn-cap-civilian-gatherers 0)\n(set-strategic-number sn-cap-civilian-explorers 0)\n(set-strategic-number sn-initial-exploration-required 0)\n(set-strategic-number sn-maximum-food-drop-distance -2)\n(set-strategic-number sn-maximum-gold-drop-distance -2)\n(set-strategic-number sn-maximum-hunt-drop-distance -2)\n(set-strategic-number sn-maximum-stone-drop-distance -2)\n(set-strategic-number sn-maximum-wood-drop-distance -2)\n(set-strategic-number sn-disable-villager-garrison 3)\n(disable-self))\n\n"

    if "self" in ai_name:
        default = "(defconst selfPlayerID 2)\n(defconst enemyPlayerID 1)\n\n"
    else:
        default = "(defconst selfPlayerID 1)\n(defconst enemyPlayerID 2)\n\n"

    default += "(defrule\n(true)\n=>\n(set-strategic-number sn-cap-civilian-explorers 0)\n(set-strategic-number sn-initial-exploration-required 10)\n(disable-self))\n\n"
    # default = ""

    if force_house:
        default += "(defrule \n(building-type-count-total town-center > 0)\n(housing-headroom < 5)\n(population-headroom > 0)\n(can-build house)\n=>\n(build house))\n\n"

    if force_age_up:
        default += "(defrule\n(true)\n=>\n(research 101))\n(defrule\n(true)\n=>\n(research 102))\n\n"

    if force_imperial_age:
        default += "(defrule\n(true)\n=>\n(research 103))\n"

    if force_barracks:
        default += "(defrule\n	(can-build barracks)\n	(building-type-count barracks < 1)\n=>\n	(build barracks)\n)\n\n"

    if force_resign:
        # default += "(defrule\n\t(unit-type-count villager < 15)\n\t(current-age >= feudal-age)\n=>\n\t(resign)\n\t(disable-self))\n\n"
        # default += "(defrule\n\t(building-type-count town-center < 1)\n\t(current-age < feudal-age)\n=>\n\t(resign)\n\t(disable-self))\n\n"
        default += "\n" + RESIGN_RULE + "\n"

    if force_scout:
        default += "\n(defrule\n\t(true)\n=>\n\t(set-strategic-number sn-total-number-explorers 1)\n\t(set-strategic-number sn-number-explore-groups 1)\n\t(up-send-scout 101 1)\n\t(disable-self)\n)\n\n"

    f.write(default)

    for i in range(len(ai[5])):
        f.write(str(ai[5][i]))

    for i in range(len(ai[0])):
        c = str(ai[0][i])  # ai[0][i] is a Simple object
        f.write(c)

    for i in range(len(ai[6])):
        f.write(write_goal_action(ai[6][i]))

    if allow_attack_rules:
        for i in range(len(ai[2])):
            c = str(ai[2][i])  # ai[2][i] is an AttackRule object
            f.write(c)

    if allow_DUC:
        for i in range(len(ai[3])):
            c = str(ai[3][i])  # ai[3][i] is a DUCSearch object
            f.write(c)
            c = write_DUC_target(ai[4][i])
            f.write(c)

    if allow_complex:
        for i in range(len(ai[1])):
            c = write_rule(ai[1][i])
            f.write(c)

    f.close()


def save_ai(ai, file):
    saved = False

    while not saved:
        try:
            temp = {"lazy": ai}

            with open("AI/" + file + ".txt", "w+") as outfile:
                json.dump(temp, outfile)

            saved = True

        except KeyboardInterrupt:
            print("saving!")
            saved = False


def read_ai(file):
    with open("AI/" + file + ".txt") as json_file:
        data = json.load(json_file)

    out = data["lazy"]

    return out


def generate_goal_action():
    goal_1 = random.randint(1, 40)
    goal_2 = random.randint(1, 40)
    goal_3 = random.randint(1, 40)

    value_1 = random.randint(0, 1)
    value_2 = random.randint(0, 1)
    value_3 = random.randint(0, 1)

    action = []
    for i in range(3):
        temp = generate_action()

        while temp[0] == "set-strategic-number":
            temp = generate_action()

        action.append(temp)

    used_goals = random.randint(1, 3)
    used_actions = random.randint(1, 3)

    return [
        [goal_1, goal_2, goal_3],
        [value_1, value_2, value_3],
        action,
        [used_goals, used_actions],
    ]


def mutate_goal_action(goal_action, mutation_chance):
    local = copy.deepcopy(goal_action)

    goals = local[0]

    values = local[1]

    action = local[2]

    count = local[3]

    for i in range(len(goals)):
        if random.random() < mutation_chance:
            goals[i] = random.randint(1, 40)

    for i in range(len(values)):
        if random.random() < mutation_chance:
            values[i] = random.randint(0, 1)

    for i in range(len(action)):
        action[i] = mutate_action(action[i], mutation_chance)
        if action[i][0] == "set-strategic-number":
            action[i] = mutate_action(action[i], mutation_chance)

    for i in range(len(count)):
        if random.random() < mutation_chance:
            count[i] = random.randint(1, 3)

    return [goals, values, action, count]


def write_goal_action(goal_action):
    goals = goal_action[0]

    values = goal_action[1]

    action = goal_action[2]

    count = goal_action[3]

    string = ""
    string += "\n"  # + age_required[0] + "\n"
    string += "(defrule"

    for i in range(count[0]):
        string += "\n\t(goal " + str(goals[i]) + " " + str(values[i]) + ")"

    string += "\n=>\n\t"

    string += write_action(action, count[1])

    string += ")\n\n"

    return string


def generate_simple() -> Simple:
    type = random.choice(
        ["train", "research", "strategic_number", "build", "build-forward"]
    )
    goal = random.randint(1, 40)
    use_goal = random.choice([True, False])
    requirement = random.choice(
        TRAINABLE + BUILDABLE + PARAMETERS["TechId"].split(";") + [""]
    )
    params = generate_parameters()
    strategic_numbers = generate_sn_values()
    threshold = random.randint(0, 200)
    if (
        settings.force_castle_age_units
        and params["Trainable"] != "villager"
        and type == "train"
    ):
        age_required = ["current-age  >= 3"]
    else:
        age_required = random.choice(
            [
                [""],
                ["current-age > 0"],
                ["current-age != 0"],
                ["current-age == 0"],
                ["current-age >= 0"],
                ["current-age < 0"],
                ["current-age <= 1"],
                ["current-age > 1"],
                ["current-age == 1"],
                ["current-age >= 1"],
                ["current-age < 1"],
                ["current-age <= 1"],
                ["current-age != 1"],
                ["current-age <= 2"],
                ["current-age > 2"],
                ["current-age == 2"],
                ["current-age >= 2"],
                ["current-age < 2"],
                ["current-age <= 3"],
                ["current-age != 3"],
                ["current-age <= 3"],
                ["current-age > 3"],
                ["current-age == 3"],
                ["current-age >= 3"],
                ["current-age < 3"],
                ["current-age <= 3"],
                ["current-age != 3"],
            ]
        )

    gametime = random.randint(0, 7200)
    requirement_count = random.randint(0, 10)

    return Simple(
        type,
        params,
        threshold,
        age_required,
        requirement,
        requirement_count,
        gametime,
        strategic_numbers,
        goal,
        use_goal,
    )


def mutate_simple(simple: Simple, mutation_chance: float) -> Simple:
    if random.random() < mutation_chance:
        if allow_units:
            simple.type = random.choice(
                ["train", "research", "strategic_number", "build", "build-forward"]
            )
        else:
            simple.type = random.choice(
                ["research", "strategic_number", "build", "build-forward"]
            )

    simple.parameters = mutate_parameters(simple.parameters, mutation_chance)
    simple.strategic_numbers = mutate_sn_values(
        simple.strategic_numbers, mutation_chance
    )

    if random.random() < mutation_chance:
        if random.random() < 0.25:
            simple.threshold = random.randint(0, 200)
        else:
            simple.threshold += random.randint(-10, 10)

    if (
        settings.force_castle_age_units
        and simple.parameters["Trainable"] != "villager"
        and simple.type == "train"
    ):
        simple.age_required = ["current-age  >= 2"]
    elif random.random() < mutation_chance:
        simple.age_required = random.choice(
            [
                [""],
                ["current-age > 0"],
                ["current-age  != 0"],
                ["current-age  == 0"],
                ["current-age  >= 0"],
                ["current-age < 0"],
                ["current-age  <= 1"],
                ["current-age > 1"],
                ["current-age  == 1"],
                ["current-age  >= 1"],
                ["current-age < 1"],
                ["current-age  <= 1"],
                ["current-age  != 1"],
                ["current-age  <= 2"],
                ["current-age > 2"],
                ["current-age  == 2"],
                ["current-age  >= 2"],
                ["current-age < 2"],
                ["current-age  <= 3"],
                ["current-age  != 3"],
                ["current-age  <= 3"],
                ["current-age > 3"],
                ["current-age  == 3"],
                ["current-age  >= 3"],
                ["current-age < 3"],
                ["current-age  <= 3"],
                ["current-age  != 3"],
            ]
        )

    if random.random() < mutation_chance:
        simple.requirement = random.choice(
            TRAINABLE + BUILDABLE + PARAMETERS["TechId"].split(";")
        )

    if random.random() < mutation_chance:
        if random.random() < 0.25:
            simple.game_time = random.randint(0, 7200)
        else:
            simple.game_time += random.randint(-100, 100)

    if random.random() < mutation_chance:
        if random.random() < 0.25:
            simple.requirement_count = random.randint(0, 10)
        else:
            simple.requirement_count += random.randint(-1, 1)

    if random.random() < mutation_chance:
        simple.goal = random.randint(1, 40)

    if random.random() < mutation_chance:
        simple.use_goal = random.choice([True, False])

    return simple


def generate_attack_rule() -> AttackRule:
    type = random.choice(["Attack", "Retreat", "Retreat to"])
    retreat_unit = random.choice(TRAINABLE)
    retreat_to = random.choice(BUILDABLE)

    age_required = random.choice(
        [
            "",
            "current-age > 0",
            "current-age != 0",
            "current-age == 0",
            "current-age >= 0",
            "current-age < 0",
            "current-age <= 1",
            "current-age > 1",
            "current-age == 1",
            "current-age >= 1",
            "current-age < 1",
            "current-age <= 1",
            "current-age != 1",
            "current-age <= 2",
            "current-age > 2",
            "current-age == 2",
            "current-age >= 2",
            "current-age < 2",
            "current-age <= 3",
            "current-age != 3",
            "current-age <= 3",
            "current-age > 3",
            "current-age == 3",
            "current-age >= 3",
            "current-age < 3",
            "current-age <= 3",
            "current-age != 3",
        ]
    )

    enemy_age_required = random.choice(
        [
            "",
            "players-current-age any-enemy > 0",
            "players-current-age any-enemy != 0",
            "players-current-age any-enemy == 0",
            "players-current-age any-enemy >= 0",
            "players-current-age any-enemy < 0",
            "players-current-age any-enemy <= 1",
            "players-current-age any-enemy > 1",
            "players-current-age any-enemy == 1",
            "players-current-age any-enemy >= 1",
            "players-current-age any-enemy < 1",
            "players-current-age any-enemy <= 1",
            "players-current-age any-enemy != 1",
            "players-current-age any-enemy <= 2",
            "players-current-age any-enemy > 2",
            "players-current-age any-enemy == 2",
            "players-current-age any-enemy >= 2",
            "players-current-age any-enemy < 2",
            "players-current-age any-enemy <= 3",
            "players-current-age any-enemy != 3",
            "players-current-age any-enemy <= 3",
            "players-current-age any-enemy > 3",
            "players-current-age any-enemy == 3",
            "players-current-age any-enemy >= 3",
            "players-current-age any-enemy < 3",
            "players-current-age any-enemy <= 3",
            "players-current-age any-enemy != 3",
        ]
    )

    population1 = PopulationCondition(
        random.choice(
            [
                "population",
                "civilian-population",
                "military-population",
                "defend-soldier-count",
                "",
            ]
        ),
        random.choice(["<", ">", "==", "!=", "<=", ">="]),
        random.randint(0, 200),
    )

    population2 = PopulationCondition(
        random.choice(
            [
                "population",
                "civilian-population",
                "military-population",
                "defend-soldier-count",
                "",
            ]
        ),
        random.choice(["<", ">", "==", "!=", "<=", ">="]),
        random.randint(0, 200),
    )

    gametime = GameTimeCondition(
        random.choice(["<", ">", "==", "!=", "<=", ">=", ""]),
        random.randint(0, 7200),
    )

    goal = random.randint(1, 40)
    use_goal = random.choice([True, False])

    # set-strategic-number sn-percent-attack-soldiers
    attack_percent = random.randint(0, 100)

    return AttackRule(
        type,
        age_required,
        enemy_age_required,
        population1,
        population2,
        gametime,
        retreat_unit,
        attack_percent,
        retreat_to,
        goal,
        use_goal,
    )


def mutate_attack_rule(rule: AttackRule, mutation_chance: float) -> AttackRule:
    if random.random() < mutation_chance:
        rule.type = random.choice(["Attack", "Retreat", "Retreat to"])
    if random.random() < mutation_chance:
        rule.retreat_unit = random.choice(TRAINABLE)
    if random.random() < mutation_chance:
        rule.retreat_to = random.choice(BUILDABLE)
    if random.random() < mutation_chance:
        rule.age_required = random.choice(
            [
                "",
                "current-age > 0",
                "current-age != 0",
                "current-age == 0",
                "current-age >= 0",
                "current-age < 0",
                "current-age <= 1",
                "current-age > 1",
                "current-age == 1",
                "current-age >= 1",
                "current-age < 1",
                "current-age <= 1",
                "current-age != 1",
                "current-age <= 2",
                "current-age > 2",
                "current-age == 2",
                "current-age >= 2",
                "current-age < 2",
                "current-age <= 3",
                "current-age != 3",
                "current-age <= 3",
                "current-age > 3",
                "current-age == 3",
                "current-age >= 3",
                "current-age < 3",
                "current-age <= 3",
                "current-age != 3",
            ]
        )
    if random.random() < mutation_chance:
        rule.enemy_age_required = random.choice(
            [
                "",
                "players-current-age any-enemy > 0",
                "players-current-age any-enemy != 0",
                "players-current-age any-enemy == 0",
                "players-current-age any-enemy >= 0",
                "players-current-age any-enemy < 0",
                "players-current-age any-enemy <= 1",
                "players-current-age any-enemy > 1",
                "players-current-age any-enemy == 1",
                "players-current-age any-enemy >= 1",
                "players-current-age any-enemy < 1",
                "players-current-age any-enemy <= 1",
                "players-current-age any-enemy != 1",
                "players-current-age any-enemy <= 2",
                "players-current-age any-enemy > 2",
                "players-current-age any-enemy == 2",
                "players-current-age any-enemy >= 2",
                "players-current-age any-enemy < 2",
                "players-current-age any-enemy <= 3",
                "players-current-age any-enemy != 3",
                "players-current-age any-enemy <= 3",
                "players-current-age any-enemy > 3",
                "players-current-age any-enemy == 3",
                "players-current-age any-enemy >= 3",
                "players-current-age any-enemy < 3",
                "players-current-age any-enemy <= 3",
                "players-current-age any-enemy != 3",
            ]
        )
    if random.random() < mutation_chance:
        rule.population1.type = random.choice(
            [
                "population",
                "civilian-population",
                "military-population",
                "defend-soldier-count",
                "",
            ]
        )
    if random.random() < mutation_chance:
        rule.population1.comparison = random.choice(["<", ">", "==", "!=", "<=", ">="])
    if random.random() < mutation_chance:
        rule.population1.amount = random.randint(0, 200)
    if random.random() < mutation_chance:
        rule.population2.type = random.choice(
            [
                "population",
                "civilian-population",
                "military-population",
                "defend-soldier-count",
                "",
            ]
        )
    if random.random() < mutation_chance:
        rule.population2.comparison = random.choice(["<", ">", "==", "!=", "<=", ">="])
    if random.random() < mutation_chance:
        rule.population2.amount = random.randint(0, 200)
    if random.random() < mutation_chance:
        rule.game_time.comparison = random.choice(
            ["<", ">", "==", "!=", "<=", ">=", ""]
        )
    if random.random() < mutation_chance:
        rule.game_time.amount = random.randint(0, 7200)
    if random.random() < mutation_chance:
        rule.attack_percent = random.randint(0, 100)
    if random.random() < mutation_chance:
        rule.goal = random.randint(1, 40)
    if random.random() < mutation_chance:
        rule.use_goal = random.choice([True, False])

    # if goal == False or goal == True or goal == "FALSE" or goal == "TRUE":
    #     goal = 1

    return rule


def generate_duc_search() -> DUCSearch:
    self_selected = random.choice(PLAYER_LIST)
    self_selected_max = random.randint(0, 40)
    selected = random.choice(PLAYER_LIST)
    selected_max = random.randint(0, 40)
    distance_check = random.choice([True, False])
    used_filters = random.randint(0, 5)
    filters = [
        Filter(
            random.randint(-1, 84),
            random.choice(SIMPLE_COMPARE),
            random.randint(-5, 100),
        )
        for _ in range(7)
    ]
    group_id = random.randint(0, 9)

    return DUCSearch(
        self_selected,
        self_selected_max,
        used_filters,
        filters,
        group_id,
        selected,
        selected_max,
        distance_check,
    )


def mutate_duc_search(search: DUCSearch, mutation_chance: float) -> DUCSearch:
    if random.random() < mutation_chance:
        search.selected = random.choice(PLAYER_LIST)
    if random.random() < mutation_chance:
        if random.random() < 0.25:
            search.selected_max = random.randint(0, 40)
        else:
            search.selected_max += random.randint(-5, 5)
    if random.random() < mutation_chance:
        search.distance_check = random.choice([True, False])
    if random.random() < mutation_chance:
        search.self_selected = random.choice(PLAYER_LIST)
    if random.random() < mutation_chance:
        if random.random() < 0.25:
            search.self_selected_max = random.randint(0, 40)
        else:
            search.self_selected_max += random.randint(-5, 5)
    if random.random() < mutation_chance:
        search.used_filters = random.randint(0, 5)
    for filter in search.filters:
        if random.random() < mutation_chance:
            filter.object = random.randint(-1, 84)
        if random.random() < mutation_chance:
            filter.compare = random.choice(SIMPLE_COMPARE)
        if random.random() < mutation_chance:
            filter.value = random.randint(-5, 100)
        else:
            filter.value += random.randint(-5, 5)
    if random.random() < mutation_chance:
        search.group_id = random.randint(0, 9)

    return search


def generate_DUC_target():
    selected = random.choice(PLAYER_LIST)
    selected_max = random.randint(0, 40)

    used_filters = random.randint(0, 5)

    filters = []

    for i in range(7):
        filter_object = random.randint(-1, 84)
        filter_compare = random.choice(SIMPLE_COMPARE)
        filter_value = random.randint(-5, 100)

        filters.append([filter_object, filter_compare, filter_value])

    group_id = random.randint(0, 9)

    action = random.randint(0, 20)
    positon = random.randint(0, 13)

    targeted_player = random.randint(1, 2)
    target_position = random.choice([True, False])

    formation = random.choice(FORMATIONS)
    stance = random.randint(-1, 3)

    timer_id = random.randint(1, 50)
    timer_time = random.randint(0, 2000)

    goal = random.randint(1, 40)
    use_goal = random.choice([True, False])

    return [
        selected,
        selected_max,
        used_filters,
        filters,
        group_id,
        action,
        positon,
        targeted_player,
        target_position,
        formation,
        stance,
        timer_id,
        timer_time,
        goal,
        use_goal,
    ]


def mutate_DUC_target(target, mutation_chance):
    selected = target[0]
    selected_max = target[1]
    used_filters = target[2]
    filters = target[3].copy()
    group_id = target[4]
    action = target[5]
    positon = target[6]
    targeted_player = target[7]
    target_position = target[8]
    formation = target[9]
    stance = target[10]
    timer_id = target[11]
    timer_time = target[12]
    if len(target) > 13:
        goal = target[13]
        use_goal = target[14]
    else:
        goal = 1
        use_goal = False

    if random.random() < mutation_chance:
        selected = random.choice(PLAYER_LIST)

    if random.random() < mutation_chance:
        if random.random() < 0.25:
            selected_max = random.randint(0, 40)
        else:
            selected_max += random.randint(-5, 5)

    if random.random() < mutation_chance:
        used_filters = random.randint(0, 5)

    for i in range(len(filters)):
        if random.random() < mutation_chance:
            filters[i][0] = random.randint(-1, 84)

        if random.random() < mutation_chance:
            filters[i][1] = random.choice(SIMPLE_COMPARE)

        if random.random() < mutation_chance:
            if random.random() < 0.25:
                filters[i][2] = random.randint(-5, 100)
            else:
                filters[i][2] += random.randint(-5, 5)

    if random.random() < mutation_chance:
        group_id = random.randint(0, 9)

    if random.random() < mutation_chance:
        action = random.randint(0, 20)

    if random.random() < mutation_chance:
        positon = random.randint(0, 13)

    if random.random() < mutation_chance:
        targeted_player = random.randint(1, 2)

    if random.random() < mutation_chance:
        target_position = random.choice([True, False])

    if random.random() < mutation_chance:
        formation = random.choice(FORMATIONS)

    if random.random() < mutation_chance:
        stance = random.randint(-1, 3)

    if random.random() < mutation_chance:
        timer_id = random.randint(1, 50)

    if random.random() < mutation_chance:
        if random.random() < 0.25:
            timer_time = random.randint(0, 2000)
        else:
            timer_time += random.randint(-100, 100)

    if random.random() < mutation_chance:
        goal = random.randint(1, 40)

    if random.random() < mutation_chance:
        use_goal = random.choice([True, False])

    return [
        selected,
        selected_max,
        used_filters,
        filters,
        group_id,
        action,
        positon,
        targeted_player,
        target_position,
        formation,
        stance,
        timer_id,
        timer_time,
        goal,
        use_goal,
    ]


def write_DUC_target(target):
    selected = target[0]
    selected_max = target[1]
    used_filters = target[2]
    filters = target[3]
    group_id = target[4]
    action = target[5]
    position = target[6]
    targeted_player = target[7]
    target_position = target[8]
    formation = target[9]
    stance = target[10]
    timer_id = target[11]
    if timer_id == 0:
        timer_id == 1
    timer_time = target[12]
    if len(target) > 13:
        goal = target[13]
        use_goal = target[14]
    else:
        goal = 1
        use_goal = False

    used_const = "selfPlayerID"
    if targeted_player == 2:
        used_const = "enemyPlayerID"

    string = (
        "\n(defrule\n\t(true)\n=>\n\t(enable-timer "
        + str(timer_id)
        + " "
        + str(timer_time)
        + " )\n\t(disable-self))\n"
    )

    string += (
        "\n(defrule\n\t(true)\n=>\n\t(up-full-reset-search)\n\t(up-reset-filters)\n\t(set-strategic-number 251 "
        + used_const
        + ")\n\t(set-strategic-number 249 "
        + used_const
        + "))\n"
    )
    string += (
        "\n(defrule\n\t(true)\n=>\n\t(up-get-group-size c: "
        + str(group_id)
        + " 51)\n\t(up-set-group 1 c: "
        + str(group_id)
        + ")\n"
    )

    if not target_position:
        string += (
            "\t(up-find-remote c: "
            + str(selected)
            + " c: "
            + str(selected_max)
            + "))\n\n"
        )

        if used_filters > 0:
            string += "\n(defrule\n\t(true)\n=>\n"

            for i in range(used_filters):
                filter_object = filters[i][0]
                filter_compare = filters[i][1]
                filter_value = filters[i][2]

                string += (
                    "\t(up-remove-objects 2 "
                    + str(filter_object)
                    + " "
                    + str(filter_compare)
                    + " "
                    + str(filter_value)
                    + ")\n"
                )

            string += ")"
    else:
        string += ")"

    if use_goal and not target_position:
        string += (
            "\n(defrule\n\t(timer-triggered "
            + str(timer_id)
            + ")"
            + "\n\t(goal "
            + str(goal)
            + " 1)"
            + "\n\t(up-compare-goal 51 > 0)\n=>\n\t(up-target-objects 0 "
            + str(action)
            + " "
            + str(formation)
            + " "
            + str(stance)
            + ")"
        )
    elif use_goal and target_position:
        string += (
            "\n\n(defrule\n\t(timer-triggered "
            + str(timer_id)
            + ")"
            + "\n\t(goal "
            + str(goal)
            + " 1)"
            + "\n\t(up-compare-goal 51 > 0)\n=>\n\t(up-get-point "
            + str(position)
            + " 52)\n\t(up-target-point 52 "
            + str(action)
            + " "
            + str(formation)
            + " "
            + str(stance)
            + ")"
        )
    elif not use_goal and not target_position:
        string += (
            "\n(defrule\n\t(timer-triggered "
            + str(timer_id)
            + ")"
            + "\n\t(up-compare-goal 51 > 0)\n=>\n\t(up-target-objects 0 "
            + str(action)
            + " "
            + str(formation)
            + " "
            + str(stance)
            + ")"
        )
    else:
        string += (
            "\n\n(defrule\n\t(timer-triggered "
            + str(timer_id)
            + ")"
            + "\n\t(up-compare-goal 51 > 0)\n=>\n\t(up-get-point "
            + str(position)
            + " 52)\n\t(up-target-point 52 "
            + str(action)
            + " "
            + str(formation)
            + " "
            + str(stance)
            + ")"
        )

    string += "\n\t(enable-timer " + str(timer_id) + " " + str(timer_time) + "))\n\n"

    string += "(defrule\n\t(true)\n\t=>\n\t(up-full-reset-search)\n\t(up-reset-filters)\n\t(set-strategic-number 251 enemyPlayerID)\n\t(set-strategic-number 249 enemyPlayerID))"

    return string
