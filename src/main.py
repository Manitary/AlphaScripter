import copy
import itertools
import random
import time
from itertools import zip_longest
from typing import Sequence

from elosports.elo import Elo

import settings

from src.functions import crossover
from src.game_launcher import Game, GameSettings, GameStatus, Launcher
from src.models import AI

AI_NAMES = ["parent", "b", "c", "d", "e", "f", "g", "h"]

EXECUTABLE_PATH = "C:\\Program Files\\Microsoft Games\\Age of Empires II\\age2_x1.5.exe"


def setup_ai_files() -> None:
    for ai in AI_NAMES:
        with open(f"{ai}.ai", "w+", encoding="utf-8") as f:
            f.write("")


# changed so only real wins count
def extract_round_robin(score: Sequence[int], game_time: int) -> tuple[int, int]:
    p1 = 0
    p2 = 0
    if score[0] > score[1]:
        p1 += 1
    elif score[1] > score[0]:
        p2 += 1
    if game_time > 0.9 * settings.game_time:
        # print("real win!")
        p1 *= 0
        p2 *= 0
    return p1, p2


def create_seeds(threshold: int) -> AI:
    while True:
        game_settings = GameSettings(
            civilisations=[settings.civ] * 4,
            names=["parent", "parent"],
            game_time_limit=settings.game_time,
            map_id="arabia",
        )

        master_score_list = [[0, 0, 0, 0, 0, 0, 0, 0]]
        # print("reset")
        ai_parent = AI.generate()
        ai_parent.export("parent")

        launcher = Launcher(
            executable_path="C:\\Program Files\\Microsoft Games\\Age of Empires II\\age2_x1.5.exe",
            settings=game_settings,
        )
        master_score_list = [
            game.stats.scores if game.stats else []
            for game in launcher.launch_games(instances=1)
            if game.status != GameStatus.EXCEPTED
        ]

        score_list = [0] * len(AI_NAMES)
        if not master_score_list:
            continue
        for scores in master_score_list:
            score_list = [sum(x) for x in zip_longest(score_list, scores, fillvalue=0)]
            print(max(score_list))
            if max(score_list) > threshold:
                ai_parent.save_to_file("seed")
                return ai_parent


def extract_ffa(master_score: list[list[int]]) -> tuple[int, int, int, int]:
    a, b, c, d = 0, 0, 0, 0

    for scores in master_score:
        local_score = scores
        sorted_list = sorted(scores, reverse=True)

        if local_score[0] == sorted_list[0]:
            a += 2
        elif local_score[1] == sorted_list[0]:
            b += 2
        elif local_score[2] == sorted_list[0]:
            c += 2
        elif local_score[3] == sorted_list[0]:
            d += 2

        if local_score[0] == sorted_list[1]:
            a += 1
        elif local_score[1] == sorted_list[1]:
            b += 1
        elif local_score[2] == sorted_list[1]:
            c += 1
        elif local_score[3] == sorted_list[1]:
            d += 1

    # print((a,b,c,d))
    return a, b, c, d


def run_ffa(
    threshold: int,
    load: bool,
    default_mutation_chance: float = settings.default_mutation_chance,
) -> None:
    game_time = 5000
    score_list = [[0] * len(AI_NAMES)]

    if load:
        ai_parent = AI.from_file("best")
    else:
        ai_parent = create_seeds(threshold)

    game_settings = GameSettings(
        civilisations=[settings.civ] * 8,
        names=AI_NAMES,
        game_time_limit=game_time,
        map_id="arabia",
    )

    second_place = copy.deepcopy(ai_parent)
    generation = 1
    fails = 0
    mutation_chance = default_mutation_chance

    while True:
        generation += 1
        crossed = crossover(ai_parent, second_place, mutation_chance)
        b = crossed.mutate(mutation_chance)

        crossed = crossover(ai_parent, second_place, mutation_chance)
        c = crossed.mutate(mutation_chance)

        crossed = crossover(ai_parent, second_place, mutation_chance)
        d = crossed.mutate(mutation_chance)

        crossed = crossover(ai_parent, second_place, mutation_chance)
        e = crossed.mutate(mutation_chance)

        crossed = crossover(ai_parent, second_place, mutation_chance)
        f = crossed.mutate(mutation_chance)

        crossed = crossover(ai_parent, second_place, mutation_chance)
        g = crossed.mutate(mutation_chance)

        crossed = crossover(ai_parent, second_place, mutation_chance)
        h = crossed.mutate(mutation_chance)

        ai_parent.export("parent")
        b.export("b")
        c.export("c")
        d.export("d")
        e.export("e")
        f.export("f")
        g.export("g")
        h.export("h")

        # reads score
        launcher = Launcher(
            executable_path="C:\\Program Files\\Microsoft Games\\Age of Empires II\\age2_x1.5.exe",
            settings=game_settings,
        )
        master_score_list = [[0] * len(AI_NAMES)]
        master_score_list.extend(
            [
                game.stats.scores if game.stats else []
                for game in launcher.launch_games(instances=5)
                if game.status != GameStatus.EXCEPTED
            ]
        )
        score_list = [0] * len(AI_NAMES)

        for scores in master_score_list:
            score_list = [sum(x) for x in zip_longest(score_list, scores, fillvalue=0)]

        if not score_list or set(score_list) == {0} or len(master_score_list) < 3:
            if generation == 1:
                generation -= 1
            continue
        while [0] * len(AI_NAMES) in master_score_list:
            master_score_list.remove([0] * len(AI_NAMES))

        (
            parent_score,
            b_score,
            c_score,
            d_score,
            e_score,
            f_score,
            g_score,
            h_score,
        ) = score_list
        score_list = sorted(score_list, reverse=True)

        # checks number of rounds with no improvement and sets annealing
        if parent_score == max(score_list):
            fails += 1
            if fails % 2 == 0:
                mutation_chance = min(
                    default_mutation_chance + fails / (1000 * settings.anneal_amount),
                    0.2,
                )
            else:
                mutation_chance = max(
                    default_mutation_chance - fails / (1000 * settings.anneal_amount),
                    0.001,
                )
        else:
            fails = 0
            mutation_chance = default_mutation_chance

        failed = False
        if parent_score == max(score_list):
            failed = True
            winner = copy.deepcopy(ai_parent)
            second_place = copy.deepcopy(ai_parent)
            print(f"parent won by score: {parent_score}")
        elif b_score == max(score_list):
            winner = copy.deepcopy(b)
            print(f"b won by score: {b_score}")
        elif c_score == max(score_list):
            winner = copy.deepcopy(c)
            print(f"c won by score: {b_score}")
        elif d_score == max(score_list):
            winner = copy.deepcopy(d)
            print(f"d won by score: {b_score}")
        elif e_score == max(score_list):
            winner = copy.deepcopy(e)
            print(f"e won by score: {b_score}")
        elif f_score == max(score_list):
            winner = copy.deepcopy(f)
            print(f"f won by score: {b_score}")
        elif g_score == max(score_list):
            winner = copy.deepcopy(g)
            print(f"g won by score: {b_score}")
        elif h_score == max(score_list):
            winner = copy.deepcopy(h)
            print(f"h won by score: {b_score}")
        else:
            print("Failed!!!")
            break

        # checks if second best for crossover, also gross and needs to be replaced later
        if not failed:
            if parent_score == score_list[1]:
                second_place = copy.deepcopy(ai_parent)
            elif b_score == score_list[1]:
                second_place = copy.deepcopy(b)
            elif c_score == score_list[1]:
                second_place = copy.deepcopy(c)
            elif d_score == score_list[1]:
                second_place = copy.deepcopy(d)
            elif e_score == score_list[1]:
                second_place = copy.deepcopy(e)
            elif f_score == score_list[1]:
                second_place = copy.deepcopy(f)
            elif g_score == score_list[1]:
                second_place = copy.deepcopy(g)
            else:  # h_score == score_list[1]:
                second_place = copy.deepcopy(h)

        ai_parent = copy.deepcopy(winner)
        winner.export("best")
        winner.save_to_file("best")

        # restarts after 10 fails
        if fails > settings.fails_before_reset:
            print("fail threshold exceeded, resetting...")
            winner.export(str(max(score_list)))
            winner.save_to_file(str(max(score_list)))
            fails = 0
            generation = 0
            ai_parent = AI.generate()


