import tkinter as tk
from io import TextIOWrapper
from typing import Any

from globals import ACTIONS, FACTS
from main import backup
from models import (
    AI,
    AttackRule,
    DUCSearch,
    DUCTarget,
    Filter,
    GameTimeCondition,
    Goal,
    GoalAction,
    PopulationCondition,
    Simple,
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

    simple_dict: dict[str, Simple] = {}

    for line in research[2:]:
        line = line.split(",")
        if not line[0]:
            continue
        temp = Simple.generate()
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
        temp = Simple.generate()
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
        temp = Simple.generate()
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
        temp = Simple.generate()
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
        temp = Simple.generate()
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
    ai = AI.from_file(string)
    simples = ai.simples
    attack_rules = ai.attack_rules
    duc_search = ai.duc_search
    duc_target = ai.duc_target
    goals = ai.goal_rules
    goal_actions = ai.goal_actions

    research: list[list[Any]] = []
    buildings: list[list[Any]] = []
    build_forward: list[list[Any]] = []
    units: list[list[Any]] = []
    strategic_numbers: list[list[Any]] = []

    # [type,params,threshold,age_required,requirement,requirement_count,gametime]
    for i, simple in enumerate(simples):
        local_simple = simple
        if local_simple.type == "research":
            # print(local_simple)
            research.append(
                [
                    local_simple.parameters["TechId"],
                    local_simple.age_required[0],
                    local_simple.requirement,
                    local_simple.requirement_count,
                    local_simple.game_time,
                    local_simple.use_goal,
                    local_simple.goal,
                    i,
                ]
            )

        if local_simple.type == "build":
            buildings.append(
                [
                    local_simple.parameters["Buildable"],
                    local_simple.age_required[0],
                    local_simple.threshold,
                    local_simple.requirement,
                    local_simple.requirement_count,
                    local_simple.game_time,
                    local_simple.use_goal,
                    local_simple.goal,
                    i,
                ]
            )

        if local_simple.type == "build-forward":
            build_forward.append(
                [
                    local_simple.parameters["Buildable"],
                    local_simple.age_required[0],
                    local_simple.threshold,
                    local_simple.requirement,
                    local_simple.requirement_count,
                    local_simple.game_time,
                    local_simple.use_goal,
                    local_simple.goal,
                    i,
                ]
            )

        if local_simple.type == "train":
            units.append(
                [
                    local_simple.parameters["Trainable"],
                    local_simple.age_required[0],
                    local_simple.threshold,
                    local_simple.requirement,
                    local_simple.requirement_count,
                    local_simple.game_time,
                    local_simple.use_goal,
                    local_simple.goal,
                    i,
                ]
            )

        if local_simple.type == "strategic_number":
            strategic_numbers.append(
                [
                    local_simple.parameters["SnId"],
                    local_simple.age_required[0],
                    local_simple.strategic_numbers[
                        str(local_simple.parameters["SnId"])
                    ],
                    local_simple.requirement,
                    local_simple.requirement_count,
                    local_simple.game_time,
                    local_simple.use_goal,
                    local_simple.goal,
                    i,
                ]
            )

    with open("edittable.csv", "w+", encoding="utf-8") as f:
        f.write("|Research\n")
        f.write(
            "TechID,age required,required,requirement count,"
            "gametime,goal_checked,goal_id,order\n"
        )
        write_list(research, f)
        f.write("\n|Building\n")
        f.write(
            "BuildingID,age required,max count,required,requirement count,"
            "gametime,goal_checked,goal_id,order\n"
        )
        write_list(buildings, f)
        f.write("\n|Build forward\n")
        f.write(
            "BuildingID,age required,max count,required,requirement count,"
            "gametime,goal_checked,goal_id,order\n"
        )
        write_list(build_forward, f)
        f.write("\n|Unit\n")
        f.write(
            "UnitID,age required,max count,required,requirement count,"
            "gametime,goal_checked,goal_id,order\n"
        )
        write_list(units, f)
        f.write("\n|Strategic Number\n")
        f.write(
            "SnID,age required,value,required,requirement count,"
            "gametime,goal_checked,goal_id,order\n"
        )
        write_list(strategic_numbers, f)
        f.write("\n|Attack Rules\n")
        f.write(
            "Type,Age required,Enemy Age Required,"
            "population1 type,population1 inq,population1 value,"
            "population2 type,population2 inq,population2 value,"
            "gametime inq,gametime value,attack %,retreat units,retreat location,"
            "goal_id,goal_checked\n"
        )
        f.write("\n".join(attack_rule.export() for attack_rule in attack_rules))
        f.write("\n")

        f.write("\n|Goals\n")
        f.write(
            "Goal ID,value,disable after use,checked goal,checked goal value,number of facts used,"
            "fact1,params1,fact2,params2,fact3,params3,fact4,params4\n"
        )
        f.write(",\n".join(goal.export() for goal in goals))
        f.write("\n")

        f.write("\n|DUC\n")
        f.write("lol I will add a descriptor later leave this line\n")
        for search, target in zip(duc_search, duc_target):
            f.write(f"{search.export()},{target.export()}\n")

        f.write("\n|Goal actions\n")
        f.write(
            "goal_count,action_count,goal1,goal_value1,goal2,goal_value2,goal3,goal_value3,"
            "action1,action1_parameters,action2,action2_parameters,action3,action3_parameters\n"
        )
        f.write("\n".join(goal_action.export() for goal_action in goal_actions))
        f.write("\n")


def write_list(lst: list[Any], f: TextIOWrapper) -> None:
    for line in lst:
        f.write(",".join(str(x) for x in line))
        f.write(",\n")


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
