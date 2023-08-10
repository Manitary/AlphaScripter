import random
import time
import subprocess
import os
import signal
import copy
from game_launcher import Launcher, GameSettings, GameStatus
from Functions import *
from settings import *
from elosports.elo import Elo

ai_names = ["parent", "b", "c", "d", "e", "f", "g", "h"]


def setup_ai_files():
    for i in range(len(ai_names)):
        f = open(ai_names[i] + ".ai", "w+")
        f.write("")
        f.close()


# changed so only real wins count
def extract_round_robin(score, time):
    p1 = 0
    p2 = 0
    if score[0] > score[1]:
        p1 += 1
    elif score[1] > score[0]:
        p2 += 1

    if time < 0.9 * game_time:
        # print("real win!")
        p1 *= 1
        p2 *= 1

    if time > 0.9 * game_time:
        # print("real win!")
        p1 *= 0
        p2 *= 0

    return p1, p2


def create_seeds(threshold):

    while True:

        gs = GameSettings(
            civilisations=[civ] * 4,
            names=["parent", "parent"],
            game_time_limit=game_time,
            map_id="arabia",
        )

        master_score_list = [[0, 0, 0, 0, 0, 0, 0, 0]]

        # print("reset")

        ai_parent = generate_ai()

        write_ai(ai_parent, "parent")

        l = Launcher(
            executable_path="C:\\Program Files\\Microsoft Games\\Age of Empires II\\age2_x1.5.exe",
            settings=gs,
        )
        master_score_list = [
            game.stats.scores
            for game in l.launch_games(instances=1)
            if game.status != GameStatus.EXCEPTED
        ]

        score_list = [0, 0, 0, 0, 0, 0, 0, 0]

        if master_score_list is not None:

            for i in range(len(master_score_list)):
                try:
                    for ai in range(len(ai_names)):
                        score_list[ai] += master_score_list[i][ai]
                except:
                    pass

                print(max(score_list))

                if max(score_list) > threshold:
                    save_ai(ai_parent, "seed")
                    return ai_parent


def extract_ffa(master_score):

    a, b, c, d = (0, 0, 0, 0)

    for i in range(len(master_score)):
        local_score = master_score[i]

        sorted_list = sorted(local_score, reverse=True)

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


def run_ffa(threshold, load):

    game_time = 5000
    force_resign = False
    score_list = [[0, 0, 0, 0, 0, 0, 0, 0]]

    if load:
        ai_parent = read_ai("best")
    else:
        ai_parent = create_seeds(threshold)

    gs = GameSettings(
        civilisations=[civ] * 8,
        names=ai_names,
        game_time_limit=game_time,
        map_id="arabia",
    )

    second_place = copy.deepcopy(ai_parent)
    mutation_chance = default_mutation_chance

    generation = 1

    fails = 0

    while True:

        generation += 1

        crossed = crossover(ai_parent, second_place, mutation_chance)
        b = mutate_ai(crossed, mutation_chance)

        crossed = crossover(ai_parent, second_place, mutation_chance)
        c = mutate_ai(crossed, mutation_chance)

        crossed = crossover(ai_parent, second_place, mutation_chance)
        d = mutate_ai(crossed, mutation_chance)

        crossed = crossover(ai_parent, second_place, mutation_chance)
        e = mutate_ai(crossed, mutation_chance)

        crossed = crossover(ai_parent, second_place, mutation_chance)
        f = mutate_ai(crossed, mutation_chance)

        crossed = crossover(ai_parent, second_place, mutation_chance)
        g = mutate_ai(crossed, mutation_chance)

        crossed = crossover(ai_parent, second_place, mutation_chance)
        h = mutate_ai(crossed, mutation_chance)

        write_ai(ai_parent, "parent")
        write_ai(b, "b")
        write_ai(c, "c")
        write_ai(d, "d")
        write_ai(e, "e")
        write_ai(f, "f")
        write_ai(g, "g")
        write_ai(h, "h")

        # reads score
        l = Launcher(
            executable_path="C:\\Program Files\\Microsoft Games\\Age of Empires II\\age2_x1.5.exe",
            settings=gs,
        )
        master_score_list = [[0, 0, 0, 0, 0, 0, 0, 0]]
        master_score_list = [
            game.stats.scores
            for game in l.launch_games(instances=5)
            if game.status != GameStatus.EXCEPTED
        ]
        score_list = [0, 0, 0, 0, 0, 0, 0, 0]

        for i in range(len(master_score_list)):
            try:
                for ai in range(len(ai_names)):
                    score_list[ai] += master_score_list[i][ai]
            except:
                pass

        if (
            score_list == [0, 0, 0, 0, 0, 0, 0, 0]
            or score_list[0] == None
            or len(master_score_list) < 3
        ):
            if generation == 1:
                generation -= 1

        else:

            while [0, 0, 0, 0, 0, 0, 0, 0] in master_score_list:
                master_score_list.remove([0, 0, 0, 0, 0, 0, 0, 0])

            parent_score = score_list[0]
            b_score = score_list[1]
            c_score = score_list[2]
            d_score = score_list[3]
            e_score = score_list[4]
            f_score = score_list[5]
            g_score = score_list[6]
            h_score = score_list[7]

            score_list = sorted(score_list, reverse=True)

            # checks number of rounds with no improvement and sets annealing
            if parent_score == max(score_list):
                fails += 1
                if fails % 2 == 0:
                    mutation_chance = min(
                        default_mutation_chance + fails / (1000 * anneal_amount), 0.2
                    )
                else:
                    mutation_chance = max(
                        default_mutation_chance - fails / (1000 * anneal_amount), 0.001
                    )
            else:
                fails = 0
                mutation_chance = default_mutation_chance

            failed = False

            if parent_score == max(score_list):
                failed = True
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

            elif e_score == max(score_list):
                winner = copy.deepcopy(e)
                print("e won by score: " + str(e_score))

            elif f_score == max(score_list):
                winner = copy.deepcopy(f)
                print("f won by score: " + str(f_score))

            elif g_score == max(score_list):
                winner = copy.deepcopy(g)
                print("g won by score: " + str(g_score))

            elif h_score == max(score_list):
                winner = copy.deepcopy(h)
                print("h won by score: " + str(h_score))

            else:
                print("failed!!!")
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
            write_ai(winner, "best")
            save_ai(winner, "best")

            # restarts after 10 fails
            if fails > fails_before_reset:
                print("fail threshold exceeded, reseting...")
                write_ai(winner, str(max(score_list)))
                save_ai(winner, str(max(score_list)))
                fails = 0
                generation = 0
                ai_parent = generate_ai()


