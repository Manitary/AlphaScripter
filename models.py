from dataclasses import dataclass

from globals import ACTIONS, BUILDABLE, FACTS


@dataclass
class GoalFact:
    fact_name: str
    parameters: dict[str, str | int]

    def __str__(self) -> str:
        return (
            f"{self.fact_name} "
            f"{' '.join(tuple(str(self.parameters[x]) for x in FACTS[self.fact_name]))}"
        )


@dataclass
class Goal:
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


@dataclass
class Fact:
    fact_name: str
    is_not: int
    parameters: dict[str, str | int]
    and_or: str

    def __str__(self) -> str:
        return (
            f"{self.fact_name} "
            f"{' '.join(tuple(str(self.parameters[x]) for x in FACTS[self.fact_name]))}"
        )


@dataclass
class Action:
    action_name: str
    parameters: dict[str, str | int]
    strategic_numbers: dict[str, str | int]

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


@dataclass
class Rule:
    fact_length: int
    action_length: int
    age_required: list[str]
    local_facts: list[Fact]
    local_actions: list[Action]

    def __str__(self) -> str:
        ans = f"\n(defrule{self.write_facts()}\n=>{self.write_actions()})\n"
        if len(ans.split()) > 20:
            ans = ""
        return ans

    def write_facts(self) -> str:
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

    def write_actions(self) -> str:
        return "....\n" + "\n".join(f"({action})" for action in self.local_actions)


@dataclass
class Simple:
    type: str
    parameters: dict[str, str | int]
    threshold: int
    age_required: list[str]
    requirement: str
    requirement_count: int
    game_time: int
    strategic_numbers: dict[str, str | int]
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
