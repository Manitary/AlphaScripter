import copy
import json
import random
import re
from abc import ABC, abstractmethod
from collections import UserDict
from dataclasses import dataclass
from typing import Self

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

if settings.allow_towers:
    PARAMETERS["Buildable"] += ";watch-tower;guard-tower;keep"

with open("resign.txt", "r", encoding="utf-8") as r:
    RESIGN_RULE = r.read()


class Mutable(ABC):
    @classmethod
    @abstractmethod
    def generate(cls) -> Self:
        ...

    @abstractmethod
    def mutate(self, mutation_chance: float) -> Self:
        ...


class Parameters(Mutable, UserDict[str, str | int]):
    @classmethod
    def generate(cls) -> Self:
        out: dict[str, str | int] = {}
        for key, mutation_rules in PARAMETERS.items():
            if "|" in mutation_rules:
                out[key] = random.randint(*tuple(map(int, mutation_rules.split("|"))))
            elif ";" in mutation_rules:
                out[key] = random.choice(mutation_rules.split(";"))
            else:
                out[key] = mutation_rules

        return Parameters(out)

    def mutate(self, mutation_chance: float, in_place: bool = False) -> Self:
        out = self if in_place else copy.deepcopy(self)
        new = Parameters.generate()
        for key in out:
            if random.random() < mutation_chance:
                out[key] = new[key]

        return Parameters(out)


@dataclass
class GoalFact:
    fact_name: str
    parameters: Parameters

    def __str__(self) -> str:
        return (
            f"{self.fact_name} "
            f"{' '.join(tuple(str(self.parameters[x]) for x in FACTS[self.fact_name]))}"
        )


@dataclass
class Goal(Mutable):
    goal_id: int
    value: int
    disable: bool
    goal_num: int
    use_goal: bool
    used_facts: list[GoalFact]
    fact_count: int

    def __str__(self) -> str:
        ans = "\n(defrule"
        if self.use_goal:
            ans += f"\n\t(goal {self.goal_num} 1)"
        for i in range(self.fact_count):
            ans += f"\n\t({self.used_facts[i]})"
        ans += "\n=>\n"
        ans += f"\n\t(set-goal {self.goal_id} {self.value})"
        if self.disable:
            ans += "\n\t(disable-self)"
        ans += ")\n"

        return ans

    @classmethod
    def generate(cls) -> Self:
        goal_id = random.randint(1, 40)
        value = random.randint(0, 1)
        disable = random.choice([True, False])
        goal_num = random.randint(1, 40)
        use_goal = random.choice([True, False])
        fact_count = random.randint(1, 4)
        used_facts = [
            GoalFact(random.choice(GOAL_FACTS), Parameters.generate()) for _ in range(4)
        ]

        return Goal(goal_id, value, disable, goal_num, use_goal, used_facts, fact_count)

    def mutate(self, mutation_chance: float, in_place: bool = False) -> Self:
        goal = self if in_place else copy.deepcopy(self)
        new = Goal.generate()
        if random.random() < mutation_chance:
            goal.goal_id = new.goal_id
        if random.random() < mutation_chance:
            goal.value = new.value
        if random.random() < mutation_chance:
            goal.disable = new.disable
        if random.random() < mutation_chance:
            goal.goal_num = new.goal_num
        if random.random() < mutation_chance:
            goal.use_goal = new.use_goal
        if random.random() < mutation_chance:
            goal.fact_count = new.fact_count
        for fact in goal.used_facts:
            fact = GoalFact(
                random.choice(GOAL_FACTS),
                fact.parameters.mutate(mutation_chance, in_place=in_place),
            )

        return goal


