import tkinter as tk

from main import backup
from src.globals import ACTIONS, FACTS
from src.models import (
    AI,
    AttackRule,
    DUCSearch,
    DUCTarget,
    Filter,
    GameTimeCondition,
    Goal,
    GoalAction,
    PopulationCondition,
    SimpleRule,
)


def write_from_csv(file: str) -> None:
    # parses csv
    with open(file + ".csv", encoding="utf-8") as f:
        data = f.read()

    # [type,params,threshold,age_required,requirement,requirement_count,gametime]

    # print(data[7])
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
    ) = [x.split("\n") for x in data.split("|")]

    simple_dict: dict[str, SimpleRule] = {}

    for line in research[2:]:
        line = line.split(",")
        if not line[0]:
            continue
        temp = SimpleRule.generate()
        temp.type = "research"
        temp.parameters["TechId"] = line[0]
        temp.age_required = [line[1]]
        temp.requirement = line[2]
        temp.requirement_count = int(line[3])
        temp.game_time = int(line[4])
        temp.goal = int(line[6])
        temp.use_goal = line[5] == "TRUE"

        simple_dict[line[7]] = temp

    for line in buildings[2:]:
        line = line.split(",")
        if not line[0]:
            continue
        temp = SimpleRule.generate()
        temp.type = "build"
        temp.parameters["Buildable"] = line[0]
        temp.threshold = int(line[2])
        temp.age_required = [line[1]]
        temp.requirement = line[3]
        temp.requirement_count = int(line[4])
        temp.game_time = int(line[5])
        temp.goal = int(line[7])
        temp.use_goal = line[6] == "TRUE"
        print(temp.use_goal)

        simple_dict[line[8]] = temp

    for line in build_forward[2:]:
        line = line.split(",")
        if not line[0]:
            continue
        temp = SimpleRule.generate()
        temp.type = "build-forward"
        temp.parameters["Buildable"] = line[0]
        temp.threshold = int(line[2])
        temp.age_required = [line[1]]
        temp.requirement = line[3]
        temp.requirement_count = int(line[4])
        temp.game_time = int(line[5])
        temp.goal = int(line[7])
        temp.use_goal = line[6] == "TRUE"

        simple_dict[line[8]] = temp

    for line in units[2:]:
        line = line.split(",")
        if not line[0]:
            continue
        temp = SimpleRule.generate()
        temp.type = "train"
        temp.parameters["Trainable"] = line[0]
        temp.threshold = int(line[2])
        temp.age_required = [line[1]]
        temp.requirement = line[3]
        temp.requirement_count = int(line[4])
        temp.game_time = int(line[5])
        temp.goal = int(line[7])
        temp.use_goal = line[6] == "TRUE"

        simple_dict[line[8]] = temp

    for line in strategic_numbers[2:]:
        line = line.split(",")
        if not line[0]:
            continue
        temp = SimpleRule.generate()
        temp.type = "strategic_number"
        temp.parameters["SnId"] = line[0]
        temp.strategic_numbers[line[0]] = line[2]
        temp.age_required = [line[1]]
        temp.requirement = line[3]
        temp.requirement_count = int(line[4])
        temp.game_time = int(line[5])
        temp.goal = int(line[7])
        temp.use_goal = line[6] == "TRUE"

        simple_dict[line[8]] = temp

    ai = AI()
    ai.simples = list(simple_dict.values())

    for line in attack_rules[2:]:
        line = line.split(",")
        if not line[0]:
            continue
        AI.attack_rules.append(
            AttackRule(
                type=line[0],
                age_required=line[1],
                enemy_age_required=line[2],
                population1=PopulationCondition(
                    type=line[3], comparison=line[4], amount=int(line[5])
                ),
                population2=PopulationCondition(
                    type=line[6], comparison=line[7], amount=int(line[8])
                ),
                game_time=GameTimeCondition(line[9], int(line[10])),
                retreat_unit=line[11],
                attack_percent=int(line[12]),
                retreat_to=line[13],
                goal=int(line[15]),
                use_goal=line[14] == "TRUE",
            )
        )

    for line in goals[2:]:
        line = line.split(",")
        if not line[0]:
            continue
        temp = Goal.generate()
        temp.goal_id = int(line[0])
        temp.value = int(line[1])
        temp.disable = line[2] == "TRUE"
        temp.goal_num = int(line[3])
        temp.use_goal = line[4] == "TRUE"
        temp.fact_count = int(line[5])

        for x, fact in enumerate(temp.used_facts):
            fact.fact_name = line[6 + x * 2]
            local_params = line[7 + x * 2].split(";")
            if fact.fact_name in {"TRUE", "FALSE"}:
                fact.fact_name = fact.fact_name.lower()
            for y, param in enumerate(local_params):
                # print(str(keys[y]) + ", " + str(local_params[y-1]))
                # print(temp[5][x][1][keys[y]])
                fact.parameters[FACTS[fact.fact_name][y + 1]] = param
                # print(keys[y])
                # print(temp[5][x][1][keys[y]])

        ai.goal_rules.append(temp)

    for line in duc[2::2]:
        # print(DUC[i])
        line = line.split(",")
        if not line[0]:
            continue
        temp = DUCSearch(
            self_selected=line[0],
            self_selected_max=int(line[1]),
            used_filters=int(line[2]),
            filters=[],
            group_id=int(line[3]),
            selected=line[4],
            selected_max=int(line[5]),
            distance_check=line[6] == "TRUE",
        )
        for x in range(7):  # ! Dependent on the number of default filters
            local = line[7 + x].split(";")
            temp.filters[x] = Filter(
                object=int(local[0]), compare=local[1], value=int(local[2])
            )

        ai.duc_search.append(temp)

    for line in duc[3::2]:
        line = line.split(",")
        if not line[0]:
            continue

        temp = DUCTarget(
            selected=line[0],
            selected_max=int(line[1]),
            used_filters=int(line[3]),
            filters=[],
            group_id=int(line[2]),
            action=int(line[11]),
            position=int(line[12]),
            targeted_player=int(line[13]),
            target_position=line[14] == "TRUE",
            formation=line[15],  # ? originally, int(), but formations are strings?
            stance=int(line[16]),
            timer_id=int(line[17]),
            timer_time=int(line[18]),
            goal=int(line[19]),
            use_goal=line[20] == "TRUE",
        )
        for x in range(7):  # ! Dependent on the number of default filters
            local = line[4 + x].split(";")
            temp.filters[x] = Filter(
                object=int(local[0]), compare=local[1], value=int(local[2])
            )

        ai.duc_target.append(temp)

    for line in goal_actions[2::]:
        line = line.split(",")
        if not line[0]:
            continue
        temp = GoalAction.generate()

        # count
        temp.used_goals = int(line[0])
        temp.used_actions = int(line[1])
        temp.goals = [int(line[2 + 2 * x]) for x in range(3)]
        temp.values = [int(line[3 + 2 * x]) for x in range(3)]

        for x, action in enumerate(temp.actions):
            action_name = line[8 + 2 * x]
            local_params = line[9 + 2 * x].split(";")
            for y, param in enumerate(local_params):
                # print(str(keys[y]) + ", " + str(local_params[y-1]))
                # print(temp[5][x][1][keys[y]])
                action.action_name = action_name
                action.parameters[ACTIONS[action_name][y + 1]] = param

        ai.goal_actions.append(temp)

    backup()
    ai.export("best")
    ai.save_to_file("best")