def run_ffa_four(threshold, load):

    game_time = 5000
    force_resign = False
    score_list = [[0, 0, 0, 0, 0, 0, 0, 0]]

    if load:
        ai_parent = read_ai("best")
    else:
        ai_parent = create_seeds(threshold)

    # temporary code
    # ai_parent = mutate_ai(copy.deepcopy(ai_parent))

    ai_names = ["parent", "b", "c", "d"]

    gs = GameSettings(
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
        b = mutate_ai(crossed, mutation_chance)

        crossed = crossover(ai_parent, second_place, mutation_chance)
        c = mutate_ai(crossed, mutation_chance)

        crossed = crossover(ai_parent, second_place, mutation_chance)
        d = mutate_ai(crossed, mutation_chance)

        write_ai(ai_parent, "parent")
        write_ai(b, "b")
        write_ai(c, "c")
        write_ai(d, "d")

        # reads score
        l = Launcher(
            executable_path="C:\\Program Files\\Microsoft Games\\Age of Empires II\\age2_x1.5.exe",
            settings=gs,
        )
        master_score_list = [[0, 0, 0, 0, 0, 0, 0, 0]]
        master_score_list = [
            game.stats.scores
            for game in l.launch_games(instances=5)
            if game.status != GameStatus.EXCEPTED
        ]
        score_list = [0, 0, 0, 0, 0, 0, 0, 0]

        for i in range(len(master_score_list)):
            try:
                for ai in range(len(ai_names)):
                    score_list[ai] += master_score_list[i][ai]
            except:
                pass

        if (
            score_list == [0, 0, 0, 0, 0, 0, 0, 0]
            or score_list[0] == None
            or len(master_score_list) < 3
        ):
            fails += 1
            if generation == 1:
                generation -= 1

        else:

            # parent_score, b_score, c_score, d_score = extract_ffa(master_score_list)

            # score_list = [parent_score, b_score, c_score, d_score]

            parent_score = score_list[0]
            b_score = score_list[1]
            c_score = score_list[2]
            d_score = score_list[3]

            score_list = sorted(score_list, reverse=True)

            # checks number of rounds with no improvement and sets annealing
            if parent_score == max(score_list):
                fails += 1
                if fails % 2 == 0:
                    mutation_chance = min(
                        default_mutation_chance + fails / (1000 * anneal_amount), 0.2
                    )
                else:
                    mutation_chance = max(
                        default_mutation_chance - fails / (1000 * anneal_amount), 0.001
                    )
            else:
                fails = 0
                mutation_chance = default_mutation_chance

            failed = False

            if parent_score == max(score_list):
                failed = True
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

            else:
                print("failed!!!")
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
            write_ai(winner, "best")
            save_ai(winner, "best")

            # restarts after 10 fails
            if fails > fails_before_reset:
                print("fail threshold exceeded, reseting...")
                write_ai(winner, str(max(score_list)))
                save_ai(winner, str(max(score_list)))
                fails = 0
                generation = 0
                ai_parent = create_seeds(threshold)


def run_vs(threshold, load):

    if load:
        ai_parent = read_ai("best")
    else:
        ai_parent = create_seeds(threshold)

    fails = 0
    generation = 0
    winner = copy.deepcopy(ai_parent)

    score_list = [[0, 0, 0, 0, 0, 0, 0, 0]]

    gs = GameSettings(
        civilisations=["huns"] * 2,
        names=["parent", "b"],
        map_size="tiny",
        game_time_limit=game_time,
    )

    while True:

        generation += 1

        b = mutate_ai(copy.deepcopy(ai_parent))

        write_ai(ai_parent, "parent")
        write_ai(b, "b")

        failed = False

        l = Launcher(
            executable_path="C:\\Program Files\\Microsoft Games\\Age of Empires II\\age2_x1.5.exe",
            settings=gs,
        )

        games = l.launch_games(instances=7, round_robin=False)
        games = [game for game in games if game.status != GameStatus.EXCEPTED]

        master_score_list = []
        times = []

        for game in games:
            master_score_list.append(game.stats.scores)
            times.append(game.stats.elapsed_game_time)

        score_list = [0, 0]
        real_wins = 0

        for i in range(len(master_score_list)):
            # try:

            if master_score_list[i][1] > master_score_list[i][0]:
                real_wins += 1

        b_score = real_wins

        # checks number of rounds with no improvement and sets annealing
        if real_wins < 4:
            fails += 1
            if fails % 2 == 0:
                mutation_chance = min(
                    default_mutation_chance + fails / (1000 * anneal_amount), 0.2
                )
            else:
                mutation_chance = max(
                    default_mutation_chance - fails / (1000 * anneal_amount), 0.001
                )
        else:
            print("new best")
            winner = copy.deepcopy(b)
            fails = 0
            mutation_chance = default_mutation_chance

        ai_parent = copy.deepcopy(winner)
        write_ai(winner, "best")
        save_ai(winner, "best")


def run_vs_other(threshold, load, trainer, civs, robustness, infinite):

    force_resign = True
    # game_time = 7200

    if load:
        ai_parent = read_ai("best")
    else:
        ai_parent = create_seeds(threshold)

    second_place = copy.deepcopy(ai_parent)

    fails = 0
    generation = 0

    score_list = [[0, 0, 0, 0, 0, 0, 0, 0]]

    gs = GameSettings(
        civilisations=civs,
        names=["b", trainer],
        map_size="tiny",
        game_time_limit=game_time,
        map_id="arabia",
    )

    best = 0
    real_wins = 0
    mutation_chance = default_mutation_chance

    wins = 0

    while wins < 7 * robustness:

        generation += 1

        if generation != 1:
            crossed = crossover(ai_parent, second_place, mutation_chance)
            b = mutate_ai(copy.deepcopy(crossed), mutation_chance)
        else:
            b = copy.deepcopy(ai_parent)

        write_ai(b, "b")

        wins = 0
        nest_break = False

        for i in range(robustness):

            l = Launcher(
                executable_path="C:\\Program Files\\Microsoft Games\\Age of Empires II\\age2_x1.5.exe",
                settings=gs,
            )

            master_score_list = []
            times = []

            games = l.launch_games(instances=7, round_robin=False)
            games = [game for game in games if game.status != GameStatus.EXCEPTED]

            for game in games:
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
                    default_mutation_chance + fails / (1000 * anneal_amount), 0.2
                )
            else:
                mutation_chance = max(
                    default_mutation_chance - fails / (1000 * anneal_amount), 0.001
                )
        else:
            best = b_score
            print(str(best) + " real wins: " + str(wins))
            winner = copy.deepcopy(b)
            fails = 0
            mutation_chance = default_mutation_chance

            second_place = copy.deepcopy(ai_parent)
            ai_parent = copy.deepcopy(winner)
            write_ai(winner, "best")
            save_ai(winner, "best")

        if wins < 1 and generation == 1:
            generation = 0
            print("fail")

    if infinite:
        speed_train(trainer)


