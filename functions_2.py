import copy
import json
import random
import re
from typing import TypeVar

import settings
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
    AI,
    Action,
    AttackRule,
    DUCSearch,
    DUCTarget,
    Fact,
    Filter,
    GameTimeCondition,
    Goal,
    GoalAction,
    GoalFact,
    PopulationCondition,
    Rule,
    Simple,
)

T = TypeVar("T")

if settings.allow_towers:
    PARAMETERS["Buildable"] += ";watch-tower;guard-tower;keep"

with open("resign.txt", "r", encoding="utf-8") as r:
    RESIGN_RULE = r.read()


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
        parameters = {
            x[0]: x[1] for param in f.readlines() if len(x := param.split(",")) > 1
        }
    print(parameters)
    return parameters


def mutate_parameters(
    parameters: dict[str, str | int], mutation_chance: float
) -> dict[str, str | int]:
    out = copy.deepcopy(parameters)
    for key in parameters:
        mutation_rules = PARAMETERS[key]
        if "|" in mutation_rules:
            if random.random() < mutation_chance:
                out[key] = random.randint(*tuple(map(int, mutation_rules.split("|"))))
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
            out[key] = random.randint(*tuple(map(int, mutation_rules.split("|"))))
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
                out[key] = random.randint(*tuple(map(int, mutation_rules.split("|"))))
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
    fact_length = random.randint(1, settings.max_fact_length)
    action_length = random.randint(1, settings.max_action_length)
    # age_required = random.choice(
    #     [
    #         [
    #             "",
    #             "",
    #             "#load-if-not-defined DARK-AGE-END",
    #             "#end-if",
    #             "#load-if-not-defined FEUDAL-AGE-END",
    #             "#end-if",
    #             "#load-if-not-defined CASTLE-AGE-END",
    #             "#end-if",
    #             "#load-if-not-defined IMPERIAL-AGE-START",
    #             "#end-if",
    #         ]
    #     ]
    # )
    age_required = ["", ""]
    local_facts = [generate_fact() for _ in range(settings.max_fact_length)]
    local_actions = [generate_action() for _ in range(settings.max_fact_length)]

    return Rule(fact_length, action_length, age_required, local_facts, local_actions)


def mutate_rule(rule: Rule, mutation_chance: float) -> Rule:
    if random.random() < mutation_chance:
        rule.fact_length = random.randint(1, settings.max_fact_length)
    if random.random() < mutation_chance:
        rule.action_length = random.randint(1, settings.max_action_length)
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


def simple_to_complex(simple: Simple) -> Rule:
    rule = generate_rule()
    for fact in rule.local_facts:
        fact.is_not = 0
        fact.and_or = "and"

    rule.action_length = 1
    rule.fact_length = 0

    # fact = [fact_name, is_not, params, and_or]
    first_fact = 0

    if simple.age_required:
        rule.fact_length += 1
        rule.local_facts[first_fact].fact_name = "current-age"
        simple.age_required[0] = re.sub(r" {2,}", " ", simple.age_required[0])

        temp = simple.age_required[0].split()
        rule.local_facts[first_fact].parameters["compareOp"] = temp[1]
        if temp[2] in {"0", "1", "2", "3", "4", "5"}:
            rule.local_facts[first_fact].parameters["Age"] = temp[2]
        else:
            rule.local_facts[first_fact].parameters["Age"] = "2"
        first_fact += 1

    if simple.type == "train":
        rule.fact_length += 2

        rule.local_facts[first_fact].fact_name = "can-train"
        rule.local_facts[first_fact].parameters["UnitId"] = simple.parameters[
            "Trainable"
        ]

        rule.local_facts[first_fact + 1].fact_name = "unit-type-count"
        rule.local_facts[first_fact + 1].parameters["compareOp"] = "<"
        rule.local_facts[first_fact + 1].parameters["UnitId"] = simple.parameters[
            "Trainable"
        ]
        rule.local_facts[first_fact + 1].parameters["0|50"] = simple.threshold
        rule.local_actions[0].action_name = "train"
        rule.local_actions[0].parameters["Trainable"] = simple.parameters["Trainable"]

    elif simple.type == "build":
        rule.fact_length += 2

        rule.local_facts[first_fact].fact_name = "can-build"
        rule.local_facts[first_fact].parameters["BuildingId"] = simple.parameters[
            "Buildable"
        ]

        rule.local_facts[first_fact + 1].fact_name = "building-type-count"
        rule.local_facts[first_fact + 1].parameters["compareOp"] = "<"
        rule.local_facts[first_fact + 1].parameters["BuildingId"] = simple.parameters[
            "Buildable"
        ]

        if simple.parameters["Buildable"] != "farm":
            rule.local_facts[first_fact + 1].parameters["0|50"] = simple.threshold % 10
        else:
            rule.local_facts[first_fact + 1].parameters["0|50"] = simple.threshold

        rule.local_actions[0].action_name = "build"
        rule.local_actions[0].parameters["Buildable"] = simple.parameters["Buildable"]

    elif simple.type == "research":
        rule.fact_length += 1
        rule.local_facts[first_fact].fact_name = "can-research"
        rule.local_facts[first_fact].parameters["TechId"] = simple.parameters["TechId"]
        rule.local_actions[0].action_name = "research"
        rule.local_actions[0].parameters["TechId"] = simple.parameters["TechId"]

    elif simple.type == "strategic_number":
        rule.fact_length += 1
        rule.local_facts[first_fact].fact_name = "true"
        rule.action_length = 2
        rule.local_actions[0].action_name = "set-strategic-number"
        rule.local_actions[0].parameters["SnId"] = simple.parameters["SnId"]
        rule.local_actions[0].parameters["SnValue"] = simple.parameters["SnValue"]
        rule.local_actions[1].action_name = "disable-self"

    return rule