def read(string: str) -> None:
    with open("edittable.csv", "w+", encoding="utf-8") as f:
        f.write(AI.from_file(string).to_csv())


def swap(name1: str, name2: str) -> None:
    ai1 = AI.from_file(name1)
    ai2 = AI.from_file(name2)
    ai1.rules = ai2.rules
    ai1.export("best")
    ai1.save_to_file("best")


# a = generate_ai()
# save_ai(a,"test")
# read("test")
# write_from_csv("edittable")


def create_app() -> tk.Tk:
    root = tk.Tk()

    input_txt = tk.Text(root, height=1, width=15)
    input_txt.pack()

    button1 = tk.Button(
        root, text="edit", command=lambda: read(input_txt.get(1.0, "end-1c"))
    )
    button1.pack()

    input_txt2 = tk.Text(root, height=1, width=15)
    input_txt2.pack()

    button2 = tk.Button(
        root,
        text="commit ai",
        command=lambda: write_from_csv(input_txt2.get(1.0, "end-1c")),
    )
    button2.pack()

    input_txt3 = tk.Text(root, height=1, width=15)
    input_txt3.pack()
    input_txt4 = tk.Text(root, height=1, width=15)
    input_txt4.pack()

    button2 = tk.Button(
        root,
        text="swap complex",
        command=lambda: swap(
            input_txt3.get(1.0, "end-1c"), input_txt4.get(1.0, "end-1c")
        ),
    )
    button2.pack()
    return root


def main() -> None:
    app = create_app()
    app.mainloop()


if __name__ == "__main__":
    main()