def run_vs_self(threshold, load, robustness, infinite):

    force_resign = True

    if load:
        ai_parent = read_ai("best")
    else:
        ai_parent = create_seeds(threshold)

    fails = 0
    generation = 0

    score_list = [[0, 0, 0, 0, 0, 0, 0, 0]]

    gs = GameSettings(
        civilisations=[civ] * 2,
        names=["b", "self"],
        map_size="tiny",
        game_time_limit=game_time,
    )

    best = 0
    real_wins = 0
    max_real_wins = 0
    write_ai(ai_parent, "self")

    mutation_chance = default_mutation_chance

    while real_wins < 7 * robustness or infinite:

        generation += 1

        if generation != 1:
            b = mutate_ai(copy.deepcopy(ai_parent), mutation_chance)
        else:
            b = copy.deepcopy(ai_parent)

        write_ai(b, "b")

        failed = False

        score_list = [0, 0]
        real_wins = 0

        l = Launcher(
            executable_path="C:\\Program Files\\Microsoft Games\\Age of Empires II\\age2_x1.5.exe",
            settings=gs,
        )

        for z in range(robustness):

            games = l.launch_games(instances=7, round_robin=False)
            games = [game for game in games if game.status != GameStatus.EXCEPTED]

            master_score_list = []
            times = []

            for game in games:
                if game.stats.winner == 1:
                    real_wins += 1
                master_score_list.append(game.stats.scores)
                times.append(game.stats.elapsed_game_time)
                # except:
                #    pass
                #    print("fail")
            if (
                real_wins + (robustness - z) * 7 < best
            ):  # checks if possible to beat best, if not kills
                break

        b_score = real_wins
        train_score = score_list[1]

        # checks number of rounds with no improvement and sets annealing
        if b_score <= best:
            fails += 1
            if fails % 2 == 0:
                mutation_chance = min(
                    default_mutation_chance + fails / (1000 * anneal_amount), 0.2
                )
            else:
                mutation_chance = max(
                    default_mutation_chance - fails / (1000 * anneal_amount), 0.001
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
            write_ai(winner, "best")
            save_ai(winner, "best")

        if real_wins == 7 * robustness or fails > 30:
            if max_real_wins > 3.5 * robustness:
                write_ai(winner, "self")
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


def run_robin(iterations):

    generation = 1
    fails = 0

    mutation_chance = default_mutation_chance

    ai_parent = read_ai("best")

    second_place = copy.deepcopy(ai_parent)

    gs = GameSettings(
        civilisations=["huns"] * 5,
        names=["parent", "b", "c", "d"],
        map_size="tiny",
        game_time_limit=game_time,
        map_id="arabia",
    )

    while True:

        crossed = crossover(ai_parent, second_place, mutation_chance)
        b = mutate_ai(crossed, mutation_chance)

        crossed = crossover(ai_parent, second_place, mutation_chance)
        c = mutate_ai(crossed, mutation_chance)

        crossed = crossover(ai_parent, second_place, mutation_chance)
        d = mutate_ai(crossed, mutation_chance)

        write_ai(ai_parent, "parent")
        write_ai(b, "b")
        write_ai(c, "c")
        write_ai(d, "d")

        generation += 1

        failed = False

        parent_score, b_score, c_score, d_score = (0, 0, 0, 0)
        score_list = [0, 0, 0, 0]

        for trials in range(iterations):

            l = Launcher(
                executable_path="C:\\Program Files\\Microsoft Games\\Age of Empires II\\age2_x1.5.exe",
                settings=gs,
            )
            # master_score_list = [[0,0],[0,0],[0,0],[0,0],[0,0],[0,0]]
            # [p,b],[p,c],[p,d],[b,c],[b,d][c,d]
            games = l.launch_games(round_robin=True)
            games = [game for game in games if game.status != GameStatus.EXCEPTED]
            master_score_list = []
            times = []
            skip = False

            for game in games:
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

        if not skip:
            # checks number of rounds with no improvement and sets annealing
            if parent_score == max(score_list) or max(score_list) < 3 * iterations + 1:
                fails += 1
                if fails % 2 == 0:
                    mutation_chance = min(
                        default_mutation_chance + fails / (1000 * anneal_amount), 0.2
                    )
                else:
                    mutation_chance = max(
                        default_mutation_chance - fails / (1000 * anneal_amount), 0.001
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

            if not fail:

                if parent_score == score_list[1]:
                    second_place = copy.deepcopy(ai_parent)

                elif b_score == score_list[1]:
                    second_place = copy.deepcopy(b)

                elif c_score == score_list[1]:
                    second_place = copy.deepcopy(c)

                elif d_score == score_list[1]:
                    second_place = copy.deepcopy(d)

            ai_parent = copy.deepcopy(winner)
            write_ai(winner, "best")
            save_ai(winner, "best")

            # if fails > fails_before_reset:
            #    print("fail threshold exceeded, reseting...")
            #    write_ai(winner, str(max(score_list)))
            #    save_ai(winner, str(max(score_list)))
            #    fails = 0
            #    generation = 0
            #    ai_parent = generate_ai()


def benchmarker(ai1, ai2, rounds, civs):

    force_resign = True

    stats_dict = {}

    stats_dict[ai1] = [[], [], []]
    stats_dict[ai2] = [[], [], []]

    gs = GameSettings(
        civilisations=civs, names=[ai1, ai2], map_size="tiny", game_time_limit=game_time
    )

    ai1_wins = 0
    ai2_wins = 0
    stalemates = 0
    failed_games = 0
    time = 0

    rounds = int(rounds / 7)

    for x in range(rounds):

        # print(x)

        l = Launcher(
            executable_path="C:\\Program Files\\Microsoft Games\\Age of Empires II\\age2_x1.5.exe",
            settings=gs,
        )

        games = l.launch_games(instances=7, round_robin=False)
        games = [game for game in games if game.status != GameStatus.EXCEPTED]

        master_score_list = []
        times = []

        score_list = [0, 0]
        local_wins = 0

        for game in games:
            master_score_list.append(game.stats.scores)
            times.append(game.stats.elapsed_game_time)
            time = game.stats.elapsed_game_time
            score = game.stats.scores

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

    print(
        str(ai1_wins)
        + "/"
        + str(ai2_wins)
        + "/"
        + str(stalemates)
        + "/"
        + str(failed_games)
    )
    # print("Average gametime: " + str(time/(ai1_wins + ai2_wins + stalemates)))

    f = open(ai1 + "," + ai2 + " data.csv", "w+")
    f.write("AI,result,game time,score\n")
    for key in stats_dict:
        for e in range(len(stats_dict[key][0])):
            f.write(
                key
                + ","
                + str(stats_dict[key][0][e])
                + ","
                + str(stats_dict[key][1][e])
                + ","
                + str(stats_dict[key][2][e])
                + "\n"
            )
    f.close()

    return ai1_wins


def backup():
    print("backing up best")
    f = open("AI/" + "best.txt", "r")
    a = f.read()
    f.close()

    letters = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
    filename = "".join(random.choice(letters) for i in range(10))

    f = open("AI/" + filename + ".txt", "w+")
    f.write(a)
    f.close()


def group_train(group_list, do_break, robustness):

    force_resign = True
    game_time = 6000

    ai_parent = read_ai("best")
    second_place = read_ai("best")

    fails = 0
    generation = 0

    score_list = [[0, 0, 0]]

    best = 0

    group_list_local = robustness * group_list.copy()

    mutation_chance = default_mutation_chance

    while True:

        generation += 1

        if generation != 1:
            crossed = crossover(ai_parent, second_place, mutation_chance)
            b = mutate_ai(copy.deepcopy(crossed), mutation_chance)
        else:
            b = copy.deepcopy(ai_parent)

        write_ai(b, "b")

        string = ""
        b_score = 0
        nest_break = False

        score_dictionary = {}
        for i in range(len(group_list)):
            score_dictionary[group_list[i]] = 0

        start = time.time()

        for i in range(len(group_list_local)):

            if nest_break:
                break

            real_wins = 0

            gs = GameSettings(
                civilisations=[civ, "huns"],
                names=["b", group_list_local[i]],
                map_size="tiny",
                game_time_limit=game_time,
            )
            l = Launcher(
                executable_path="C:\\Program Files\\Microsoft Games\\Age of Empires II\\age2_x1.5.exe",
                settings=gs,
            )

            games = l.launch_games(instances=7, round_robin=False)
            games = [game for game in games if game.status != GameStatus.EXCEPTED]

            master_score_list = []
            times = []
            string_wins = 0
            string += group_list_local[i] + " : "

            for game in games:
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

            #    hypothetical_max = min(hypothetical_max, 7 * len(group_list_local) / 2 + 7 * len(group_list_local) / 20 )

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
                    default_mutation_chance + fails / (1000 * anneal_amount), 0.2
                )
            else:
                mutation_chance = max(
                    default_mutation_chance - fails / (1000 * anneal_amount), 0.001
                )
        else:
            best = b_score
            print(
                string
                + "total score : "
                + str(best)
                + " Time: "
                + str(time.time() - start)
            )
            winner = copy.deepcopy(b)
            fails = 0
            mutation_chance = default_mutation_chance

            second_place = copy.deepcopy(ai_parent)
            ai_parent = copy.deepcopy(winner)
            write_ai(winner, "best")
            save_ai(winner, "best")

        # if fails > 30:
        #    print("reset")
        #    best = 0
        #    generation = 0

        if best == 0 and generation == 1:
            generation = 0


def speed_train(trainer):

    default_mutation_chance = 0.01

    force_resign = True
    game_time = 7200
    # game_time = 3000

    ai_parent = read_ai("best")

    second_place = copy.deepcopy(ai_parent)

    fails = 0
    generation = 0

    best = -100000000000000000
    real_wins = 0

    while True:

        generation += 1

        if generation != 1:
            crossed = crossover(ai_parent, second_place, mutation_chance)
            b = mutate_ai(copy.deepcopy(crossed), mutation_chance)
        else:
            b = copy.deepcopy(ai_parent)

        write_ai(b, "b")

        failed = False

        master_score_list = []
        times = []

        gs = GameSettings(
            civilisations=["huns"] * 2,
            names=["b", trainer],
            map_size="tiny",
            game_time_limit=game_time,
        )
        l = Launcher(
            executable_path="C:\\Program Files\\Microsoft Games\\Age of Empires II\\age2_x1.5.exe",
            settings=gs,
        )

        games = l.launch_games(instances=10, round_robin=False)
        games = [game for game in games if game.status != GameStatus.EXCEPTED]

        for game in games:
            master_score_list.append(game.stats.scores)
            times.append(game.stats.elapsed_game_time)

        real_wins = 0
        b_score = 0

        for i in range(len(master_score_list)):
            if game.stats.winner == 1:
                real_wins += 1
                b_score -= times[i]

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
                    default_mutation_chance + fails / (1000 * anneal_amount), 0.2
                )
            else:
                mutation_chance = max(
                    default_mutation_chance - fails / (1000 * anneal_amount), 0.001
                )
        else:
            best = b_score
            print("New best: " + str(best))
            winner = copy.deepcopy(b)
            fails = 0
            mutation_chance = default_mutation_chance

            second_place = copy.deepcopy(ai_parent)
            ai_parent = copy.deepcopy(winner)
            write_ai(winner, "best")
            save_ai(winner, "best")

            if best > (-10 * game_time):
                game_time = (-1 * best / 10) / 0.75
                print("New time limit: " + str(game_time))

        if generation == 1 and best == -100000000000000000:
            generation = 0