def generate_ai() -> AI:
    simple_list: list[Simple] = []
    if settings.villager_preset:
        # build villagers
        temp = generate_simple()
        temp.type = "train"
        temp.parameters["Trainable"] = "83"
        temp.threshold = 30
        temp.age_required = ["current-age == 0"]

        simple_list.append(temp)

        temp = generate_simple()
        temp.type = "train"
        temp.parameters["Trainable"] = "83"
        temp.threshold = 80
        temp.age_required = ["current-age == 1"]

        simple_list.append(temp)

    simple_list.extend([generate_simple() for _ in range(settings.simple_count)])

    ai = [generate_rule() for _ in range(settings.ai_length)]
    attack_rules = [generate_attack_rule() for _ in range(settings.attack_rule_count)]
    duc_search = [generate_duc_search() for _ in range(settings.DUC_count)]
    duc_target = [generate_duc_target() for _ in range(settings.DUC_count)]
    goal_rules = [generate_goal() for _ in range(settings.goal_rule_count)]
    goal_actions = [generate_goal_action() for _ in range(settings.goal_action_count)]

    return AI(
        simple_list,
        ai,
        attack_rules,
        duc_search,
        duc_target,
        goal_rules,
        goal_actions,
    )


def mutate_ai(ai: AI, mutation_chance: float) -> AI:
    local = copy.deepcopy(ai)

    while local == ai:
        local.simples = [
            mutate_simple(simple, mutation_chance) for simple in local.simples
        ]

        new_rules: list[Rule] = []
        if settings.allow_complex:
            for simple in local.simples:
                if random.random() < mutation_chance / 2:
                    new_rules.append(simple_to_complex(simple))
                    local.simples.remove(simple)

        for _ in range(4):
            if random.random() < mutation_chance:
                local.simples.append(generate_simple())

        if random.random() < mutation_chance / 2:
            local.simples.remove(random.choice(local.simples))

        local.rules = [mutate_rule(rule, mutation_chance) for rule in local.rules]

        if random.random() < mutation_chance / 2:
            local.rules.append(generate_rule())

        if len(local.rules) > 0:
            if random.random() < mutation_chance / 2:
                local.rules.remove(random.choice(local.rules))

        local.attack_rules = [
            mutate_attack_rule(attack_rule, mutation_chance)
            for attack_rule in local.attack_rules
        ]

        for _ in range(2):
            if random.random() < mutation_chance:
                local.attack_rules.append(generate_attack_rule())

        if len(local.attack_rules) > 0:
            if random.random() < mutation_chance:
                local.attack_rules.remove(random.choice(local.attack_rules))

        if random.random() < mutation_chance / 3:
            random.shuffle(local.simples)

        if random.random() < mutation_chance / 3:
            random.shuffle(local.rules)

        if random.random() < mutation_chance / 3:
            random.shuffle(local.attack_rules)

        if random.random() < mutation_chance / 3:
            random.shuffle(local.duc_search)

        if random.random() < mutation_chance / 3:
            random.shuffle(local.duc_target)

        if random.random() < mutation_chance / 3:
            random.shuffle(local.goal_rules)

        if random.random() < mutation_chance / 3:
            random.shuffle(local.goal_actions)

        local.rules = new_rules + local.rules

        local.duc_search = [
            mutate_duc_search(search, mutation_chance) for search in local.duc_search
        ]
        local.duc_target = [
            mutate_duc_target(target, mutation_chance) for target in local.duc_target
        ]

        num = len(local.duc_search)
        randoms = [random.random() for _ in range(num)]
        local.duc_search = [
            s for s, x in zip(local.duc_search, randoms) if x >= mutation_chance / 3
        ]
        local.duc_target = [
            t for t, x in zip(local.duc_target, randoms) if x >= mutation_chance / 3
        ]
        for _ in range(num):
            if random.random() < mutation_chance / 2:
                local.duc_search.append(generate_duc_search())
                local.duc_target.append(generate_duc_target())

        local.goal_rules = [
            mutate_goal(goal, mutation_chance) for goal in local.goal_rules
        ]
        for rule in local.goal_rules:
            if random.random() < mutation_chance / 3:
                local.goal_rules.remove(rule)
        for _ in range(2):
            if random.random() < mutation_chance / 2:
                local.goal_rules.append(generate_goal())

        local.goal_actions = [
            mutate_goal_action(goal_action, mutation_chance)
            for goal_action in local.goal_actions
        ]
        for goal_action in local.goal_actions:
            if random.random() < mutation_chance / 3:
                local.goal_actions.remove(goal_action)
        for _ in range(4):
            if random.random() < mutation_chance:
                local.goal_actions.append(generate_goal_action())

    return local


