import random
from typing import TypeVar

from models import AI

T = TypeVar("T")


def parse_params() -> dict[str, str]:
    with open("params.csv", "r", encoding="utf-8") as f:
        parameters = {
            x[0]: x[1] for param in f.readlines() if len(x := param.split(",")) > 1
        }
    print(parameters)
    return parameters


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