def run_elo_once(ai, elo_dict, group_list):
    eloLeague = Elo(k=20, g=1)

    game_time = 7200

    score_list = [[0, 0, 0]]

    games_run = []

    for x in range(len(group_list)):
        eloLeague.addPlayer(group_list[x], rating=elo_dict[group_list[x]])

    eloLeague.addPlayer(ai, rating=1600)

    for x in range(len(group_list)):
        if (
            group_list[x] != ai
            and [group_list[x], ai] not in games_run
            and [ai, group_list[x]] not in games_run
        ):

            games_run.append([group_list[x], ai])

            gs = GameSettings(
                civilisations=[civ, "huns"],
                names=[ai, group_list[x]],
                map_size="tiny",
                game_time_limit=game_time,
            )
            l = Launcher(
                executable_path="C:\\Program Files\\Microsoft Games\\Age of Empires II\\age2_x1.5.exe",
                settings=gs,
            )

            games = l.launch_games(instances=7, round_robin=False)
            games = [game for game in games if game.status != GameStatus.EXCEPTED]

            master_score_list = []
            times = []

            wins = 0
            for game in games:
                master_score_list.append(game.stats.scores)
                times.append(game.stats.elapsed_game_time)
                if game.stats.winner == 1:
                    wins += 1
                    eloLeague.gameOver(winner=ai, loser=group_list[x], winnerHome=False)
                elif game.stats.winner == 2:
                    eloLeague.gameOver(winner=group_list[x], loser=ai, winnerHome=False)

            if x == 0 and wins == 0:
                # print("failed")
                return 0

    return eloLeague.ratingDict[ai]