def _crossover_rule_1(
    parent_1: list[T], parent_2: list[T], mutation_chance: float
) -> list[T]:
    child: list[T] = []
    for i, _ in enumerate(parent_1):
        if random.random() < mutation_chance / 5:
            if random.random() < 0.5:
                child.append(random.choice(parent_1))
            else:
                child.append(random.choice(parent_2))
        else:
            if i >= len(parent_2):
                child.append(random.choice(parent_1))
            else:
                child.append(random.choice((parent_1[i], parent_2[i])))

    return child


def _crossover_rule_2(parent_1: list[T], parent_2: list[T]) -> list[T]:
    child: list[T] = []
    for i, _ in enumerate(parent_1):
        if i < len(parent_2):
            child.append(random.choice((parent_1[i], parent_2[i])))
        else:
            child.append(random.choice(parent_1))

    return child


def crossover(ai_1: AI, ai_2: AI, mutation_chance: float) -> AI:
    simples = _crossover_rule_1(ai_1.simples, ai_2.simples, mutation_chance)
    rules = _crossover_rule_1(ai_1.rules, ai_2.rules, mutation_chance)
    attack_rules = _crossover_rule_1(
        ai_1.attack_rules, ai_2.attack_rules, mutation_chance
    )
    duc_search = _crossover_rule_2(ai_1.duc_search, ai_2.duc_search)
    duc_target = _crossover_rule_2(ai_1.duc_target, ai_2.duc_target)
    goal_rules = _crossover_rule_2(ai_1.goal_rules, ai_2.goal_rules)
    goal_actions = _crossover_rule_2(ai_1.goal_actions, ai_2.goal_actions)

    return AI(
        simples, rules, attack_rules, duc_search, duc_target, goal_rules, goal_actions
    )