def run_ffa_four(
    threshold: int,
    load: bool,
    default_mutation_chance: float = settings.default_mutation_chance,
) -> None:
    game_time = 5000
    score_list = [[0] * len(AI_NAMES)]

    if load:
        ai_parent = AI.from_file("best")
    else:
        ai_parent = create_seeds(threshold)

    # temporary code
    # ai_parent = mutate_ai(copy.deepcopy(ai_parent))

    ai_names = ["parent", "b", "c", "d"]

    game_settings = GameSettings(
        civilisations=["huns"] * 4,
        names=ai_names,
        game_time_limit=game_time,
        map_id="arabia",
        map_size="tiny",
    )

    second_place = copy.deepcopy(ai_parent)
    mutation_chance = default_mutation_chance
    generation = 1
    fails = 0

    while True:
        generation += 1
        crossed = crossover(ai_parent, second_place, mutation_chance)
        b = crossed.mutate(mutation_chance)
        crossed = crossover(ai_parent, second_place, mutation_chance)
        c = crossed.mutate(mutation_chance)
        crossed = crossover(ai_parent, second_place, mutation_chance)
        d = crossed.mutate(mutation_chance)

        ai_parent.export("parent")
        b.export("b")
        c.export("c")
        d.export("d")

        # reads score
        launcher = Launcher(
            executable_path="C:\\Program Files\\Microsoft Games\\Age of Empires II\\age2_x1.5.exe",
            settings=game_settings,
        )
        master_score_list = [[0] * len(AI_NAMES)]
        master_score_list.extend(
            [
                game.stats.scores if game.stats else []
                for game in launcher.launch_games(instances=5)
                if game.status != GameStatus.EXCEPTED
            ]
        )
        score_list = [0] * len(AI_NAMES)

        for scores in master_score_list:
            score_list = [sum(x) for x in zip_longest(score_list, scores, fillvalue=0)]

        if not score_list or set(score_list) == {0} or len(master_score_list) < 3:
            if generation == 1:
                generation -= 1
            continue

        # parent_score, b_score, c_score, d_score = extract_ffa(master_score_list)

        # score_list = [parent_score, b_score, c_score, d_score]

        parent_score, b_score, c_score, d_score = score_list
        score_list = sorted(score_list, reverse=True)

        # checks number of rounds with no improvement and sets annealing
        if parent_score == max(score_list):
            fails += 1
            if fails % 2 == 0:
                mutation_chance = min(
                    default_mutation_chance + fails / (1000 * settings.anneal_amount),
                    0.2,
                )
            else:
                mutation_chance = max(
                    default_mutation_chance - fails / (1000 * settings.anneal_amount),
                    0.001,
                )
        else:
            fails = 0
            mutation_chance = default_mutation_chance

        failed = False

        if parent_score == max(score_list):
            failed = True
            winner = copy.deepcopy(ai_parent)
            second_place = copy.deepcopy(ai_parent)
            print(f"parent won by score: {parent_score}")
        elif b_score == max(score_list):
            winner = copy.deepcopy(b)
            print(f"b won by score: {b_score}")
        elif c_score == max(score_list):
            winner = copy.deepcopy(c)
            print(f"c won by score: {b_score}")
        elif d_score == max(score_list):
            winner = copy.deepcopy(d)
            print(f"d won by score: {b_score}")
        else:
            print("Failed!!!")
            break

        # checks if second best for crossover, also gross and needs to be replaced later
        if not failed:
            if parent_score == score_list[1]:
                second_place = copy.deepcopy(ai_parent)
            elif b_score == score_list[1]:
                second_place = copy.deepcopy(b)
            elif c_score == score_list[1]:
                second_place = copy.deepcopy(c)
            elif d_score == score_list[1]:
                second_place = copy.deepcopy(d)

        ai_parent = copy.deepcopy(winner)
        winner.export("best")
        winner.save_to_file("best")

        # restarts after 10 fails
        if fails > settings.fails_before_reset:
            print("fail threshold exceeded, resetting...")
            winner.export(str(max(score_list)))
            winner.save_to_file(str(max(score_list)))
            fails = 0
            generation = 0
            ai_parent = create_seeds(threshold)


def run_vs(
    threshold: int,
    load: bool,
    default_mutation_chance: float = settings.default_mutation_chance,
) -> None:
    if load:
        ai_parent = AI.from_file("best")
    else:
        ai_parent = create_seeds(threshold)

    fails = 0
    generation = 0
    winner = copy.deepcopy(ai_parent)
    mutation_chance = default_mutation_chance

    game_settings = GameSettings(
        civilisations=["huns"] * 2,
        names=["parent", "b"],
        map_size="tiny",
        game_time_limit=settings.game_time,
    )

    while True:
        generation += 1
        b = copy.deepcopy(ai_parent).mutate(mutation_chance)
        ai_parent.export("parent")
        b.export("b")
        launcher = Launcher(
            executable_path="C:\\Program Files\\Microsoft Games\\Age of Empires II\\age2_x1.5.exe",
            settings=game_settings,
        )
        games = launcher.launch_games(instances=7, round_robin=False)
        games = [game for game in games if game.status != GameStatus.EXCEPTED]
        master_score_list = [game.stats.scores for game in games if game.stats]
        real_wins = 0

        for scores in master_score_list:
            # try:
            if scores[1] > scores[0]:
                real_wins += 1

        # checks number of rounds with no improvement and sets annealing
        if real_wins < 4:
            fails += 1
            if fails % 2 == 0:
                mutation_chance = min(
                    default_mutation_chance + fails / (1000 * settings.anneal_amount),
                    0.2,
                )
            else:
                mutation_chance = max(
                    default_mutation_chance - fails / (1000 * settings.anneal_amount),
                    0.001,
                )
        else:
            print("new best")
            winner = copy.deepcopy(b)
            fails = 0
            mutation_chance = default_mutation_chance

        ai_parent = copy.deepcopy(winner)
        winner.export("best")
        winner.save_to_file("best")