def elo_train():

    force_resign = True
    game_time = 7200

    ai_parent = read_ai("best")
    second_place = read_ai("best")

    fails = 0
    generation = 0

    score_list = [[0, 0, 0]]

    best = 0

    while True:

        start = time.time()
        generation += 1

        if generation != 1:
            crossed = crossover(ai_parent, second_place, mutation_chance)
            b = mutate_ai(copy.deepcopy(crossed), mutation_chance)
        else:
            b = copy.deepcopy(ai_parent)

        write_ai(b, "b")

        b_score = run_elo_once("b", elo_dict.copy(), list(eloDict.keys()))

        # checks number of rounds with no improvement and sets annealing
        if b_score <= best:
            # print(str(b_score))
            fails += 1
            if fails % 2 == 0:
                mutation_chance = min(
                    default_mutation_chance + fails / (1000 * anneal_amount), 0.2
                )
            else:
                mutation_chance = max(
                    default_mutation_chance - fails / (1000 * anneal_amount), 0.001
                )
        else:
            best = b_score
            print("New Best: " + str(best))
            winner = copy.deepcopy(b)
            fails = 0
            mutation_chance = default_mutation_chance

            second_place = copy.deepcopy(ai_parent)
            ai_parent = copy.deepcopy(winner)
            write_ai(winner, "best")
            save_ai(winner, "best")

        if best == 0 and generation == 1:
            generation = 0

        print(str(time.time() - start))


def get_ai_data(group_list):

    stats_dict = {}

    eloLeague = Elo(k=20, g=1)

    game_time = 7200

    score_list = [[0, 0, 0]]

    games_run = []

    for x in range(len(group_list)):
        eloLeague.addPlayer(group_list[x], rating=1600)
        stats_dict[group_list[x]] = [[], [], [], []]

    for x in range(len(group_list)):
        print(str(x))
        for y in range(len(group_list)):

            if (
                group_list[x] != group_list[y]
                and [group_list[x], group_list[y]] not in games_run
                and [group_list[y], group_list[x]] not in games_run
            ):

                games_run.append([group_list[x], group_list[y]])

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

                gs = GameSettings(
                    civilisations=civs,
                    names=[group_list[x], group_list[y]],
                    map_size="tiny",
                    game_time_limit=game_time,
                )
                l = Launcher(
                    executable_path="C:\\Program Files\\Microsoft Games\\Age of Empires II\\age2_x1.5.exe",
                    settings=gs,
                )

                games = l.launch_games(instances=7, round_robin=False)
                games = [game for game in games if game.status != GameStatus.EXCEPTED]

                master_score_list = []
                times = []

                for game in games:
                    master_score_list.append(game.stats.scores)
                    times.append(game.stats.elapsed_game_time)

                    if game.stats.elapsed_game_time < 0.9 * game_time:
                        if game.stats.winner == 1:
                            stats_dict[group_list[x]][0].append("win")
                            stats_dict[group_list[x]][1].append(
                                game.stats.elapsed_game_time
                            )
                            stats_dict[group_list[x]][2].append(game.stats.scores)
                            stats_dict[group_list[x]][3].append(group_list[y])
                            stats_dict[group_list[y]][0].append("loss")
                            stats_dict[group_list[y]][1].append(
                                game.stats.elapsed_game_time
                            )
                            stats_dict[group_list[y]][2].append(game.stats.scores)
                            stats_dict[group_list[y]][3].append(group_list[x])
                            eloLeague.gameOver(
                                winner=group_list[x],
                                loser=group_list[y],
                                winnerHome=False,
                            )

                        elif game.stats.winner == 2:
                            stats_dict[group_list[x]][0].append("loss")
                            stats_dict[group_list[x]][1].append(
                                game.stats.elapsed_game_time
                            )
                            stats_dict[group_list[x]][2].append(game.stats.scores)
                            stats_dict[group_list[x]][3].append(group_list[y])
                            stats_dict[group_list[y]][0].append("win")
                            stats_dict[group_list[y]][1].append(
                                game.stats.elapsed_game_time
                            )
                            stats_dict[group_list[y]][2].append(game.stats.scores)
                            stats_dict[group_list[y]][3].append(group_list[x])
                            eloLeague.gameOver(
                                winner=group_list[y],
                                loser=group_list[x],
                                winnerHome=False,
                            )

                    else:
                        stats_dict[group_list[x]][0].append("draw")
                        stats_dict[group_list[x]][1].append(
                            game.stats.elapsed_game_time
                        )
                        stats_dict[group_list[x]][2].append(game.stats.scores)
                        stats_dict[group_list[x]][3].append(group_list[y])
                        stats_dict[group_list[y]][0].append("draw")
                        stats_dict[group_list[y]][1].append(
                            game.stats.elapsed_game_time
                        )
                        stats_dict[group_list[y]][2].append(game.stats.scores)
                        stats_dict[group_list[y]][3].append(group_list[x])

    print(eloLeague.ratingDict)
    print(stats_dict)
    f = open("data.csv", "w+")
    f.write("AI,elo,result,game time,score,opponent\n")
    for key in stats_dict:
        for e in range(len(stats_dict[key][0])):
            f.write(
                key
                + ","
                + str(eloLeague.ratingDict[key])
                + ","
                + str(stats_dict[key][0][e])
                + ","
                + str(stats_dict[key][1][e])
                + ","
                + str(stats_dict[key][2][e])
                + ","
                + str(stats_dict[key][3][e])
                + "\n"
            )
    f.close()


