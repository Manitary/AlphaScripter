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


def _write_actions(actions: list[Action]) -> str:
    return "....\n" + "\n".join(f"({action})" for action in actions)

@dataclass
class Rule:
    fact_length: int
    action_length: int
    age_required: list[str]
    local_facts: list[Fact]
    local_actions: list[Action]

    def __str__(self) -> str:
        ans = f"\n(defrule{self.write_facts()}\n=>{_write_actions(self.local_actions)})\n"
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


@dataclass
class AttackRule:
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


@dataclass
class Filter:
    object: int
    compare: str
    value: int

    def __str__(self) -> str:
        return f"{self.object} {self.compare} {self.value}"


@dataclass
class DUCSearch:
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


@dataclass
class DUCTarget:
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


@dataclass
class GoalAction:
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
