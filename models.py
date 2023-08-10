from dataclasses import dataclass

from globals import ACTIONS, FACTS


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
    gametime: int
    strategic_numbers: dict[str, str | int]
    goal: int
    use_goal: bool