def get_single_ai_data(civs, ai, group_list, dictionary, runs):

    stats_dict = {}

    eloLeague = Elo(k=20, g=1)

    game_time = 7200

    score_list = [[0, 0, 0]]

    games_run = []

    for x in range(len(group_list)):
        eloLeague.addPlayer(group_list[x], rating=dictionary[group_list[x]])

    eloLeague.addPlayer(ai, rating=1600)

    stats_dict[ai] = [[], [], [], []]

    for r in range(runs):
        print(r)
        for y in range(len(group_list)):

            gs = GameSettings(
                civilisations=civs,
                names=[ai, group_list[y]],
                map_size="tiny",
                game_time_limit=game_time,
            )
            l = Launcher(
                executable_path="C:\\Program Files\\Microsoft Games\\Age of Empires II\\age2_x1.5.exe",
                settings=gs,
            )

            games = l.launch_games(instances=7, round_robin=False)
            games = [game for game in games if game.status != GameStatus.EXCEPTED]

            master_score_list = []
            times = []

            wins = 0
            for game in games:
                master_score_list.append(game.stats.scores)
                times.append(game.stats.elapsed_game_time)
                if game.stats.winner == 1:
                    wins += 1

                if game.stats.winner == 0:

                    stats_dict[ai][0].append("draw")
                    stats_dict[ai][1].append(game.stats.elapsed_game_time)
                    stats_dict[ai][2].append(game.stats.scores[0])
                    stats_dict[ai][3].append(group_list[y])

                else:
                    if game.stats.winner == 1:
                        stats_dict[ai][0].append("win")
                        stats_dict[ai][1].append(game.stats.elapsed_game_time)
                        stats_dict[ai][2].append(game.stats.scores[0])
                        stats_dict[ai][3].append(group_list[y])

                        eloLeague.gameOver(
                            winner=ai, loser=group_list[y], winnerHome=False
                        )

                    elif game.stats.winner == 2:
                        stats_dict[ai][0].append("loss")
                        stats_dict[ai][1].append(game.stats.elapsed_game_time)
                        stats_dict[ai][2].append(game.stats.scores[0])
                        stats_dict[ai][3].append(group_list[y])

                        eloLeague.gameOver(
                            winner=group_list[y], loser=ai, winnerHome=False
                        )

    print(eloLeague.ratingDict)
    print(stats_dict)
    f = open("data.csv", "w+")
    f.write("AI,elo,result,game time,score,opponent\n")
    for key in stats_dict:
        for e in range(len(stats_dict[key][0])):
            f.write(
                key
                + ","
                + str(eloLeague.ratingDict[key])
                + ","
                + str(stats_dict[key][0][e])
                + ","
                + str(stats_dict[key][1][e])
                + ","
                + str(stats_dict[key][2][e])
                + ","
                + str(stats_dict[key][3][e])
                + "\n"
            )
    f.close()


def benchmarker_slow(ai1, ai2, civs):

    force_resign = True

    stats_dict = {}

    stats_dict[ai1] = [[], [], []]
    stats_dict[ai2] = [[], [], []]

    gs = GameSettings(
        civilisations=civs,
        names=[ai1, ai2],
        map_size="tiny",
        game_time_limit=game_time,
        speed=False,
    )

    ai1_wins = 0
    ai2_wins = 0
    stalemates = 0
    failed_games = 0
    time = 0

    l = Launcher(
        executable_path="C:\\Program Files\\Microsoft Games\\Age of Empires II\\age2_x1.5.exe",
        settings=gs,
    )

    games = l.launch_games(instances=40, round_robin=False)
    games = [game for game in games if game.status != GameStatus.EXCEPTED]

    master_score_list = []
    times = []

    for game in games:
        master_score_list.append(game.stats.scores)
        times.append(game.stats.elapsed_game_time)

    score_list = [0, 0]

    for i in range(len(master_score_list)):

        time += times[i]

        if (
            master_score_list[i][0] > master_score_list[i][1]
            and times[i] / game_time < 0.9
        ):
            ai1_wins += 1
            stats_dict[ai1][0].append("win")
            stats_dict[ai1][1].append(times[i])
            stats_dict[ai1][2].append(master_score_list[i][0])
            stats_dict[ai2][0].append("loss")
            stats_dict[ai2][1].append(times[i])
            stats_dict[ai2][2].append(master_score_list[i][1])

        elif (
            master_score_list[i][0] < master_score_list[i][1]
            and times[i] / game_time < 0.9
        ):
            ai2_wins += 1
            stats_dict[ai1][0].append("loss")
            stats_dict[ai1][1].append(times[i])
            stats_dict[ai1][2].append(master_score_list[i][0])
            stats_dict[ai2][0].append("win")
            stats_dict[ai2][1].append(times[i])
            stats_dict[ai2][2].append(master_score_list[i][1])

        elif master_score_list[i] == [0, 0]:
            failed_games += 1
        else:
            stats_dict[ai1][0].append("draw")
            stats_dict[ai1][1].append(times[i])
            stats_dict[ai1][2].append(master_score_list[i][0])
            stats_dict[ai2][0].append("draw")
            stats_dict[ai2][1].append(times[i])
            stats_dict[ai2][2].append(master_score_list[i][1])
            stalemates += 1

    print(
        str(ai1_wins)
        + "/"
        + str(ai2_wins)
        + "/"
        + str(stalemates)
        + "/"
        + str(failed_games)
    )
    # print("Average gametime: " + str(time/(ai1_wins + ai2_wins + stalemates)))

    f = open(ai1 + "," + ai2 + " data.csv", "w+")
    f.write("AI,result,game time,score\n")
    for key in stats_dict:
        for e in range(len(stats_dict[key][0])):
            f.write(
                key
                + ","
                + str(stats_dict[key][0][e])
                + ","
                + str(stats_dict[key][1][e])
                + ","
                + str(stats_dict[key][2][e])
                + "\n"
            )
    f.close()

    return ai1_wins