def run_vs_other(
    threshold: int,
    load: bool,
    trainer: str,
    civs: list[str],
    robustness: int,
    infinite: bool,
    default_mutation_chance: float = settings.default_mutation_chance,
) -> None:
    # game_time = 7200

    if load:
        ai_parent = AI.from_file("best")
    else:
        ai_parent = create_seeds(threshold)

    second_place = copy.deepcopy(ai_parent)

    fails = 0
    generation = 0

    game_settings = GameSettings(
        civilisations=civs,
        names=["b", trainer],
        map_size="tiny",
        game_time_limit=settings.game_time,
        map_id="arabia",
    )

    best = 0
    mutation_chance = default_mutation_chance
    wins = 0

    while wins < 7 * robustness:
        generation += 1

        if generation != 1:
            crossed = crossover(ai_parent, second_place, mutation_chance)
            b = copy.deepcopy(crossed).mutate(mutation_chance)
        else:
            b = copy.deepcopy(ai_parent)

        b.export("b")

        wins = 0
        nest_break = False

        for i in range(robustness):
            launcher = Launcher(
                executable_path=EXECUTABLE_PATH,
                settings=game_settings,
            )

            master_score_list: list[list[int]] = []

            games = launcher.launch_games(instances=7, round_robin=False)
            games = [game for game in games if game.status != GameStatus.EXCEPTED]

            for game in games:
                if not game.stats:
                    continue
                if game.stats.winner == 1:
                    wins += 1
                master_score_list.append(game.stats.scores)
                if game.stats.elapsed_game_time < 100:
                    nest_break = True

            # for x in range(len(master_score_list)):
            #    if master_score_list[x][0] > master_score_list[x][1]:
            #        if times[x]/game_time < .9:
            #            wins += 1

            if wins == 0 or wins + (robustness - (i + 1)) * 7 < best or nest_break:
                # print(str(wins + (robustness - (i + 1)) * 7))
                # print("individual failed")
                break

        b_score = wins
        # train_score = score_list[1]

        # checks number of rounds with no improvement and sets annealing
        if b_score <= best:
            fails += 1
            if fails % 2 == 0:
                mutation_chance = min(
                    default_mutation_chance + fails / (1000 * settings.anneal_amount),
                    0.2,
                )
            else:
                mutation_chance = max(
                    default_mutation_chance - fails / (1000 * settings.anneal_amount),
                    0.001,
                )
        else:
            best = b_score
            print(str(best) + " real wins: " + str(wins))
            winner = copy.deepcopy(b)
            fails = 0
            mutation_chance = default_mutation_chance

            second_place = copy.deepcopy(ai_parent)
            ai_parent = copy.deepcopy(winner)
            winner.export("best")
            winner.save_to_file("best")

        if wins < 1 and generation == 1:
            generation = 0
            print("fail")

    if infinite:
        speed_train(trainer)


def run_vs_self(
    threshold: int,
    load: bool,
    robustness: int,
    infinite: bool,
    default_mutation_chance: float = settings.default_mutation_chance,
) -> None:
    if load:
        ai_parent = AI.from_file("best")
    else:
        ai_parent = create_seeds(threshold)

    fails = 0
    generation = 0

    game_settings = GameSettings(
        civilisations=[settings.civ] * 2,
        names=["b", "self"],
        map_size="tiny",
        game_time_limit=settings.game_time,
    )

    best = 0
    real_wins = 0
    max_real_wins = 0
    ai_parent.export("self")
    mutation_chance = default_mutation_chance

    while real_wins < 7 * robustness or infinite:
        generation += 1

        if generation != 1:
            b = copy.deepcopy(ai_parent).mutate(mutation_chance)
        else:
            b = copy.deepcopy(ai_parent)

        b.export("b")
        real_wins = 0

        launcher = Launcher(
            executable_path="C:\\Program Files\\Microsoft Games\\Age of Empires II\\age2_x1.5.exe",
            settings=game_settings,
        )

        for i in range(robustness):
            games = launcher.launch_games(instances=7, round_robin=False)
            games = [game for game in games if game.status != GameStatus.EXCEPTED]

            master_score_list: list[list[int]] = []
            times: list[int] = []

            for game in games:
                if not game.stats:
                    continue
                if game.stats.winner == 1:
                    real_wins += 1
                master_score_list.append(game.stats.scores)
                times.append(game.stats.elapsed_game_time)
                # except:
                #    pass
                #    print("fail")
            if (
                real_wins + (robustness - i) * 7 < best
            ):  # checks if possible to beat best, if not kills
                break

        b_score = real_wins

        # checks number of rounds with no improvement and sets annealing
        if b_score <= best:
            fails += 1
            if fails % 2 == 0:
                mutation_chance = min(
                    default_mutation_chance + fails / (1000 * settings.anneal_amount),
                    0.2,
                )
            else:
                mutation_chance = max(
                    default_mutation_chance - fails / (1000 * settings.anneal_amount),
                    0.001,
                )

        else:
            if real_wins > max_real_wins:
                max_real_wins = real_wins
            best = b_score
            print(f"{best} real wins: {real_wins}")
            winner = copy.deepcopy(b)
            fails = 0
            mutation_chance = default_mutation_chance

            ai_parent = copy.deepcopy(winner)
            winner.export("best")
            winner.save_to_file("best")

        if real_wins == 7 * robustness or fails > 30:
            if max_real_wins > 3.5 * robustness:
                winner.export("self")  # ! winner may not be defined
                print("success, reset!")
                backup()
                max_real_wins = 0
                generation = 1
                # k = eloDict.keys()
                # print(run_elo_once("best",eloDict,list(k)))
            # else:
            #    ai_parent = read_ai("best")
            #    print("fail,    reset!")
            #    max_real_wins = 0
            #    generation = 1
            best = 0


def run_robin(
    iterations: int, default_mutation_chance: float = settings.default_mutation_chance
):
    generation = 1
    fails = 0

    mutation_chance = default_mutation_chance

    ai_parent = AI.from_file("best")
    second_place = copy.deepcopy(ai_parent)

    game_settings = GameSettings(
        civilisations=["huns"] * 5,
        names=["parent", "b", "c", "d"],
        map_size="tiny",
        game_time_limit=settings.game_time,
        map_id="arabia",
    )

    while True:
        generation += 1
        crossed = crossover(ai_parent, second_place, mutation_chance)
        b = crossed.mutate(mutation_chance)
        crossed = crossover(ai_parent, second_place, mutation_chance)
        c = crossed.mutate(mutation_chance)
        crossed = crossover(ai_parent, second_place, mutation_chance)
        d = crossed.mutate(mutation_chance)

        ai_parent.export("parent")
        b.export("b")
        c.export("c")
        d.export("d")

        parent_score, b_score, c_score, d_score = (0, 0, 0, 0)
        score_list = [0, 0, 0, 0]

        for _ in range(iterations):
            launcher = Launcher(
                executable_path=EXECUTABLE_PATH,
                settings=game_settings,
            )
            # master_score_list = [[0,0],[0,0],[0,0],[0,0],[0,0],[0,0]]
            # [p,b],[p,c],[p,d],[b,c],[b,d][c,d]
            games = launcher.launch_games(round_robin=True)
            games = [game for game in games if game.status != GameStatus.EXCEPTED]
            master_score_list: list[list[int]] = []
            times: list[int] = []
            skip = False

            for game in games:
                if not game.stats:
                    continue
                master_score_list.append(game.stats.scores)
                times.append(game.stats.elapsed_game_time)

            if len(master_score_list) == 6:
                parent_temp_score, b_temp_score = extract_round_robin(
                    master_score_list[0], times[0]
                )
                parent_score += parent_temp_score
                b_score += b_temp_score

                parent_temp_score, c_temp_score = extract_round_robin(
                    master_score_list[1], times[1]
                )
                parent_score += parent_temp_score
                c_score += c_temp_score

                parent_temp_score, d_temp_score = extract_round_robin(
                    master_score_list[2], times[2]
                )
                parent_score += parent_temp_score
                d_score += d_temp_score

                b_temp_score, c_temp_score = extract_round_robin(
                    master_score_list[3], times[3]
                )
                b_score += b_temp_score
                c_score += c_temp_score

                b_temp_score, d_temp_score = extract_round_robin(
                    master_score_list[4], times[4]
                )
                b_score += b_temp_score
                d_score += d_temp_score

                c_temp_score, d_temp_score = extract_round_robin(
                    master_score_list[5], times[5]
                )
                c_score += c_temp_score
                d_score += d_temp_score

                score_list = [parent_score, b_score, c_score, d_score]
                score_list = sorted(score_list, reverse=True)
                fail = False

            else:
                parent_score, b_score, c_score, d_score = (0, 0, 0, 0)
                skip = True
                break

        if not skip:  # ! skip not necessarily defined
            # checks number of rounds with no improvement and sets annealing
            if parent_score == max(score_list) or max(score_list) < 3 * iterations + 1:
                fails += 1
                if fails % 2 == 0:
                    mutation_chance = min(
                        default_mutation_chance
                        + fails / (1000 * settings.anneal_amount),
                        0.2,
                    )
                else:
                    mutation_chance = max(
                        default_mutation_chance
                        - fails / (1000 * settings.anneal_amount),
                        0.001,
                    )
                fail = True
            else:
                fails = 0
                mutation_chance = default_mutation_chance

            if parent_score == max(score_list) or max(score_list) == 0:
                winner = copy.deepcopy(ai_parent)
                second_place = copy.deepcopy(ai_parent)
                print("parent won by score: " + str(parent_score))

            elif b_score == max(score_list):
                winner = copy.deepcopy(b)
                print("b won by score: " + str(b_score))

            elif c_score == max(score_list):
                winner = copy.deepcopy(c)
                print("c won by score: " + str(c_score))

            elif d_score == max(score_list):
                winner = copy.deepcopy(d)
                print("d won by score: " + str(d_score))

            if not fail:  # ! fail not necessarily defined
                if parent_score == score_list[1]:
                    second_place = copy.deepcopy(ai_parent)

                elif b_score == score_list[1]:
                    second_place = copy.deepcopy(b)

                elif c_score == score_list[1]:
                    second_place = copy.deepcopy(c)

                elif d_score == score_list[1]:
                    second_place = copy.deepcopy(d)

            ai_parent = copy.deepcopy(winner)  # ! winner not necessarily defined
            winner.export("best")
            winner.save_to_file("best")

            # if fails > fails_before_reset:
            #    print("fail threshold exceeded, resetting...")
            #    write_ai(winner, str(max(score_list)))
            #    save_ai(winner, str(max(score_list)))
            #    fails = 0
            #    generation = 0
            #    ai_parent = generate_ai()


