import copy
import random
from dataclasses import dataclass, field
from typing import Self, TypeVar

import yaml
from yamlable import yaml_info

from src.globals import RESIGN_RULE
from src.config import CONFIG
from src.models import (
    AttackRule,
    ComplexRule,
    DUCSearch,
    DUCTarget,
    Goal,
    GoalAction,
    Mutable,
    SimpleRule,
)


@yaml_info(yaml_tag="AI")
@dataclass
class AI(Mutable):
    simples: list[SimpleRule] = field(default_factory=list)
    rules: list[ComplexRule] = field(default_factory=list)
    attack_rules: list[AttackRule] = field(default_factory=list)
    duc_search: list[DUCSearch] = field(default_factory=list)
    duc_target: list[DUCTarget] = field(default_factory=list)
    goal_rules: list[Goal] = field(default_factory=list)
    goal_actions: list[GoalAction] = field(default_factory=list)

    @classmethod
    def generate(cls) -> Self:
        simple_list: list[SimpleRule] = []
        if CONFIG.villager_preset:
            # build villagers
            temp = SimpleRule.generate()
            temp.type = "train"
            temp.parameters["Trainable"] = "83"
            temp.threshold = 30
            temp.age_required = ["current-age == 0"]

            simple_list.append(temp)

            temp = SimpleRule.generate()
            temp.type = "train"
            temp.parameters["Trainable"] = "83"
            temp.threshold = 80
            temp.age_required = ["current-age == 1"]

            simple_list.append(temp)

        simple_list.extend([SimpleRule.generate() for _ in range(CONFIG.simple_count)])

        ai = [ComplexRule.generate() for _ in range(CONFIG.ai_length)]
        attack_rules = [AttackRule.generate() for _ in range(CONFIG.attack_rule_count)]
        duc_search = [DUCSearch.generate() for _ in range(CONFIG.duc_count)]
        duc_target = [DUCTarget.generate() for _ in range(CONFIG.duc_count)]
        goal_rules = [Goal.generate() for _ in range(CONFIG.goal_rule_count)]
        goal_actions = [GoalAction.generate() for _ in range(CONFIG.goal_action_count)]

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

            new_rules: list[ComplexRule] = []
            if CONFIG.allow_complex:
                for simple in ai.simples:
                    if random.random() < mutation_chance / 2:
                        new_rules.append(simple.to_complex())
                        ai.simples.remove(simple)

            for _ in range(4):
                if random.random() < mutation_chance:
                    ai.simples.append(SimpleRule.generate())

            if random.random() < mutation_chance / 2:
                ai.simples.remove(random.choice(ai.simples))

            ai.rules = [rule.mutate(mutation_chance) for rule in ai.rules]

            if random.random() < mutation_chance / 2:
                ai.rules.append(ComplexRule.generate())

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
        if CONFIG.force_house:
            default_ai += (
                "(defrule\n"
                "(building-type-count-total town-center > 0)\n"
                "(housing-headroom < 5)\n"
                "(population-headroom > 0)\n"
                "(can-build house)\n"
                "=>\n(build house))\n\n"
            )

        if CONFIG.force_age_up:
            default_ai += (
                "(defrule\n(true)\n=>\n(research 101))\n"
                "(defrule\n(true)\n=>\n(research 102))\n\n"
            )

        if CONFIG.force_imperial_age:
            default_ai += "(defrule\n(true)\n=>\n(research 103))\n"

        if CONFIG.force_barracks:
            default_ai += (
                "(defrule\n"
                "(can-build barracks)\n"
                "(building-type-count barracks < 1)\n"
                "=>\n(build barracks)\n)\n\n"
            )

        if CONFIG.force_resign:
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

        if CONFIG.force_scout:
            default_ai += (
                "\n(defrule\n(true)\n"
                "=>\n\t(set-strategic-number sn-total-number-explorers 1)"
                "\n\t(set-strategic-number sn-number-explore-groups 1)"
                "\n\t(up-send-scout 101 1)"
                "\n\t(disable-self)\n)\n\n"
            )

        with open(CONFIG.local_drive + ai_name + ".per", "w", encoding="utf-8") as f:
            f.write(default_ai)
            for rule in self.goal_rules:
                f.write(rule.write())
            for simple in self.simples:
                f.write(simple.write())
            for goal_action in self.goal_actions:
                f.write(goal_action.write())
            if CONFIG.allow_attack_rules:
                for attack_rule in self.attack_rules:
                    f.write(attack_rule.write())
            if CONFIG.allow_duc:
                for search, target in zip(self.duc_search, self.duc_target):
                    f.write(search.write())
                    f.write(target.write())
            if CONFIG.allow_complex:
                for rule in self.rules:
                    f.write(rule.write())

    def save_to_file(self, file_name: str) -> None:
        """Save as YAML file"""
        saved = False
        while not saved:
            try:
                with open(f"AI/{file_name}.yaml", "w", encoding="utf-8") as f:
                    f.write(yaml.dump(self))
            except KeyboardInterrupt:
                print("saving!")
                saved = False
            else:
                saved = True

    @classmethod
    def from_file(cls, file_name: str) -> Self:
        """Import from YAML file"""
        return cls.load_yaml(f"AI/{file_name}.yaml")

    def to_csv(self) -> str:
        ans = ""
        ans += (
            "|Research\n"
            "TechID,age required,required,requirement count,"
            "gametime,goal_checked,goal_id,order\n"
        )
        ans += ",\n".join(
            (
                f"{simple.to_csv()},{i},\n"
                for i, simple in enumerate(self.simples)
                if simple.type == "research"
            )
        )
        ans += ",\n"
        ans += (
            "\n|Building\n"
            "BuildingID,age required,max count,required,requirement count,"
            "gametime,goal_checked,goal_id,order\n"
        )
        ans += ",\n".join(
            (
                f"{simple.to_csv()},{i},\n"
                for i, simple in enumerate(self.simples)
                if simple.type == "build"
            )
        )
        ans += ",\n"
        ans += (
            "\n|Build forward\n"
            "BuildingID,age required,max count,required,requirement count,"
            "gametime,goal_checked,goal_id,order\n"
        )
        ans += ",\n".join(
            (
                f"{simple.to_csv()},{i},\n"
                for i, simple in enumerate(self.simples)
                if simple.type == "build-forward"
            )
        )
        ans += ",\n"
        ans += (
            "\n|Unit\n"
            "UnitID,age required,max count,required,requirement count,"
            "gametime,goal_checked,goal_id,order\n"
        )
        ans += ",\n".join(
            (
                f"{simple.to_csv()},{i},\n"
                for i, simple in enumerate(self.simples)
                if simple.type == "train"
            )
        )
        ans += (
            "\n|Strategic Number\n"
            "SnID,age required,value,required,requirement count,"
            "gametime,goal_checked,goal_id,order\n"
        )
        ans += "".join(
            (
                f"{simple.to_csv()},{i},\n"
                for i, simple in enumerate(self.simples)
                if simple.type == "strategic_number"
            )
        )
        ans += (
            "\n|Attack Rules\n"
            "Type,Age required,Enemy Age Required,"
            "population1 type,population1 inq,population1 value,"
            "population2 type,population2 inq,population2 value,"
            "gametime inq,gametime value,attack %,retreat units,retreat location,"
            "goal_id,goal_checked\n"
        )
        ans += "\n".join(attack_rule.to_csv() for attack_rule in self.attack_rules)
        ans += "\n"
        ans += (
            "\n|Goals\n"
            "Goal ID,value,disable after use,checked goal,checked goal value,number of facts used,"
            "fact1,params1,fact2,params2,fact3,params3,fact4,params4\n"
        )
        ans += ",\n".join(goal.to_csv() for goal in self.goal_rules)
        ans += "\n"
        ans += "\n|DUC\n"
        ans += "lol I will add a descriptor later leave this line\n"  # TODO
        for search, target in zip(self.duc_search, self.duc_target):
            ans += f"{search.export()},{target.export()}\n"
        ans += (
            "\n|Goal actions\n"
            "goal_count,action_count,goal1,goal_value1,goal2,goal_value2,goal3,goal_value3,"
            "action1,action1_parameters,action2,action2_parameters,action3,action3_parameters\n"
        )
        ans += "\n".join(goal_action.export() for goal_action in self.goal_actions)
        ans += "\n"

        return ans

    @classmethod
    def from_csv(cls, csv: str) -> Self:
        (
            _,
            research,
            buildings,
            build_forward,
            units,
            strategic_numbers,
            attack_rules,
            goals,
            duc,
            goal_actions,
        ) = [x.split("\n") for x in csv.split("|")]
        ai = AI()
        # TODO Reduce duplication
        for line in research[2:]:
            line = line.split(",")
            if line[0]:
                ai.simples[int(line[7])] = SimpleRule.from_csv("research", line)
        for line in buildings[2:]:
            line = line.split(",")
            if line[0]:
                ai.simples[int(line[8])] = SimpleRule.from_csv("build", line)
        for line in build_forward[2:]:
            line = line.split(",")
            if line[0]:
                ai.simples[int(line[8])] = SimpleRule.from_csv("build-forward", line)
        for line in units[2:]:
            line = line.split(",")
            if line[0]:
                ai.simples[int(line[8])] = SimpleRule.from_csv("train", line)
        for line in strategic_numbers[2:]:
            line = line.split(",")
            if line[0]:
                ai.simples[int(line[8])] = SimpleRule.from_csv(
                    "strategic_numbers", line
                )
        for line in attack_rules[2:]:
            line = line.split(",")
            if line[0]:
                ai.attack_rules.append(AttackRule.from_csv(line))
        for line in goals[2:]:
            line = line.split(",")
            if line[0]:
                ai.goal_rules.append(Goal.from_csv(line))
        for line in duc[2::2]:
            line = line.split(",")
            if line[0]:
                ai.duc_search.append(DUCSearch.from_csv(line))
        for line in duc[3::2]:
            line = line.split(",")
            if line[0]:
                ai.duc_target.append(DUCTarget.from_csv(line))
        for line in goal_actions[2:]:
            line = line.split(",")
            if line[0]:
                ai.goal_actions.append(GoalAction.from_csv(line))
        return ai


T = TypeVar("T")


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