def run_vs_other_slow(threshold, load, trainer, civs, instance_count, infinite):

    force_resign = True
    game_time = 3600

    if load:
        ai_parent = read_ai(network_drive + "best")
    else:
        ai_parent = create_seeds(threshold)

    second_place = copy.deepcopy(ai_parent)

    fails = 0
    generation = 0

    score_list = [[0, 0, 0, 0, 0, 0, 0, 0]]

    gs = GameSettings(
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

        ai_parent = read_ai(network_drive + "best")
        generation += 1

        if generation != 1:
            crossed = crossover(ai_parent, second_place, mutation_chance)
            b = mutate_ai(copy.deepcopy(crossed), mutation_chance)
        else:
            b = copy.deepcopy(ai_parent)

        write_ai(b, "b")

        failed = False

        master_score_list = []
        times = []

        l = Launcher(
            executable_path="C:\\Program Files\\Microsoft Games\\Age of Empires II\\age2_x1.5.exe",
            settings=gs,
        )

        games = l.launch_games(instances=instance_count, round_robin=False)
        games = [game for game in games if game.status != GameStatus.EXCEPTED]

        for game in games:
            master_score_list.append(game.stats.scores)
            times.append(game.stats.elapsed_game_time)

        wins = 0
        draws = 0
        for i in range(len(master_score_list)):
            if times[i] / game_time < 0.9:
                if master_score_list[i][0] > master_score_list[i][1]:
                    wins += 1
            else:
                draws += 1

        score_list = [0, 0]
        real_wins = 0
        multiplier = 1
        bonus = 1

        # does nothing but keeping so I don't have to debug
        for i in range(len(master_score_list)):
            # try:

            if master_score_list[i][0] > master_score_list[i][1]:
                multiplier = game_time / times[i]
                # multiplier = 1
                if times[i] / game_time < 0.9:
                    real_wins += 1
                    bonus += 10000000000 + 1000 * multiplier
            else:
                multiplier = 1

            score_list[0] += master_score_list[i][0]
            # except:
            #    pass
            #    print("fail")

        # score_list[0] += bonus
        score_list[0] = wins + draws / 100

        f = open(network_drive + "score.txt", "r")
        best_temp = float(f.read())
        if best_temp > best:
            best = best_temp
            fails = 0

        if score_list != [0, 0]:

            b_score = score_list[0]
            train_score = score_list[1]

            # checks number of rounds with no improvement and sets annealing
            if b_score < best:
                fails += 1
                if fails % 2 == 0:
                    mutation_chance = min(
                        default_mutation_chance + fails / (1000 * anneal_amount), 0.2
                    )
                else:
                    mutation_chance = max(
                        default_mutation_chance - fails / (1000 * anneal_amount), 0.001
                    )
            else:
                best = b_score
                print(str(best) + " real wins: " + str(real_wins))
                winner = copy.deepcopy(b)
                fails = 0
                mutation_chance = default_mutation_chance

                second_place = copy.deepcopy(ai_parent)
                ai_parent = copy.deepcopy(winner)
                write_ai(winner, "best")
                save_ai(winner, network_drive + "best")

                f = open(network_drive + "score.txt", "w+")
                f.write(str(best))
                f.close()

        # if fails > 50:
        #    print("reset")
        #    best = 0
        #    generation = 0

        if real_wins < 1 and generation == 1:
            generation = 0
            print("fail")

    if infinite:
        speed_train(trainer)


def run_vs_self_slow(threshold, load, instance_count):

    force_resign = True
    game_time = 3600

    if load:
        ai_parent = read_ai("best")
    else:
        ai_parent = create_seeds(threshold)

    second_place = copy.deepcopy(ai_parent)

    fails = 0
    generation = 0

    score_list = [[0, 0, 0, 0, 0, 0, 0, 0]]

    gs = GameSettings(
        civilisations=["huns", "huns"],
        names=["b", "self"],
        map_size="tiny",
        game_time_limit=game_time,
        speed=False,
    )

    best = 0
    real_wins = 0
    mutation_chance = default_mutation_chance
    write_ai(ai_parent, "self")

    while True:

        generation += 1

        crossed = crossover(ai_parent, second_place, mutation_chance)
        b = mutate_ai(copy.deepcopy(crossed), mutation_chance)

        write_ai(b, "b")

        failed = False

        master_score_list = []
        times = []

        l = Launcher(
            executable_path="C:\\Program Files\\Microsoft Games\\Age of Empires II\\age2_x1.5.exe",
            settings=gs,
        )

        games = l.launch_games(instances=instance_count, round_robin=False)
        games = [game for game in games if game.status != GameStatus.EXCEPTED]

        wins = 0
        losses = 0
        draws = 0

        for game in games:
            if game.stats.winner == 1:
                wins += 1
            else:
                losses += 1

        score_list = [0, 0]
        real_wins = 0
        multiplier = 1
        bonus = 1

        b_score = wins
        train_score = score_list[1]

        # checks number of rounds with no improvement and sets annealing
        if b_score <= losses or b_score < draws:
            fails += 1
            if fails % 2 == 0:
                mutation_chance = min(
                    default_mutation_chance + fails / (1000 * anneal_amount), 0.2
                )
            else:
                mutation_chance = max(
                    default_mutation_chance - fails / (1000 * anneal_amount), 0.001
                )
        else:
            print(str("new best, scored ") + str(b_score))
            winner = copy.deepcopy(b)
            fails = 0
            mutation_chance = default_mutation_chance

            second_place = copy.deepcopy(ai_parent)
            ai_parent = copy.deepcopy(winner)
            write_ai(winner, "best")
            write_ai(winner, "self")
            save_ai(winner, "best")

        # if fails > 50:
        #    print("reset")
        #    best = 0
        #    generation = 0

        # for i in range(100):


def basic_benchmarker(ai1, ai2, rounds, civs):

    force_resign = True

    stats_dict = {}

    stats_dict[ai1] = [[], [], []]
    stats_dict[ai2] = [[], [], []]

    gs = GameSettings(
        civilisations=civs, names=[ai1, ai2], map_size="tiny", game_time_limit=game_time
    )

    ai1_wins = 0
    ai2_wins = 0
    stalemates = 0
    failed_games = 0
    time = 0

    rounds = int(rounds / 7)

    for x in range(rounds):

        # print(x)

        l = Launcher(
            executable_path="C:\\Program Files\\Microsoft Games\\Age of Empires II\\age2_x1.5.exe",
            settings=gs,
        )

        games = l.launch_games(instances=7, round_robin=False)
        games = [game for game in games if game.status != GameStatus.EXCEPTED]

        master_score_list = []
        times = []

        score_list = [0, 0]
        local_wins = 0

        for game in games:
            master_score_list.append(game.stats.scores)
            times.append(game.stats.elapsed_game_time)
            time = game.stats.elapsed_game_time
            score = game.stats.scores

            if game.stats.winner == 1:
                ai1_wins += 1
                local_wins += 1

            elif game.stats.winner == 2:
                ai2_wins += 1

            else:
                stalemates += 1

    return ai1_wins


# get_ai_data(working_ais)
def run_vs_self_slow2(threshold, load, robustness, infinite):

    if load:
        ai_parent = read_ai("best")
    else:
        ai_parent = create_seeds(threshold)

    fails = 0
    generation = 0

    score_list = [[0, 0, 0, 0, 0, 0, 0, 0]]

    gs = GameSettings(
        civilisations=[civ] * 2,
        names=["b", "self"],
        map_size="tiny",
        game_time_limit=game_time,
        speed=False,
    )

    best = 0
    real_wins = 0
    max_real_wins = 0
    write_ai(ai_parent, "self")

    mutation_chance = default_mutation_chance

    while real_wins < 7 * robustness or infinite:

        generation += 1

        if generation != 1:
            b = mutate_ai(copy.deepcopy(ai_parent), mutation_chance)
        else:
            b = copy.deepcopy(ai_parent)

        write_ai(b, "b")

        failed = False

        score_list = [0, 0]
        real_wins = 0

        l = Launcher(
            executable_path="C:\\Program Files\\Microsoft Games\\Age of Empires II\\age2_x1.5.exe",
            settings=gs,
        )

        for z in range(robustness):

            games = l.launch_games(instances=30, round_robin=False)
            games = [game for game in games if game.status != GameStatus.EXCEPTED]

            master_score_list = []
            times = []

            for game in games:
                if game.stats.winner == 1:
                    real_wins += 1
                master_score_list.append(game.stats.scores)
                times.append(game.stats.elapsed_game_time)
                # except:
                #    pass
                #    print("fail")
            if (
                real_wins + (robustness - z) * 7 < best
            ):  # checks if possible to beat best, if not kills
                break

        b_score = real_wins
        train_score = score_list[1]

        # checks number of rounds with no improvement and sets annealing
        if b_score <= best:
            fails += 1
            if fails % 2 == 0:
                mutation_chance = min(
                    default_mutation_chance + fails / (1000 * anneal_amount), 0.2
                )
            else:
                mutation_chance = max(
                    default_mutation_chance - fails / (1000 * anneal_amount), 0.001
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
            write_ai(winner, "best")
            save_ai(winner, "best")

        if real_wins == 7 * robustness or fails > 30:
            if max_real_wins > 3.5 * robustness:
                write_ai(winner, "self")
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


def run_vs_selfs(threshold, load, robustness, infinite):

    force_resign = True

    if load:
        ai_parent = read_ai("best")
    else:
        ai_parent = create_seeds(threshold)

    fails = 0
    generation = 0

    score_list = [[0, 0, 0, 0, 0, 0, 0, 0]]

    best = 0
    real_wins = 0
    max_real_wins = 0

    self1 = copy.deepcopy(ai_parent)
    self2 = copy.deepcopy(ai_parent)
    self3 = copy.deepcopy(ai_parent)

    # print("loading ais, please edit if unwanted")
    # self1 = copy.deepcopy(ai_parent)
    # self2 = read_ai("4076768862")
    # self3 = read_ai("7004446841")

    write_ai(self1, "self")
    write_ai(self2, "self2")
    write_ai(self3, "self3")
    group_list = ["self", "self2", "self3"]

    test_ai = "king"

    mutation_chance = default_mutation_chance
    sets_to_be_run = len(group_list) * robustness

    while real_wins < 7 * robustness or infinite:

        generation += 1
        sets_run = 0

        if generation != 1:
            b = mutate_ai(copy.deepcopy(ai_parent), mutation_chance)
        else:
            b = copy.deepcopy(ai_parent)

        write_ai(b, "b")

        failed = False

        score_list = [0, 0]
        real_wins = 0
        nest_break = False

        gs = GameSettings(
            civilisations=[civ] * 2,
            names=["b", test_ai],
            map_size="tiny",
            game_time_limit=game_time,
        )
        l = Launcher(
            executable_path="C:\\Program Files\\Microsoft Games\\Age of Empires II\\age2_x1.5.exe",
            settings=gs,
        )

        games = l.launch_games(instances=7, round_robin=False)
        games = [game for game in games if game.status != GameStatus.EXCEPTED]

        master_score_list = []
        times = []
        sets_run += 1

        test_wins = 0
        for game in games:
            if game.stats.winner == 1:
                test_wins += 1

        if test_wins >= 7:  # change to adjust threshold vs test ai
            for z in range(robustness):

                if nest_break:
                    break

                for e in range(len(group_list)):

                    gs = GameSettings(
                        civilisations=[civ] * 2,
                        names=["b", group_list[e]],
                        map_size="tiny",
                        game_time_limit=game_time,
                    )
                    l = Launcher(
                        executable_path="C:\\Program Files\\Microsoft Games\\Age of Empires II\\age2_x1.5.exe",
                        settings=gs,
                    )

                    games = l.launch_games(instances=7, round_robin=False)
                    games = [
                        game for game in games if game.status != GameStatus.EXCEPTED
                    ]

                    master_score_list = []
                    times = []
                    sets_run += 1

                    for game in games:
                        if game.stats.winner == 1:
                            real_wins += 1
                        master_score_list.append(game.stats.scores)
                        times.append(game.stats.elapsed_game_time)

                        if game.stats.elapsed_game_time < 100:
                            # crashed
                            break
                            nest_break = True

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
                        default_mutation_chance + fails / (1000 * anneal_amount), 0.2
                    )
                else:
                    mutation_chance = max(
                        default_mutation_chance - fails / (1000 * anneal_amount), 0.001
                    )

            else:
                best = b_score
                print(str(best) + " real wins: " + str(real_wins))
                winner = copy.deepcopy(b)
                fails = 0
                mutation_chance = default_mutation_chance

                ai_parent = copy.deepcopy(winner)
                write_ai(winner, "best")
                save_ai(winner, "best")

            if best == 7 * robustness * 3 or fails > 25:
                if best > 3.5 * robustness * 3:

                    self3 = copy.deepcopy(self2)
                    self2 = copy.deepcopy(self1)
                    self1 = copy.deepcopy(winner)

                    write_ai(self1, "self")
                    write_ai(self2, "self2")
                    write_ai(self3, "self3")

                    print("success, reset!")
                    backup()
                    max_real_wins = 0
                    generation = 1
                    # k = eloDict.keys()
                    # print(run_elo_once("best",eloDict,list(k)))
                else:
                    ai_parent = read_ai("best")
                    print("fail,    reset!")
                    max_real_wins = 0
                    generation = 1
                best = 0
                fails = 0