def benchmarker(ai1: str, ai2: str, rounds: int, civs: list[str]) -> int:
    stats_dict: dict[str, list[list[str | float | int]]] = {}

    stats_dict[ai1] = [[], [], []]
    stats_dict[ai2] = [[], [], []]

    game_settings = GameSettings(
        civilisations=civs,
        names=[ai1, ai2],
        map_size="tiny",
        game_time_limit=settings.game_time,
    )

    ai1_wins = 0
    ai2_wins = 0
    stalemates = 0
    failed_games = 0
    time = 0

    rounds = int(rounds / 7)

    for _ in range(rounds):
        # print(x)

        launcher = Launcher(
            executable_path="C:\\Program Files\\Microsoft Games\\Age of Empires II\\age2_x1.5.exe",
            settings=game_settings,
        )

        games = launcher.launch_games(instances=7, round_robin=False)
        games = [
            game for game in games if game.status != GameStatus.EXCEPTED and game.stats
        ]

        master_score_list: list[list[int]] = []
        times: list[int] = []

        local_wins = 0

        for game in games:
            assert game.stats
            time = game.stats.elapsed_game_time
            score = game.stats.scores
            times.append(time)
            master_score_list.append(score)

            if game.stats.winner == 1:
                ai1_wins += 1
                local_wins += 1
                stats_dict[ai1][0].append("win")
                stats_dict[ai1][1].append(time)
                stats_dict[ai1][2].append(score[0])
                stats_dict[ai2][0].append("loss")
                stats_dict[ai2][1].append(time)
                stats_dict[ai2][2].append(score[0])

            elif game.stats.winner == 2:
                ai2_wins += 1
                stats_dict[ai1][0].append("loss")
                stats_dict[ai1][1].append(time)
                stats_dict[ai1][2].append(score[0])
                stats_dict[ai2][0].append("win")
                stats_dict[ai2][1].append(time)
                stats_dict[ai2][2].append(score[0])

            elif game.stats.winner == 0:
                stats_dict[ai1][0].append("draw")
                stats_dict[ai1][1].append(time)
                stats_dict[ai1][2].append(score[0])
                stats_dict[ai2][0].append("draw")
                stats_dict[ai2][1].append(time)
                stats_dict[ai2][2].append(score[0])
                stalemates += 1

        print(local_wins)

    print(f"{ai1_wins}/{ai2_wins}/{stalemates}/{failed_games}")
    # print("Average gametime: " + str(time/(ai1_wins + ai2_wins + stalemates)))

    with open(f"{ai1},{ai2}data.csv", "w+", encoding="utf-8") as f:
        f.write("AI,result,game time,score\n")
        for k, v in stats_dict.items():
            for a, b, c in zip(v[0], v[1], v[2]):
                f.write(f"{k},{a},{b},{c}\n")

    return ai1_wins


def backup() -> None:
    print("backing up best")
    with open("AI/best.txt", encoding="utf-8") as f:
        a = f.read()

    letters = [str(i) for i in range(10)]
    filename = "".join(random.choice(letters) for _ in range(10))

    with open(f"AI/{filename}.txt", "w+", encoding="utf-8") as f:
        f.write(a)


def group_train(
    group_list: list[str],
    do_break: bool,
    robustness: int,
    default_mutation_chance: float = settings.default_mutation_chance,
) -> None:
    game_time = 6000

    ai_parent = AI.from_file("best")
    second_place = AI.from_file("best")

    fails = 0
    generation = 0
    best = 0

    group_list_local = robustness * group_list.copy()

    mutation_chance = default_mutation_chance

    while True:
        generation += 1

        if generation != 1:
            crossed = crossover(ai_parent, second_place, mutation_chance)
            b = copy.deepcopy(crossed).mutate(mutation_chance)
        else:
            b = copy.deepcopy(ai_parent)

        b.export("b")

        string = ""
        b_score = 0
        nest_break = False
        score_dictionary = {x: 0 for x in group_list}
        start = time.time()

        for i, name in enumerate(group_list_local):
            if nest_break:
                break

            real_wins = 0
            game_settings = GameSettings(
                civilisations=[settings.civ, "huns"],
                names=["b", name],
                map_size="tiny",
                game_time_limit=game_time,
            )
            launcher = Launcher(
                executable_path=EXECUTABLE_PATH,
                settings=game_settings,
            )

            games = launcher.launch_games(instances=7, round_robin=False)
            games = [
                game
                for game in games
                if game.status != GameStatus.EXCEPTED and game.stats
            ]

            master_score_list: list[list[int]] = []
            times: list[int] = []
            string += group_list_local[i] + " : "

            for game in games:
                assert game.stats
                if game.stats.winner == 1:
                    real_wins += 1
                    score_dictionary[group_list_local[i]] += 1
                master_score_list.append(game.stats.scores)
                times.append(game.stats.elapsed_game_time)

            string += str(real_wins) + " "

            if real_wins == 0 and i == 0 and do_break:
                nest_break = True
                break

            # b_score = 0
            # for ai in score_dictionary:

            #    local_wins = score_dictionary[ai]
            #    if local_wins > 3.5 * robustness:
            #        b_score += 3.5 * robustness + (local_wins - 3.5 * robustness)/10
            #    else:
            #        b_score += local_wins

            #    #kills if beating best impossible; not efficient right now fix later
            #    hypothetical_max = b_score
            #    hypothetical_max += 3.85*(len(group_list_local)-i-1)

            #    hypothetical_max = min(hypothetical_max, 7 * len(group_list_local) / 2
            #                       + 7 * len(group_list_local) / 20 )

            #    #print(hypothetical_max)

            #    if hypothetical_max < best:
            #        print(hypothetical_max)
            #        nest_break = True
            #        break

        b_score = 0
        for ai in score_dictionary:
            local_wins = score_dictionary[ai]
            if local_wins > 3.5 * robustness:
                b_score += 3.5 * robustness + (local_wins - 3.5 * robustness) / 10
            else:
                b_score += local_wins

        # print(str(b_score) + " " + str(time.time() - start))

        # checks number of rounds with no improvement and sets annealing
        if b_score <= best:
            # print(string)
            fails += 1
            if fails % 2 == 0:
                mutation_chance = min(
                    default_mutation_chance + fails / (1000 * settings.anneal_amount),
                    0.2,
                )
            else:
                mutation_chance = max(
                    default_mutation_chance - fails / (1000 * settings.anneal_amount),
                    0.001,
                )
        else:
            best = b_score
            print(f"{string}total score : {best} Time: {time.time() - start}")
            winner = copy.deepcopy(b)
            fails = 0
            mutation_chance = default_mutation_chance

            second_place = copy.deepcopy(ai_parent)
            ai_parent = copy.deepcopy(winner)
            winner.export("best")
            winner.save_to_file("best")

        # if fails > 30:
        #    print("reset")
        #    best = 0
        #    generation = 0

        if best == 0 and generation == 1:
            generation = 0