@dataclass
class Fact(Mutable):
    fact_name: str
    is_not: int
    parameters: Parameters
    and_or: str

    def __str__(self) -> str:
        return (
            f"{self.fact_name} "
            f"{' '.join(tuple(str(self.parameters[x]) for x in FACTS[self.fact_name]))}"
        )

    @classmethod
    def generate(cls) -> Self:
        fact_name = random.choice(list(FACTS))
        is_not = random.randint(0, 1)
        params = Parameters.generate()
        and_or = random.choice(["and", "or", "nand", "nor"])

        return Fact(fact_name, is_not, params, and_or)

    def mutate(self, mutation_chance: float, in_place: bool = False) -> Self:
        fact = self if in_place else copy.deepcopy(self)
        new = Fact.generate()
        if random.random() < mutation_chance:
            fact.fact_name = new.fact_name
        if random.random() < mutation_chance:
            fact.is_not = new.is_not
        if random.random() < mutation_chance:
            fact.and_or = new.and_or
        fact.parameters = fact.parameters.mutate(mutation_chance)

        return fact


class StrategicNumbers(Mutable, UserDict[str, str | int]):
    @classmethod
    def generate(cls) -> Self:
        out: dict[str, str | int] = {}
        for key, mutation_rules in SN.items():
            if "|" in mutation_rules:
                out[key] = random.randint(*tuple(map(int, mutation_rules.split("|"))))
            elif ";" in mutation_rules:
                out[key] = random.choice(mutation_rules.split(";"))
            else:
                out[key] = mutation_rules

        return StrategicNumbers(out)

    def mutate(self, mutation_chance: float, in_place: bool = False) -> Self:
        out = self if in_place else copy.deepcopy(self)
        new = Parameters.generate()
        for key in out:
            if random.random() < mutation_chance:
                out[key] = new[key]

        return StrategicNumbers(out)


@dataclass
class Action(Mutable):
    action_name: str
    parameters: Parameters
    strategic_numbers: StrategicNumbers

    def __str__(self) -> str:
        if self.action_name == "set-strategic-number":
            return (
                f"{self.action_name}"
                f" {self.parameters[ACTIONS[self.action_name][1]]}"
                f" {self.strategic_numbers[str(self.parameters[ACTIONS[self.action_name][1]])]}"
            )
        return (
            f"{self.action_name} "
            f"{' '.join(tuple(str(self.parameters[x]) for x in ACTIONS[self.action_name]))}"
        )

    @classmethod
    def generate(cls) -> Self:
        action_name = random.choice(list(ACTIONS))
        parameters = Parameters.generate()
        strategic_numbers = StrategicNumbers.generate()

        return Action(action_name, parameters, strategic_numbers)

    def mutate(self, mutation_chance: float, in_place: bool = False) -> Self:
        action = self if in_place else copy.deepcopy(self)
        if random.random() < mutation_chance:
            action.action_name = random.choice(list(ACTIONS))
        action.parameters = action.parameters.mutate(mutation_chance)
        action.strategic_numbers = action.strategic_numbers.mutate(mutation_chance)

        return action


def _write_actions(actions: list[Action]) -> str:
    return "....\n" + "\n".join(f"({action})" for action in actions)


@dataclass
class Rule(Mutable):
    fact_length: int
    action_length: int
    age_required: list[str]
    local_facts: list[Fact]
    local_actions: list[Action]

    def __str__(self) -> str:
        ans = f"\n(defrule{self._write_facts()}\n=>{_write_actions(self.local_actions)})\n"
        if len(ans.split()) > 20:
            ans = ""
        return ans

    def _write_facts(self) -> str:
        pad = "...."
        ans = pad
        for i, fact in enumerate(self.local_facts):
            if i >= self.fact_length:
                break
            ans += "\n"
            ans += pad * i
            if i < self.fact_length - 1:
                ans += f"{pad}({fact.and_or} "
            if fact.is_not:
                ans += "(not "
            ans += f"({fact})"
            if i == self.fact_length - 1:
                ans += "\n"
                ans += ")" * i
            if fact.is_not:
                ans += ")"
        return ans

    @classmethod
    def generate(cls) -> Self:
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
        local_facts = [Fact.generate() for _ in range(settings.max_fact_length)]
        local_actions = [Action.generate() for _ in range(settings.max_fact_length)]

        return Rule(
            fact_length, action_length, age_required, local_facts, local_actions
        )

    def mutate(self, mutation_chance: float, in_place: bool = False) -> Self:
        if random.random() < mutation_chance / 5:
            return Rule.generate()

        rule = self if in_place else copy.deepcopy(self)
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
            fact = fact.mutate(mutation_chance)
        for action in rule.local_actions:
            action = action.mutate(mutation_chance)

        return rule