def export_ai(ai: AI, ai_name: str) -> None:
    # default = (
    #     "(defrule\n(true)\n=>\n"
    #     "(set-strategic-number sn-cap-civilian-builders -1)\n"
    #     "(set-strategic-number sn-cap-civilian-gatherers 0)\n"
    #     "(set-strategic-number sn-cap-civilian-explorers 0)\n"
    #     "(set-strategic-number sn-initial-exploration-required 0)\n"
    #     "(set-strategic-number sn-maximum-food-drop-distance -2)\n"
    #     "(set-strategic-number sn-maximum-gold-drop-distance -2)\n"
    #     "(set-strategic-number sn-maximum-hunt-drop-distance -2)\n"
    #     "(set-strategic-number sn-maximum-stone-drop-distance -2)\n"
    #     "(set-strategic-number sn-maximum-wood-drop-distance -2)\n"
    #     "(set-strategic-number sn-disable-villager-garrison 3)\n(disable-self))\n\n"
    # )
    self, enemy = (2, 1) if "self" in ai_name else (1, 2)
    default_ai = (
        f"(defconst selfPlayerID {self})\n(defconst enemyPlayerID {enemy})\n\n"
        "(defrule\n(true)\n=>\n(set-strategic-number sn-cap-civilian-explorers 0)\n"
        "(set-strategic-number sn-initial-exploration-required 10)\n(disable-self))\n\n"
    )
    if settings.force_house:
        default_ai += (
            "(defrule\n"
            "(building-type-count-total town-center > 0)\n"
            "(housing-headroom < 5)\n"
            "(population-headroom > 0)\n"
            "(can-build house)\n"
            "=>\n(build house))\n\n"
        )

    if settings.force_age_up:
        default_ai += (
            "(defrule\n(true)\n=>\n(research 101))\n"
            "(defrule\n(true)\n=>\n(research 102))\n\n"
        )

    if settings.force_imperial_age:
        default_ai += "(defrule\n(true)\n=>\n(research 103))\n"

    if settings.force_barracks:
        default_ai += (
            "(defrule\n"
            "(can-build barracks)\n"
            "(building-type-count barracks < 1)\n"
            "=>\n(build barracks)\n)\n\n"
        )

    if settings.force_resign:
        default_ai += "\n" + RESIGN_RULE + "\n"
        # ans += (
        #     "(defrule\n"
        #     "(unit-type-count villager < 15)\n"
        #     "(current-age >= feudal-age)\n"
        #     "=>\n\t(resign)\n\t(disable-self))\n\n"
        #     "(defrule\n"
        #     "(building-type-count town-center < 1)\n"
        #     "(current-age < .feudal-age)\n"
        #     "=>\n\t(resign)\n\t(disable-self))\n\n"
        # )

    if settings.force_scout:
        default_ai += (
            "\n(defrule\n(true)\n"
            "=>\n\t(set-strategic-number sn-total-number-explorers 1)"
            "\n\t(set-strategic-number sn-number-explore-groups 1)"
            "\n\t(up-send-scout 101 1)"
            "\n\t(disable-self)\n)\n\n"
        )

    with open(settings.local_drive + ai_name + ".per", "w", encoding="utf-8") as f:
        f.write(default_ai)
        for rule in ai.goal_rules:
            f.write(str(rule))
        for simple in ai.simples:
            f.write(str(simple))
        for goal_action in ai.goal_actions:
            f.write(str(goal_action))
        if settings.allow_attack_rules:
            for attack_rule in ai.attack_rules:
                f.write(str(attack_rule))
        if settings.allow_DUC:
            for search, target in zip(ai.duc_search, ai.duc_target):
                f.write(str(search))
                f.write(str(target))
        if settings.allow_complex:
            for rule in ai.rules:
                f.write(str(rule))


def save_ai(ai: AI, file_name: str) -> None:
    # ! make AI objects exportable in JSON format
    temp = {"lazy": ai}
    saved = False
    while not saved:
        try:
            with open("AI/" + file_name + ".txt", "w+", encoding="utf-8") as outfile:
                json.dump(temp, outfile)
        except KeyboardInterrupt:
            print("saving!")
            saved = False
        else:
            saved = True


def read_ai(file_name: str) -> AI:
    # ! make AI objects exportable in JSON format
    with open("AI/" + file_name + ".txt", encoding="utf-8") as json_file:
        data = json.load(json_file)
    return data["lazy"]


def generate_goal_action() -> GoalAction:
    size = 3
    goals = [random.randint(1, 40) for _ in range(size)]
    values = [random.randint(0, 1) for _ in range(size)]

    actions: list[Action] = []
    for _ in range(size):
        temp = generate_action()
        while temp.action_name == "set-strategic-number":
            temp = generate_action()
        actions.append(temp)

    used_goals = random.randint(1, 3)
    used_actions = random.randint(1, 3)

    return GoalAction(
        goals,
        values,
        actions,
        used_goals,
        used_actions,
    )


def mutate_goal_action(goal_action: GoalAction, mutation_chance: float) -> GoalAction:
    for i, _ in enumerate(goal_action.goals):
        if random.random() < mutation_chance:
            goal_action.goals[i] = random.randint(1, 40)
    for i, _ in enumerate(goal_action.values):
        if random.random() < mutation_chance:
            goal_action.values[i] = random.randint(0, 1)
    for action in goal_action.actions:
        action = mutate_action(action, mutation_chance)
        if action.action_name == "set-strategic-number":
            action = mutate_action(action, mutation_chance)
        # ? Should this be a while loop until the action name is not that?
    if random.random() < mutation_chance:
        goal_action.used_goals = random.randint(1, 3)
    if random.random() < mutation_chance:
        goal_action.used_actions = random.randint(1, 3)

    return goal_action