def speed_train(trainer: str, default_mutation_chance: float = 0.01):
    mutation_chance = default_mutation_chance
    game_time = 7200
    # game_time = 3000

    ai_parent = AI.from_file("best")
    second_place = copy.deepcopy(ai_parent)

    fails = 0
    generation = 0

    best = -100000000000000000
    real_wins = 0

    while True:
        generation += 1

        if generation != 1:
            crossed = crossover(ai_parent, second_place, mutation_chance)
            b = copy.deepcopy(crossed).mutate(mutation_chance)
        else:
            b = copy.deepcopy(ai_parent)

        b.export("b")

        game_settings = GameSettings(
            civilisations=["huns"] * 2,
            names=["b", trainer],
            map_size="tiny",
            game_time_limit=int(game_time),
        )
        launcher = Launcher(
            executable_path="C:\\Program Files\\Microsoft Games\\Age of Empires II\\age2_x1.5.exe",
            settings=game_settings,
        )

        games = launcher.launch_games(instances=10, round_robin=False)
        games = [
            game for game in games if game.status != GameStatus.EXCEPTED and game.stats
        ]

        real_wins = 0
        b_score = 0

        for game in enumerate(games):
            assert isinstance(game, Game)
            assert game.stats
            if game.stats.winner == 1:
                real_wins += 1
                b_score -= game.stats.elapsed_game_time

        if real_wins < 10:
            b_score = -100000000000000000

        # print(real_wins)

        # except:
        #    pass
        #    print("fail")

        # checks number of rounds with no improvement and sets annealing
        if b_score <= best:
            # print(b_score)
            fails += 1
            if fails % 2 == 0:
                mutation_chance = min(
                    default_mutation_chance + fails / (1000 * settings.anneal_amount),
                    0.2,
                )
            else:
                mutation_chance = max(
                    default_mutation_chance - fails / (1000 * settings.anneal_amount),
                    0.001,
                )
        else:
            best = b_score
            print(f"New best: {best}")
            winner = copy.deepcopy(b)
            fails = 0
            mutation_chance = default_mutation_chance

            second_place = copy.deepcopy(ai_parent)
            ai_parent = copy.deepcopy(winner)
            winner.export("best")
            winner.save_to_file("best")

            if best > (-10 * game_time):
                game_time = (-1 * best / 10) / 0.75
                print(f"New time limit: {game_time}")

        if generation == 1 and best == -100000000000000000:
            generation = 0


def run_elo_once(ai: str, elo_dict: dict[str, float], group_list: list[str]) -> float:
    elo_league = Elo(k=20, g=1)

    game_time = 7200
    games_run: list[list[list[str] | str]] = []

    for name in group_list:
        elo_league.add_player(name, rating=elo_dict[name])

    elo_league.add_player(ai, rating=1600)

    for x, name in enumerate(group_list):
        if (
            name != ai
            and [group_list[x], ai] not in games_run
            and [ai, group_list[x]] not in games_run
        ):
            games_run.append([group_list[x], ai])

            game_settings = GameSettings(
                civilisations=[settings.civ, "huns"],
                names=[ai, group_list[x]],
                map_size="tiny",
                game_time_limit=game_time,
            )
            launcher = Launcher(
                executable_path=EXECUTABLE_PATH,
                settings=game_settings,
            )

            games = launcher.launch_games(instances=7, round_robin=False)
            games = [
                game
                for game in games
                if game.status != GameStatus.EXCEPTED
                if game.stats
            ]

            master_score_list: list[list[int]] = []
            times: list[int] = []

            wins = 0
            for game in games:
                assert game.stats
                master_score_list.append(game.stats.scores)
                times.append(game.stats.elapsed_game_time)
                if game.stats.winner == 1:
                    wins += 1
                    elo_league.game_over(
                        winner=ai, loser=group_list[x], winner_home=False
                    )
                elif game.stats.winner == 2:
                    elo_league.game_over(
                        winner=group_list[x], loser=ai, winner_home=False
                    )

            if x == 0 and wins == 0:
                # print("failed")
                return 0

    return elo_league.rating[ai]


def elo_train(default_mutation_chance: float = settings.default_mutation_chance):
    ai_parent = AI.from_file("best")
    second_place = AI.from_file("best")
    fails = 0
    generation = 0
    best = 0
    mutation_chance = default_mutation_chance
    while True:
        start = time.time()
        generation += 1

        if generation != 1:
            crossed = crossover(ai_parent, second_place, mutation_chance)
            b = copy.deepcopy(crossed).mutate(mutation_chance)
        else:
            b = copy.deepcopy(ai_parent)

        b.export("b")

        b_score = run_elo_once("b", elo_dict.copy(), list(settings.eloDict.keys()))

        # checks number of rounds with no improvement and sets annealing
        if b_score <= best:
            # print(str(b_score))
            fails += 1
            if fails % 2 == 0:
                mutation_chance = min(
                    default_mutation_chance + fails / (1000 * settings.anneal_amount),
                    0.2,
                )
            else:
                mutation_chance = max(
                    default_mutation_chance - fails / (1000 * settings.anneal_amount),
                    0.001,
                )
        else:
            best = b_score
            print("New Best: " + str(best))
            winner = copy.deepcopy(b)
            fails = 0
            mutation_chance = default_mutation_chance

            second_place = copy.deepcopy(ai_parent)
            ai_parent = copy.deepcopy(winner)
            winner.export("best")
            winner.save_to_file("best")

        if best == 0 and generation == 1:
            generation = 0

        print(str(time.time() - start))