@dataclass
class Simple(Mutable):
    type: str
    parameters: Parameters
    threshold: int
    age_required: list[str]
    requirement: str
    requirement_count: int
    game_time: int
    strategic_numbers: StrategicNumbers
    goal: int = 1
    use_goal: bool = False

    def __str__(self) -> str:
        ans = "\n(defrule"
        if self.use_goal:
            ans += f"\n\t(goal {self.goal} 1)"
        if self.age_required[0]:
            ans += f"\n\t({self.age_required[0]})"
        if self.game_time > 0:
            ans += f"\n\t(game-time > {self.game_time})"
        if self.requirement and self.requirement != "none":
            try:
                int(self.requirement)
            except ValueError:
                ans += f"\n\t({'building-type-count-total' if self.requirement in BUILDABLE else 'unit-type-count-total'} {self.requirement} > {self.requirement_count})"
            else:
                ans += f"\n\t(up-research-status c: {self.requirement} >= 2)"
        if self.type == "train":
            ans += f"\n\t(can-train {self.parameters['Trainable']})"
            ans += f"\n\t(unit-type-count-total {self.parameters['Trainable']} < {max(0, self.threshold)})"
            ans += f"=>\n\t(train {self.parameters['Trainable']})"
        elif self.type in {"build", "build-forward"}:
            ans += f"\n\t(can-build {self.parameters['Buildable']})"
            ans += f"\n\t(building-type-count-total {self.parameters['Buildable']} < {max(0, self.threshold)})"
            ans += f"=>\n\t({self.type} {self.parameters['Buildable']})"
        elif self.type == "research":
            ans += f"\n\t(can-research {self.parameters['TechId']})"
            ans += f"=>\n\t(research {self.parameters['TechId']})"
        elif self.type == "strategic-number":
            ans += "\n\t(true)"
            ans += f"=>\n\t(set-strategic-number {self.parameters['SnId']} {self.strategic_numbers[str(self.parameters['SnId'])]})\n\t(disable-self)"
        ans += ")\n"

        return ans

    @classmethod
    def generate(cls) -> Self:
        simple_type = random.choice(
            ["train", "research", "strategic_number", "build", "build-forward"]
        )
        goal = random.randint(1, 40)
        use_goal = random.choice([True, False])
        requirement = random.choice(
            TRAINABLE + BUILDABLE + PARAMETERS["TechId"].split(";") + [""]
        )
        params = Parameters.generate()
        strategic_numbers = StrategicNumbers.generate()
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

    def mutate(self, mutation_chance: float, in_place: bool = False) -> Self:
        simple = self if in_place else copy.deepcopy(self)
        if random.random() < mutation_chance:
            if settings.allow_units:
                simple.type = random.choice(
                    ["train", "research", "strategic_number", "build", "build-forward"]
                )
            else:
                simple.type = random.choice(
                    ["research", "strategic_number", "build", "build-forward"]
                )

        simple.parameters = simple.parameters.mutate(mutation_chance)
        simple.strategic_numbers = simple.strategic_numbers.mutate(mutation_chance)

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

    def to_complex(self) -> Rule:
        rule = Rule.generate()
        for fact in rule.local_facts:
            fact.is_not = 0
            fact.and_or = "and"

        rule.action_length = 1
        rule.fact_length = 0

        # fact = [fact_name, is_not, params, and_or]
        first_fact = 0

        if self.age_required:
            rule.fact_length += 1
            rule.local_facts[first_fact].fact_name = "current-age"
            self.age_required[0] = re.sub(r" {2,}", " ", self.age_required[0])

            temp = self.age_required[0].split()
            rule.local_facts[first_fact].parameters["compareOp"] = temp[1]
            if temp[2] in {"0", "1", "2", "3", "4", "5"}:
                rule.local_facts[first_fact].parameters["Age"] = temp[2]
            else:
                rule.local_facts[first_fact].parameters["Age"] = "2"
            first_fact += 1

        if self.type == "train":
            rule.fact_length += 2

            rule.local_facts[first_fact].fact_name = "can-train"
            rule.local_facts[first_fact].parameters["UnitId"] = self.parameters[
                "Trainable"
            ]

            rule.local_facts[first_fact + 1].fact_name = "unit-type-count"
            rule.local_facts[first_fact + 1].parameters["compareOp"] = "<"
            rule.local_facts[first_fact + 1].parameters["UnitId"] = self.parameters[
                "Trainable"
            ]
            rule.local_facts[first_fact + 1].parameters["0|50"] = self.threshold
            rule.local_actions[0].action_name = "train"
            rule.local_actions[0].parameters["Trainable"] = self.parameters["Trainable"]

        elif self.type == "build":
            rule.fact_length += 2

            rule.local_facts[first_fact].fact_name = "can-build"
            rule.local_facts[first_fact].parameters["BuildingId"] = self.parameters[
                "Buildable"
            ]

            rule.local_facts[first_fact + 1].fact_name = "building-type-count"
            rule.local_facts[first_fact + 1].parameters["compareOp"] = "<"
            rule.local_facts[first_fact + 1].parameters["BuildingId"] = self.parameters[
                "Buildable"
            ]

            if self.parameters["Buildable"] != "farm":
                rule.local_facts[first_fact + 1].parameters["0|50"] = (
                    self.threshold % 10
                )
            else:
                rule.local_facts[first_fact + 1].parameters["0|50"] = self.threshold

            rule.local_actions[0].action_name = "build"
            rule.local_actions[0].parameters["Buildable"] = self.parameters["Buildable"]

        elif self.type == "research":
            rule.fact_length += 1
            rule.local_facts[first_fact].fact_name = "can-research"
            rule.local_facts[first_fact].parameters["TechId"] = self.parameters[
                "TechId"
            ]
            rule.local_actions[0].action_name = "research"
            rule.local_actions[0].parameters["TechId"] = self.parameters["TechId"]

        elif self.type == "strategic_number":
            rule.fact_length += 1
            rule.local_facts[first_fact].fact_name = "true"
            rule.action_length = 2
            rule.local_actions[0].action_name = "set-strategic-number"
            rule.local_actions[0].parameters["SnId"] = self.parameters["SnId"]
            rule.local_actions[0].parameters["SnValue"] = self.parameters["SnValue"]
            rule.local_actions[1].action_name = "disable-self"

        return rule