def generate_simple() -> Simple:
    simple_type = random.choice(
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
        and simple_type == "train"
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

    game_time = random.randint(0, 7200)
    requirement_count = random.randint(0, 10)

    return Simple(
        simple_type,
        params,
        threshold,
        age_required,
        requirement,
        requirement_count,
        game_time,
        strategic_numbers,
        goal,
        use_goal,
    )


def mutate_simple(simple: Simple, mutation_chance: float) -> Simple:
    if random.random() < mutation_chance:
        if settings.allow_units:
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
    rule_type = random.choice(["Attack", "Retreat", "Retreat to"])
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

    game_time = GameTimeCondition(
        random.choice(["<", ">", "==", "!=", "<=", ">=", ""]),
        random.randint(0, 7200),
    )

    goal = random.randint(1, 40)
    use_goal = random.choice([True, False])

    # set-strategic-number sn-percent-attack-soldiers
    attack_percent = random.randint(0, 100)

    return AttackRule(
        rule_type,
        age_required,
        enemy_age_required,
        population1,
        population2,
        game_time,
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
    for search_filter in search.filters:
        if random.random() < mutation_chance:
            search_filter.object = random.randint(-1, 84)
        if random.random() < mutation_chance:
            search_filter.compare = random.choice(SIMPLE_COMPARE)
        if random.random() < mutation_chance:
            search_filter.value = random.randint(-5, 100)
        else:
            search_filter.value += random.randint(-5, 5)
    if random.random() < mutation_chance:
        search.group_id = random.randint(0, 9)

    return search


def generate_duc_target() -> DUCTarget:
    selected = random.choice(PLAYER_LIST)
    selected_max = random.randint(0, 40)
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
    action = random.randint(0, 20)
    position = random.randint(0, 13)
    targeted_player = random.randint(1, 2)
    target_position = random.choice([True, False])
    formation = random.choice(FORMATIONS)
    stance = random.randint(-1, 3)
    timer_id = random.randint(1, 50)
    timer_time = random.randint(0, 2000)
    goal = random.randint(1, 40)
    use_goal = random.choice([True, False])

    return DUCTarget(
        selected,
        selected_max,
        used_filters,
        filters,
        group_id,
        action,
        position,
        targeted_player,
        target_position,
        formation,
        stance,
        timer_id,
        timer_time,
        goal,
        use_goal,
    )


def mutate_duc_target(target: DUCTarget, mutation_chance: float) -> DUCTarget:
    if random.random() < mutation_chance:
        target.selected = random.choice(PLAYER_LIST)
    if random.random() < mutation_chance:
        if random.random() < 0.25:
            target.selected_max = random.randint(0, 40)
        else:
            target.selected_max += random.randint(-5, 5)
    if random.random() < mutation_chance:
        target.used_filters = random.randint(0, 5)
    for target_filter in target.filters:
        if random.random() < mutation_chance:
            target_filter.object = random.randint(-1, 84)
        if random.random() < mutation_chance:
            target_filter.compare = random.choice(SIMPLE_COMPARE)
        if random.random() < mutation_chance:
            if random.random() < 0.25:
                target_filter.value = random.randint(-5, 100)
            else:
                target_filter.value += random.randint(-5, 5)
    if random.random() < mutation_chance:
        target.group_id = random.randint(0, 9)
    if random.random() < mutation_chance:
        target.action = random.randint(0, 20)
    if random.random() < mutation_chance:
        target.position = random.randint(0, 13)
    if random.random() < mutation_chance:
        target.targeted_player = random.randint(1, 2)
    if random.random() < mutation_chance:
        target.target_position = random.choice([True, False])
    if random.random() < mutation_chance:
        target.formation = random.choice(FORMATIONS)
    if random.random() < mutation_chance:
        target.stance = random.randint(-1, 3)
    if random.random() < mutation_chance:
        target.timer_id = random.randint(1, 50)
    if random.random() < mutation_chance:
        if random.random() < 0.25:
            target.timer_time = random.randint(0, 2000)
        else:
            target.timer_time += random.randint(-100, 100)
    if random.random() < mutation_chance:
        target.goal = random.randint(1, 40)
    if random.random() < mutation_chance:
        target.use_goal = random.choice([True, False])

    return target