def get_ai_data(group_list: list[str]) -> None:
    stats_dict: dict[str, list[list[str | int | float | list[int]]]] = {}
    elo_league = Elo(k=20, g=1)
    game_time = 7200
    games_run: list[list[str]] = []

    for name in group_list:
        elo_league.add_player(name, rating=1600)
        stats_dict[name] = [[], [], [], []]

    for name_1, name_2 in itertools.combinations(group_list, 2):
        print(name_1, name_2)
        if [name_1, name_2] in games_run or [name_2, name_1] in games_run:
            continue

        games_run.append([name_1, name_2])

        # REMOVE THIS later
        #
        #
        #
        #
        civs = ["huns", "huns"]
        # if group_list[x] == 'best':
        #    civs = ['franks','byzantine']
        # elif group_list[y] == 'best':
        #    ['byzantine','franks']

        game_settings = GameSettings(
            civilisations=civs,
            names=[name_1, name_2],
            map_size="tiny",
            game_time_limit=game_time,
        )
        launcher = Launcher(
            executable_path="C:\\Program Files\\Microsoft Games\\Age of Empires II\\age2_x1.5.exe",
            settings=game_settings,
        )

        games = launcher.launch_games(instances=7, round_robin=False)
        games = [
            game for game in games if game.status != GameStatus.EXCEPTED and game.stats
        ]

        master_score_list: list[list[int]] = []
        times: list[int] = []

        for game in games:
            assert game.stats
            master_score_list.append(game.stats.scores)
            times.append(game.stats.elapsed_game_time)

            if game.stats.elapsed_game_time < 0.9 * game_time:
                if game.stats.winner == 1:
                    stats_dict[name_1][0].append("win")
                    stats_dict[name_1][1].append(game.stats.elapsed_game_time)
                    stats_dict[name_1][2].append(game.stats.scores)
                    stats_dict[name_1][3].append(name_2)
                    stats_dict[name_2][0].append("loss")
                    stats_dict[name_2][1].append(game.stats.elapsed_game_time)
                    stats_dict[name_2][2].append(game.stats.scores)
                    stats_dict[name_2][3].append(name_1)
                    elo_league.game_over(
                        winner=name_1,
                        loser=name_2,
                        winner_home=False,
                    )

                elif game.stats.winner == 2:
                    stats_dict[name_1][0].append("loss")
                    stats_dict[name_1][1].append(game.stats.elapsed_game_time)
                    stats_dict[name_1][2].append(game.stats.scores)
                    stats_dict[name_1][3].append(name_2)
                    stats_dict[name_2][0].append("win")
                    stats_dict[name_2][1].append(game.stats.elapsed_game_time)
                    stats_dict[name_2][2].append(game.stats.scores)
                    stats_dict[name_2][3].append(name_1)
                    elo_league.game_over(
                        winner=name_2,
                        loser=name_1,
                        winner_home=False,
                    )

            else:
                stats_dict[name_1][0].append("draw")
                stats_dict[name_1][1].append(game.stats.elapsed_game_time)
                stats_dict[name_1][2].append(game.stats.scores)
                stats_dict[name_1][3].append(name_2)
                stats_dict[name_2][0].append("draw")
                stats_dict[name_2][1].append(game.stats.elapsed_game_time)
                stats_dict[name_2][2].append(game.stats.scores)
                stats_dict[name_2][3].append(name_1)

    print(elo_league.rating)
    print(stats_dict)
    with open("data.csv", "w+", encoding="utf-8") as f:
        f.write("AI,elo,result,game time,score,opponent\n")
        for k, v in stats_dict.items():
            for a, b, c, d in zip(v[0], v[1], v[2], v[3]):
                f.write(f"{k},{elo_league.rating[k]},{a},{b},{c},{d}\n")


def get_single_ai_data(
    civs: list[str],
    ai: str,
    group_list: list[str],
    dictionary: dict[str, int],
    runs: int,
) -> None:
    stats_dict: dict[str, list[list[str | int | float | list[int]]]] = {}
    elo_league = Elo(k=20, g=1)
    game_time = 7200

    for name in group_list:
        elo_league.add_player(name, rating=dictionary[name])

    elo_league.add_player(ai, rating=1600)

    stats_dict[ai] = [[], [], [], []]

    for i in range(runs):
        print(i)
        for name in group_list:
            game_settings = GameSettings(
                civilisations=civs,
                names=[ai, name],
                map_size="tiny",
                game_time_limit=game_time,
            )
            launcher = Launcher(
                executable_path=EXECUTABLE_PATH,
                settings=game_settings,
            )

            games = launcher.launch_games(instances=7, round_robin=False)
            games = [
                game
                for game in games
                if game.status != GameStatus.EXCEPTED and game.stats
            ]

            master_score_list: list[list[int]] = []
            times: list[int] = []

            wins = 0
            for game in games:
                assert game.stats
                master_score_list.append(game.stats.scores)
                times.append(game.stats.elapsed_game_time)
                if game.stats.winner == 1:
                    wins += 1

                if game.stats.winner == 0:
                    stats_dict[ai][0].append("draw")
                    stats_dict[ai][1].append(game.stats.elapsed_game_time)
                    stats_dict[ai][2].append(game.stats.scores[0])
                    stats_dict[ai][3].append(name)

                else:
                    if game.stats.winner == 1:
                        stats_dict[ai][0].append("win")
                        stats_dict[ai][1].append(game.stats.elapsed_game_time)
                        stats_dict[ai][2].append(game.stats.scores[0])
                        stats_dict[ai][3].append(name)

                        elo_league.game_over(winner=ai, loser=name, winner_home=False)

                    elif game.stats.winner == 2:
                        stats_dict[ai][0].append("loss")
                        stats_dict[ai][1].append(game.stats.elapsed_game_time)
                        stats_dict[ai][2].append(game.stats.scores[0])
                        stats_dict[ai][3].append(name)

                        elo_league.game_over(winner=name, loser=ai, winner_home=False)

    print(elo_league.rating)
    print(stats_dict)
    with open("data.csv", "w+", encoding="utf-8") as f:
        f.write("AI,elo,result,game time,score,opponent\n")
        for k, v in stats_dict.items():
            for a, b, c, d in zip(v[0], v[1], v[2], v[3]):
                f.write(f"{k},{elo_league.rating[k]},{a},{b},{c},{d}\n")


def benchmarker_slow(ai1: str, ai2: str, civs: list[str]) -> int:
    stats_dict: dict[str, list[list[str | float | list[int]]]] = {}

    stats_dict[ai1] = [[], [], []]
    stats_dict[ai2] = [[], [], []]

    game_settings = GameSettings(
        civilisations=civs,
        names=[ai1, ai2],
        map_size="tiny",
        game_time_limit=settings.game_time,
        speed=False,
    )

    ai1_wins = 0
    ai2_wins = 0
    stalemates = 0
    failed_games = 0
    time = 0

    launcher = Launcher(
        executable_path="C:\\Program Files\\Microsoft Games\\Age of Empires II\\age2_x1.5.exe",
        settings=game_settings,
    )

    games = launcher.launch_games(instances=40, round_robin=False)
    games = [
        game for game in games if game.status != GameStatus.EXCEPTED and game.stats
    ]

    for game in games:
        assert game.stats
        time += game.stats.elapsed_game_time

        if (
            game.stats.scores[0] > game.stats.scores[1]
            and game.stats.elapsed_game_time / settings.game_time < 0.9
        ):
            ai1_wins += 1
            stats_dict[ai1][0].append("win")
            stats_dict[ai1][1].append(game.stats.elapsed_game_time)
            stats_dict[ai1][2].append(game.stats.scores[0])
            stats_dict[ai2][0].append("loss")
            stats_dict[ai2][1].append(game.stats.elapsed_game_time)
            stats_dict[ai2][2].append(game.stats.scores[1])

        elif (
            game.stats.scores[0] < game.stats.scores[1]
            and game.stats.elapsed_game_time / settings.game_time < 0.9
        ):
            ai2_wins += 1
            stats_dict[ai1][0].append("loss")
            stats_dict[ai1][1].append(game.stats.elapsed_game_time)
            stats_dict[ai1][2].append(game.stats.scores[0])
            stats_dict[ai2][0].append("win")
            stats_dict[ai2][1].append(game.stats.elapsed_game_time)
            stats_dict[ai2][2].append(game.stats.scores[1])

        elif game.stats.scores == [0, 0]:
            failed_games += 1
        else:
            stats_dict[ai1][0].append("draw")
            stats_dict[ai1][1].append(game.stats.elapsed_game_time)
            stats_dict[ai1][2].append(game.stats.scores[0])
            stats_dict[ai2][0].append("draw")
            stats_dict[ai2][1].append(game.stats.elapsed_game_time)
            stats_dict[ai2][2].append(game.stats.scores[1])
            stalemates += 1

    print(f"{ai1_wins}/{ai2_wins}/{stalemates}/{failed_games}")
    # print("Average gametime: " + str(time/(ai1_wins + ai2_wins + stalemates)))

    with open(f"{ai1},{ai2} data.csv", "w+", encoding="utf-8") as f:
        f.write("AI,result,game t`ime,score\n")
        for k, v in stats_dict.items():
            for a, b, c in zip(v[0], v[1], v[2]):
                f.write(f"{k},{a},{b},{c}\n")

    return ai1_wins