@dataclass
class PopulationCondition:
    type: str
    comparison: str
    amount: int

    def __bool__(self) -> bool:
        if self.comparison and self.type:
            return True
        return False

    def __str__(self) -> str:
        return f"{self.type} {self.comparison} {self.amount}"

    @classmethod
    def generate(cls) -> Self:
        return PopulationCondition(
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


@dataclass
class GameTimeCondition:
    comparison: str
    amount: int

    def __bool__(self) -> bool:
        if self.comparison:
            return True
        return False

    def __str__(self) -> str:
        return f"{self.comparison} {self.amount}"

    @classmethod
    def generate(cls) -> Self:
        return GameTimeCondition(
            random.choice(["<", ">", "==", "!=", "<=", ">=", ""]),
            random.randint(0, 7200),
        )


@dataclass
class AttackRule(Mutable):
    type: str
    age_required: str  # ? | list[str]
    enemy_age_required: str  # ? | list[str]
    population1: PopulationCondition
    population2: PopulationCondition
    game_time: GameTimeCondition
    retreat_unit: str
    attack_percent: int
    retreat_to: str
    goal: int = 1
    use_goal: bool = False

    def __str__(self) -> str:
        ans = "\n(defrule \n"
        if self.use_goal:
            ans += f"\n\t(goal {self.goal} 1)"
        ans += self._write_conditions()
        ans += "\n=>\n\t"
        ans += f"(set-strategic-number sn-percent-attack-soldiers {self.attack_percent})\n\t"
        if self.type == "Attack":
            ans += "(attack-now)"
        elif self.type == "Retreat":
            ans += "(up-reset-attack-now)\n\t(up-retreat-now)"
        elif self.type == "Retreat to":
            ans += (
                "(up-reset-attack-now)\n\t"
                f"(up-retreat-to {self.retreat_to} c: {self.retreat_unit})"
            )
        ans += "\n)"
        return ans

    def _write_conditions(self) -> str:
        ans = ""
        if self.age_required:
            ans += f"\n\t({self.age_required})\n\t"
        if self.enemy_age_required:
            ans += f"\n\t({self.enemy_age_required})\n\t"
        if self.population1:
            ans += f"({self.population1})\n\t"
        if self.population2:
            ans += f"({self.population2})\n\t"
        if self.game_time:
            ans += f"(game-time {self.game_time})\n\t"
        if not ans:
            ans = "\n\t(true)"
        return ans

    @classmethod
    def generate(cls) -> Self:
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

        population1 = PopulationCondition.generate()
        population2 = PopulationCondition.generate()
        game_time = GameTimeCondition.generate()
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

    def mutate(self, mutation_chance: float, in_place: bool = False) -> Self:
        rule = self if in_place else copy.deepcopy(self)
        new = AttackRule.generate()
        if random.random() < mutation_chance:
            rule.type = new.type
        if random.random() < mutation_chance:
            rule.retreat_unit = new.retreat_unit
        if random.random() < mutation_chance:
            rule.retreat_to = new.retreat_to
        if random.random() < mutation_chance:
            rule.age_required = new.age_required
        if random.random() < mutation_chance:
            rule.enemy_age_required = new.enemy_age_required
        if random.random() < mutation_chance:
            rule.population1.type = new.population1.type
        if random.random() < mutation_chance:
            rule.population1.comparison = new.population1.type
        if random.random() < mutation_chance:
            rule.population1.amount = new.population1.amount
        if random.random() < mutation_chance:
            rule.population2.type = new.population2.type
        if random.random() < mutation_chance:
            rule.population2.comparison = new.population2.comparison
        if random.random() < mutation_chance:
            rule.population2.amount = new.population2.amount
        if random.random() < mutation_chance:
            rule.game_time.comparison = new.game_time.comparison
        if random.random() < mutation_chance:
            rule.game_time.amount = new.game_time.amount
        if random.random() < mutation_chance:
            rule.attack_percent = new.attack_percent
        if random.random() < mutation_chance:
            rule.goal = new.goal
        if random.random() < mutation_chance:
            rule.use_goal = new.use_goal

        return rule


@dataclass
class Filter:
    object: int
    compare: str
    value: int

    def __str__(self) -> str:
        return f"{self.object} {self.compare} {self.value}"

    @classmethod
    def generate(cls) -> Self:
        return Filter(
            random.randint(-1, 84),
            random.choice(SIMPLE_COMPARE),
            random.randint(-5, 100),
        )


@dataclass
class DUCSearch(Mutable):
    self_selected: str
    self_selected_max: int
    used_filters: int
    filters: list[Filter]
    group_id: int
    selected: str
    selected_max: int
    distance_check: bool

    def __str__(self) -> str:
        used_const = "enemyPlayerID"
        ans = (
            "\n(defrule\n\t(true)\n=>"
            "\n\t(up-full-reset-search)\n\t(up-reset-filters)\n\t(set-strategic-number 251 "
            f"{used_const}"
            ")\n\t(set-strategic-number 249 "
            f"{used_const}"
            "))\n"
        )
        if self.distance_check:
            ans += (
                "\n(defrule\n\t(true)\n=>\n"
                f"\t(up-find-remote c: {self.selected} c: {self.selected_max}))\n\n"
                "\n(defrule\n\t(true)\n=>\n\t(up-set-target-object 2 c: 0))"
                "\n(defrule\n\t(true)\n=>\n"
                "\n\t (up-get-point 12 55))\n"
                "\n(defrule\n\t(true)\n=>\n\t(up-set-target-point 55))\n"
            )
        ans += (
            "\n(defrule\n\t(true)\n=>\n\t"
            f"(up-find-local c: {self.self_selected} c: {self.self_selected_max}))\n\n"
            "\n(defrule\n\t(true)\n=>\n"
        )
        ans += "".join(
            [
                f"\t(up-remove-objects 1 {f})\n"
                for i, f in enumerate(self.filters)
                if i < self.used_filters
            ]
        )
        ans += f"\t(up-create-group 0 0 c: {self.group_id}))\n"

        return ans

    @classmethod
    def generate(cls) -> Self:
        self_selected = random.choice(PLAYER_LIST)
        self_selected_max = random.randint(0, 40)
        selected = random.choice(PLAYER_LIST)
        selected_max = random.randint(0, 40)
        distance_check = random.choice([True, False])
        used_filters = random.randint(0, 5)
        filters = [Filter.generate() for _ in range(7)]
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

    def mutate(self, mutation_chance: float, in_place: bool = False) -> Self:
        search = self if in_place else copy.deepcopy(self)
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


@dataclass
class DUCTarget(Mutable):
    selected: str
    selected_max: int
    used_filters: int
    filters: list[Filter]
    group_id: int
    action: int
    position: int
    targeted_player: int
    target_position: bool
    formation: str
    stance: int
    timer_id: int
    timer_time: int
    goal: int = 1
    use_goal: bool = False

    def __str__(self) -> str:
        used_const = "enemyPlayerID" if self.targeted_player == 2 else "selfPlayerID"
        ans = (
            "\n(defrule\n\t(true)\n=>\n\t(enable-timer "
            f"{self.timer_id} {self.timer_time})\n\t(disable-self))\n"
        )
        ans += (
            "\n(defrule\n\t(true)\n=>"
            "\n\t(up-full-reset-search)\n\t(up-reset-filters)\n\t(set-strategic-number 251 "
            f"{used_const})\n\t(set-strategic-number 249 {used_const}))\n"
            "\n(defrule\n\t(true)\n=>"
            f"\n\t(up-get-group-size c: {self.group_id} 51)"
            f"\n\t(up-set-group 1 c: {self.group_id})\n"
        )
        if not self.target_position:
            ans += f"\t(up-find-remote c: {self.selected} c: {self.selected_max}))\n\n"
            if self.used_filters:
                ans += "\n(defrule\n\t(true)\n=>\n"
                ans += "".join(
                    [
                        f"\t(up-remove-objects 2 {f})\n"
                        for i, f in enumerate(self.filters)
                        if i < self.used_filters
                    ]
                )
        ans += ")"
        ans += f"\n(defrule\n\t(timer-triggered {self.timer_id})"
        if self.goal:
            ans += f"\n\t(goal {self.goal} 1)"
        ans += "\n\t(up-compare-goal 51 > 0)\n=>\n\t"
        ans += (
            f"(up-get-point {self.position} 52)\n\t(up-target-point 52"
            if self.target_position
            else "(up-target-objects 0"
        )
        ans += f" {self.action} {self.formation} {self.stance})"
        ans += (
            f"\n\t(enable-timer {self.timer_id} {self.timer_time}))\n\n"
            "(defrule\n\t(true)\n\t=>\n\t(up-full-reset-search)\n\t(up-reset-filters)\n\t"
            "(set-strategic-number 251 enemyPlayerID)\n\t(set-strategic-number 249 enemyPlayerID))"
        )
        return ans

    @classmethod
    def generate(cls) -> Self:
        selected = random.choice(PLAYER_LIST)
        selected_max = random.randint(0, 40)
        used_filters = random.randint(0, 5)
        filters = [Filter.generate() for _ in range(7)]
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

    def mutate(self, mutation_chance: float, in_place: bool = False) -> Self:
        target = self if in_place else copy.deepcopy(self)
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


@dataclass
class GoalAction(Mutable):
    goals: list[int]
    values: list[int]
    actions: list[Action]
    used_goals: int
    used_actions: int

    def __str__(self) -> str:
        ans = "\n(defrule"
        ans += "".join((f"\n\t(goal {g} {v})") for g, v in zip(self.goals, self.values))
        ans += f"\n=>\n\t{_write_actions(self.actions)})\n\n"
        return ans

    @classmethod
    def generate(cls) -> Self:
        size = 3
        goals = [random.randint(1, 40) for _ in range(size)]
        values = [random.randint(0, 1) for _ in range(size)]

        actions: list[Action] = []
        for _ in range(size):
            temp = Action.generate()
            while temp.action_name == "set-strategic-number":
                temp = Action.generate()
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

    def mutate(self, mutation_chance: float, in_place: bool = False) -> Self:
        goal_action = self if in_place else copy.deepcopy(self)
        new = GoalAction.generate()
        for i, _ in enumerate(goal_action.goals):
            if random.random() < mutation_chance:
                goal_action.goals[i] = new.goals[i]
        for i, _ in enumerate(goal_action.values):
            if random.random() < mutation_chance:
                goal_action.values[i] = new.values[i]
        for action in goal_action.actions:
            action = action.mutate(mutation_chance)
            if action.action_name == "set-strategic-number":
                action = action.mutate(mutation_chance)
            # ? Should this be a while loop until the action name is not that?
        if random.random() < mutation_chance:
            goal_action.used_goals = new.used_goals
        if random.random() < mutation_chance:
            goal_action.used_actions = new.used_actions

        return goal_action


@dataclass
class AI(Mutable):
    simples: list[Simple]
    rules: list[Rule]
    attack_rules: list[AttackRule]
    duc_search: list[DUCSearch]
    duc_target: list[DUCTarget]
    goal_rules: list[Goal]
    goal_actions: list[GoalAction]

    @classmethod
    def generate(cls) -> Self:
        simple_list: list[Simple] = []
        if settings.villager_preset:
            # build villagers
            temp = Simple.generate()
            temp.type = "train"
            temp.parameters["Trainable"] = "83"
            temp.threshold = 30
            temp.age_required = ["current-age == 0"]

            simple_list.append(temp)

            temp = Simple.generate()
            temp.type = "train"
            temp.parameters["Trainable"] = "83"
            temp.threshold = 80
            temp.age_required = ["current-age == 1"]

            simple_list.append(temp)

        simple_list.extend([Simple.generate() for _ in range(settings.simple_count)])

        ai = [Rule.generate() for _ in range(settings.ai_length)]
        attack_rules = [
            AttackRule.generate() for _ in range(settings.attack_rule_count)
        ]
        duc_search = [DUCSearch.generate() for _ in range(settings.DUC_count)]
        duc_target = [DUCTarget.generate() for _ in range(settings.DUC_count)]
        goal_rules = [Goal.generate() for _ in range(settings.goal_rule_count)]
        goal_actions = [
            GoalAction.generate() for _ in range(settings.goal_action_count)
        ]

        return AI(
            simple_list,
            ai,
            attack_rules,
            duc_search,
            duc_target,
            goal_rules,
            goal_actions,
        )

    def mutate(self, mutation_chance: float) -> Self:
        ai = copy.deepcopy(self)

        while ai == self:
            ai.simples = [simple.mutate(mutation_chance) for simple in ai.simples]

            new_rules: list[Rule] = []
            if settings.allow_complex:
                for simple in ai.simples:
                    if random.random() < mutation_chance / 2:
                        new_rules.append(simple.to_complex())
                        ai.simples.remove(simple)

            for _ in range(4):
                if random.random() < mutation_chance:
                    ai.simples.append(Simple.generate())

            if random.random() < mutation_chance / 2:
                ai.simples.remove(random.choice(ai.simples))

            ai.rules = [rule.mutate(mutation_chance) for rule in ai.rules]

            if random.random() < mutation_chance / 2:
                ai.rules.append(Rule.generate())

            if len(ai.rules) > 0:
                if random.random() < mutation_chance / 2:
                    ai.rules.remove(random.choice(ai.rules))

            ai.attack_rules = [
                attack_rule.mutate(mutation_chance) for attack_rule in ai.attack_rules
            ]

            for _ in range(2):
                if random.random() < mutation_chance:
                    ai.attack_rules.append(AttackRule.generate())

            if len(ai.attack_rules) > 0:
                if random.random() < mutation_chance:
                    ai.attack_rules.remove(random.choice(ai.attack_rules))

            if random.random() < mutation_chance / 3:
                random.shuffle(ai.simples)

            if random.random() < mutation_chance / 3:
                random.shuffle(ai.rules)

            if random.random() < mutation_chance / 3:
                random.shuffle(ai.attack_rules)

            if random.random() < mutation_chance / 3:
                random.shuffle(ai.duc_search)

            if random.random() < mutation_chance / 3:
                random.shuffle(ai.duc_target)

            if random.random() < mutation_chance / 3:
                random.shuffle(ai.goal_rules)

            if random.random() < mutation_chance / 3:
                random.shuffle(ai.goal_actions)

            ai.rules = new_rules + ai.rules

            ai.duc_search = [search.mutate(mutation_chance) for search in ai.duc_search]
            ai.duc_target = [target.mutate(mutation_chance) for target in ai.duc_target]

            num = len(ai.duc_search)
            randoms = [random.random() for _ in range(num)]
            ai.duc_search = [
                s for s, x in zip(ai.duc_search, randoms) if x >= mutation_chance / 3
            ]
            ai.duc_target = [
                t for t, x in zip(ai.duc_target, randoms) if x >= mutation_chance / 3
            ]
            for _ in range(num):
                if random.random() < mutation_chance / 2:
                    ai.duc_search.append(DUCSearch.generate())
                    ai.duc_target.append(DUCTarget.generate())

            ai.goal_rules = [goal.mutate(mutation_chance) for goal in ai.goal_rules]
            for rule in ai.goal_rules:
                if random.random() < mutation_chance / 3:
                    ai.goal_rules.remove(rule)
            for _ in range(2):
                if random.random() < mutation_chance / 2:
                    ai.goal_rules.append(Goal.generate())

            ai.goal_actions = [
                goal_action.mutate(mutation_chance) for goal_action in ai.goal_actions
            ]
            for goal_action in ai.goal_actions:
                if random.random() < mutation_chance / 3:
                    ai.goal_actions.remove(goal_action)
            for _ in range(4):
                if random.random() < mutation_chance:
                    ai.goal_actions.append(GoalAction.generate())

        return ai

    def export(self, ai_name: str) -> None:
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
        player, enemy = (2, 1) if "self" in ai_name else (1, 2)
        default_ai = (
            f"(defconst selfPlayerID {player})\n(defconst enemyPlayerID {enemy})\n\n"
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
            for rule in self.goal_rules:
                f.write(str(rule))
            for simple in self.simples:
                f.write(str(simple))
            for goal_action in self.goal_actions:
                f.write(str(goal_action))
            if settings.allow_attack_rules:
                for attack_rule in self.attack_rules:
                    f.write(str(attack_rule))
            if settings.allow_DUC:
                for search, target in zip(self.duc_search, self.duc_target):
                    f.write(str(search))
                    f.write(str(target))
            if settings.allow_complex:
                for rule in self.rules:
                    f.write(str(rule))

    def save_to_file(self, file_name: str) -> None:
        # ! make AI objects exportable in JSON format
        temp = {"lazy": json.dumps(self, default=vars)}
        saved = False
        while not saved:
            try:
                with open(
                    "AI/" + file_name + ".txt", "w+", encoding="utf-8"
                ) as outfile:
                    json.dump(temp, outfile)
            except KeyboardInterrupt:
                print("saving!")
                saved = False
            else:
                saved = True

    @classmethod
    def from_file(cls, file_name: str) -> Self:
        # ! make AI objects exportable in JSON format
        with open("AI/" + file_name + ".txt", encoding="utf-8") as json_file:
            data = json.load(json_file)
        return AI(**json.loads(data["lazy"]))