def run_vs_other_slow(
    threshold: int,
    load: bool,
    trainer: str,
    civs: list[str],
    instance_count: int,
    infinite: bool,
    default_mutation_chance: float = settings.default_mutation_chance,
) -> None:
    game_time = 3600

    if load:
        ai_parent = AI.from_file(f"{settings.network_drive}best")
    else:
        ai_parent = create_seeds(threshold)

    second_place = copy.deepcopy(ai_parent)

    fails = 0
    generation = 0

    game_settings = GameSettings(
        civilisations=civs,
        names=["b", trainer],
        map_size="tiny",
        game_time_limit=game_time,
        speed=False,
    )

    best = 0
    real_wins = 0
    wins = 0
    mutation_chance = default_mutation_chance

    while wins < instance_count:
        ai_parent = AI.from_file(f"{settings.network_drive}best")
        generation += 1

        if generation != 1:
            crossed = crossover(ai_parent, second_place, mutation_chance)
            b = copy.deepcopy(crossed).mutate(mutation_chance)
        else:
            b = copy.deepcopy(ai_parent)

        b.export("b")

        launcher = Launcher(
            executable_path="C:\\Program Files\\Microsoft Games\\Age of Empires II\\age2_x1.5.exe",
            settings=game_settings,
        )

        games = launcher.launch_games(instances=instance_count, round_robin=False)
        games = [
            game for game in games if game.status != GameStatus.EXCEPTED and game.stats
        ]

        wins = 0
        draws = 0
        for game in games:
            assert game.stats
            if game.stats.elapsed_game_time / game_time < 0.9:
                if game.stats.scores[0] > game.stats.scores[1]:
                    wins += 1
            else:
                draws += 1

        score_list: list[float] = [0, 0]
        real_wins = 0
        multiplier = 1
        bonus = 1

        # does nothing but keeping so I don't have to debug
        for game in games:
            assert game.stats
            if game.stats.scores[0] > game.stats.scores[1]:
                multiplier = game_time / game.stats.elapsed_game_time
                if game.stats.elapsed_game_time / game_time < 0.9:
                    real_wins += 1
                    bonus += 10000000000 + 1000 * multiplier
            else:
                multiplier = 1

            score_list[0] += game.stats.scores[0]

        # score_list[0] += bonus
        score_list[0] = wins + draws / 100

        with open(f"{settings.network_drive}score.txt", encoding="utf-8") as f:
            best_temp = float(f.read())
            if best_temp > best:
                best = best_temp
                fails = 0
            if score_list == [0, 0]:
                continue
            if score_list != [0, 0]:
                b_score = score_list[0]

                # checks number of rounds with no improvement and sets annealing
                if b_score < best:
                    fails += 1
                    if fails % 2 == 0:
                        mutation_chance = min(
                            default_mutation_chance
                            + fails / (1000 * settings.anneal_amount),
                            0.2,
                        )
                    else:
                        mutation_chance = max(
                            default_mutation_chance
                            - fails / (1000 * settings.anneal_amount),
                            0.001,
                        )
                else:
                    best = b_score
                    print(f"{best} real wins: {real_wins}")
                    winner = copy.deepcopy(b)
                    fails = 0
                    mutation_chance = default_mutation_chance

                    second_place = copy.deepcopy(ai_parent)
                    ai_parent = copy.deepcopy(winner)
                    winner.export("best")
                    winner.save_to_file(f"{settings.network_drive}best")

                    with open(
                        f"{settings.network_drive}score.txt", "w+", encoding="utf-8"
                    ) as f:  # ! opening within the same context manager?
                        f.write(str(best))

        # if fails > 50:
        #    print("reset")
        #    best = 0
        #    generation = 0

        if real_wins < 1 and generation == 1:
            generation = 0
            print("fail")

    if infinite:
        speed_train(trainer)


def run_vs_self_slow(
    threshold: int,
    load: bool,
    instance_count: int,
    default_mutation_chance: float = settings.default_mutation_chance,
) -> None:
    game_time = 3600

    if load:
        ai_parent = AI.from_file("best")
    else:
        ai_parent = create_seeds(threshold)

    second_place = copy.deepcopy(ai_parent)

    fails = 0
    generation = 0

    game_settings = GameSettings(
        civilisations=["huns", "huns"],
        names=["b", "self"],
        map_size="tiny",
        game_time_limit=game_time,
        speed=False,
    )

    mutation_chance = default_mutation_chance
    ai_parent.export("self")

    while True:
        generation += 1

        crossed = crossover(ai_parent, second_place, mutation_chance)
        b = copy.deepcopy(crossed).mutate(mutation_chance)
        b.export("b")

        launcher = Launcher(
            executable_path="C:\\Program Files\\Microsoft Games\\Age of Empires II\\age2_x1.5.exe",
            settings=game_settings,
        )

        games = launcher.launch_games(instances=instance_count, round_robin=False)
        games = [
            game for game in games if game.status != GameStatus.EXCEPTED and game.stats
        ]

        wins = 0
        losses = 0
        draws = 0

        for game in games:
            if game.stats.winner == 1:
                wins += 1
            else:
                losses += 1

        b_score = wins
        # checks number of rounds with no improvement and sets annealing
        if b_score <= losses or b_score < draws:
            fails += 1
            if fails % 2 == 0:
                mutation_chance = min(
                    default_mutation_chance + fails / (1000 * settings.anneal_amount),
                    0.2,
                )
            else:
                mutation_chance = max(
                    default_mutation_chance - fails / (1000 * settings.anneal_amount),
                    0.001,
                )
        else:
            print(str("new best, scored ") + str(b_score))
            winner = copy.deepcopy(b)
            fails = 0
            mutation_chance = default_mutation_chance

            second_place = copy.deepcopy(ai_parent)
            ai_parent = copy.deepcopy(winner)
            winner.export("best")
            winner.export("self")
            winner.save_to_file("best")

        # if fails > 50:
        #    print("reset")
        #    best = 0
        #    generation = 0

        # for i in range(100):


def basic_benchmarker(ai1: str, ai2: str, rounds: int, civs: list[str]) -> int:
    stats_dict = {}

    stats_dict[ai1] = [[], [], []]
    stats_dict[ai2] = [[], [], []]

    game_settings = GameSettings(
        civilisations=civs,
        names=[ai1, ai2],
        map_size="tiny",
        game_time_limit=settings.game_time,
    )

    ai1_wins = 0
    ai2_wins = 0
    stalemates = 0
    rounds = int(rounds / 7)

    for _ in range(rounds):
        # print(x)

        launcher = Launcher(
            executable_path="C:\\Program Files\\Microsoft Games\\Age of Empires II\\age2_x1.5.exe",
            settings=game_settings,
        )

        games = launcher.launch_games(instances=7, round_robin=False)
        games = [
            game for game in games if game.status != GameStatus.EXCEPTED if game.stats
        ]

        local_wins = 0
        for game in games:
            assert game.stats
            if game.stats.winner == 1:
                ai1_wins += 1
                local_wins += 1
            elif game.stats.winner == 2:
                ai2_wins += 1
            else:
                stalemates += 1

    return ai1_wins


# get_ai_data(working_ais)
def run_vs_self_slow2(
    threshold: int,
    load: bool,
    robustness: int,
    infinite: bool,
    default_mutation_chance: float = settings.default_mutation_chance,
) -> None:
    if load:
        ai_parent = AI.from_file("best")
    else:
        ai_parent = create_seeds(threshold)

    fails = 0
    generation = 0

    game_settings = GameSettings(
        civilisations=[settings.civ] * 2,
        names=["b", "self"],
        map_size="tiny",
        game_time_limit=settings.game_time,
        speed=False,
    )

    best = 0
    real_wins = 0
    max_real_wins = 0
    ai_parent.export("self")
    mutation_chance = default_mutation_chance

    while real_wins < 7 * robustness or infinite:
        generation += 1

        if generation != 1:
            b = copy.deepcopy(ai_parent).mutate(mutation_chance)
        else:
            b = copy.deepcopy(ai_parent)

        b.export("b")
        real_wins = 0
        launcher = Launcher(
            executable_path="C:\\Program Files\\Microsoft Games\\Age of Empires II\\age2_x1.5.exe",
            settings=game_settings,
        )

        for i in range(robustness):
            games = launcher.launch_games(instances=30, round_robin=False)
            games = [
                game
                for game in games
                if game.status != GameStatus.EXCEPTED
                if game.stats
            ]
            for game in games:
                if game.stats.winner == 1:
                    real_wins += 1
                # except:
                #    pass
                #    print("fail")
            if (
                real_wins + (robustness - i) * 7 < best
            ):  # checks if possible to beat best, if not kills
                break

        b_score = real_wins

        # checks number of rounds with no improvement and sets annealing
        if b_score <= best:
            fails += 1
            if fails % 2 == 0:
                mutation_chance = min(
                    default_mutation_chance + fails / (1000 * settings.anneal_amount),
                    0.2,
                )
            else:
                mutation_chance = max(
                    default_mutation_chance - fails / (1000 * settings.anneal_amount),
                    0.001,
                )

        else:
            if real_wins > max_real_wins:
                max_real_wins = real_wins
            best = b_score
            print(str(best) + " real wins: " + str(real_wins))
            winner = copy.deepcopy(b)
            fails = 0
            mutation_chance = default_mutation_chance

            ai_parent = copy.deepcopy(winner)
            winner.export("best")
            winner.save_to_file("best")

        if real_wins == 7 * robustness or fails > 30:
            if max_real_wins > 3.5 * robustness:
                winner.export("self")  # ! winner may not be defined
                print("success, reset!")
                backup()
                max_real_wins = 0
                generation = 1
                # k = eloDict.keys()
                # print(run_elo_once("best",eloDict,list(k)))
            # else:
            #    ai_parent = read_ai("best")
            #    print("fail,    reset!")
            #    max_real_wins = 0
            #    generation = 1
            best = 0


def run_vs_selfs(
    threshold: int,
    load: bool,
    robustness: int,
    infinite: bool,
    default_mutation_chance: float = settings.default_mutation_chance,
) -> None:
    if load:
        ai_parent = AI.from_file("best")
    else:
        ai_parent = create_seeds(threshold)

    fails = 0
    generation = 0

    best = 0
    real_wins = 0

    self1 = copy.deepcopy(ai_parent)
    self2 = copy.deepcopy(ai_parent)
    self3 = copy.deepcopy(ai_parent)

    # print("loading ais, please edit if unwanted")
    # self1 = copy.deepcopy(ai_parent)
    # self2 = read_ai("4076768862")
    # self3 = read_ai("7004446841")

    self1.export("self")
    self2.export("self2")
    self3.export("self3")
    group_list = ["self", "self2", "self3"]

    test_ai = "king"

    mutation_chance = default_mutation_chance
    sets_to_be_run = len(group_list) * robustness

    while real_wins < 7 * robustness or infinite:
        generation += 1
        sets_run = 0

        if generation != 1:
            b = copy.deepcopy(ai_parent).mutate(mutation_chance)
        else:
            b = copy.deepcopy(ai_parent)

        b.export("b")
        real_wins = 0
        nest_break = False

        game_settings = GameSettings(
            civilisations=[settings.civ] * 2,
            names=["b", test_ai],
            map_size="tiny",
            game_time_limit=settings.game_time,
        )
        launcher = Launcher(
            executable_path="C:\\Program Files\\Microsoft Games\\Age of Empires II\\age2_x1.5.exe",
            settings=game_settings,
        )

        games = launcher.launch_games(instances=7, round_robin=False)
        games = [
            game for game in games if game.status != GameStatus.EXCEPTED and game.stats
        ]

        sets_run += 1

        test_wins = 0
        for game in games:
            assert game.stats
            if game.stats.winner == 1:
                test_wins += 1

        if test_wins < 6:
            continue
        for _ in range(robustness):
            if nest_break:
                break

            for name in group_list:
                game_settings = GameSettings(
                    civilisations=[settings.civ] * 2,
                    names=["b", name],
                    map_size="tiny",
                    game_time_limit=settings.game_time,
                )
                launcher = Launcher(
                    executable_path=EXECUTABLE_PATH,
                    settings=game_settings,
                )

                games = launcher.launch_games(instances=7, round_robin=False)
                games = [
                    game
                    for game in games
                    if game.status != GameStatus.EXCEPTED and game.stats
                ]

                sets_run += 1
                for game in games:
                    assert game.stats
                    if game.stats.winner == 1:
                        real_wins += 1

                    if game.stats.elapsed_game_time < 100:
                        # crashed
                        break

                # print(real_wins)
                # print((sets_to_be_run - sets_run)*7)
                # print(best)
                if nest_break:
                    break

                if best > real_wins + (sets_to_be_run - sets_run) * 7:
                    # print("impossible")
                    nest_break = True
                    break

        b_score = real_wins

        # checks number of rounds with no improvement and sets annealing
        if b_score <= best:
            fails += 1
            if fails % 2 == 0:
                mutation_chance = min(
                    default_mutation_chance + fails / (1000 * settings.anneal_amount),
                    0.2,
                )
            else:
                mutation_chance = max(
                    default_mutation_chance - fails / (1000 * settings.anneal_amount),
                    0.001,
                )

        else:
            best = b_score
            print(str(best) + " real wins: " + str(real_wins))
            winner = copy.deepcopy(b)
            fails = 0
            mutation_chance = default_mutation_chance

            ai_parent = copy.deepcopy(winner)
            winner.export("best")
            winner.save_to_file("best")

        if best == 7 * robustness * 3 or fails > 25:
            if best > 3.5 * robustness * 3:
                self3 = copy.deepcopy(self2)
                self2 = copy.deepcopy(self1)
                self1 = copy.deepcopy(winner)  # ! winner may not be defined

                self1.export("self")
                self2.export("self2")
                self3.export("self3")

                print("success, reset!")
                backup()
                generation = 1
                # k = eloDict.keys()
                # print(run_elo_once("best",eloDict,list(k)))
            else:
                ai_parent = AI.from_file("best")
                print("fail,    reset!")
                generation = 1
            best = 0
            fails = 0
