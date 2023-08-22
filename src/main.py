import copy
import itertools
import random
import time
from dataclasses import dataclass
from enum import StrEnum, auto
from itertools import zip_longest
from typing import Any, Sequence

from elosports.elo import Elo

from src.functions import crossover
from src.game_launcher import Civilisation, GameSettings, Launcher, MapSize
from src.models import AI
from src.settings import CONFIG

AI_NAMES = ("parent", "b", "c", "d", "e", "f", "g", "h")


def setup_ai_files() -> None:
    for ai in AI_NAMES:
        with open(f"{ai}.ai", "w+", encoding="utf-8") as f:
            f.write("")


def set_annealing(
    fails: int, mutation_chance: float, anneal_amount: int = CONFIG.anneal_amount
) -> float:
    if fails % 2 == 0:
        return min(
            mutation_chance + fails / (1000 * anneal_amount),
            0.2,
        )
    return max(
        mutation_chance - fails / (1000 * anneal_amount),
        0.001,
    )


# changed so only real wins count
def extract_round_robin(
    p1: int, p2: int, game_time: int, max_game_time: int = CONFIG.game_time
) -> tuple[int, int]:
    if game_time > 0.9 * max_game_time:
        return 0, 0
    if p1 > p2:
        return 1, 0
    if p2 > p1:
        return 0, 1
    return 0, 0


def create_seeds(
    threshold: int,
    civ: str = CONFIG.civ,
    map_size: MapSize = MapSize.MEDIUM,
    **kwargs: Any,
) -> AI:
    while True:
        game_settings = GameSettings(
            civilisations=[civ] * 4,
            names=["parent", "parent"],
            map_size=map_size,
            **kwargs,
        )

        master_score_list = [[0, 0, 0, 0, 0, 0, 0, 0]]
        # print("reset")
        ai_parent = AI.generate()
        ai_parent.export("parent")

        launcher = Launcher(
            executable_path=CONFIG.executable_path,
            settings=game_settings,
        )
        master_score_list = [
            game.scores for game in launcher.launch_games(instances=1) if game.is_valid
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


# unused function
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
    base_mutation_chance: float = CONFIG.default_mutation_chance,
    anneal_amount: int = CONFIG.anneal_amount,
    fails_before_reset: int = CONFIG.fails_before_reset,
    ai_names: Sequence[str] = AI_NAMES,
    map_size: MapSize = MapSize.MEDIUM,
    game_time_limit: int = 5000,
    **kwargs: Any,
) -> None:
    if load:
        ai_parent = AI.from_file("best")
    else:
        ai_parent = create_seeds(threshold)

    second_place = copy.deepcopy(ai_parent)
    generation = 1
    fails = 0
    mutation_chance = base_mutation_chance
    game_settings = GameSettings(
        names=list(ai_names),
        civilisations=[Civilisation.default()] * len(ai_names),
        game_time_limit=game_time_limit,
        map_size=map_size,
        **kwargs,
    )
    launcher = Launcher(
        executable_path=CONFIG.executable_path,
        settings=game_settings,
    )

    while True:
        generation += 1
        ais = [ai_parent]
        for i, name in enumerate(ai_names):
            if i > 0:
                ais.append(
                    crossover(ai_parent, second_place, mutation_chance).mutate(
                        mutation_chance
                    )
                )
            ais[i].export(name)

        # reads score
        master_score_list = [
            game.scores for game in launcher.launch_games(instances=5) if game.is_valid
        ]
        score_list = [sum(x) for x in zip(*master_score_list)]

        if len(master_score_list) < 3 or set(score_list) == {0}:
            if generation == 1:
                generation -= 1
            continue

        sorted_score_list = sorted(score_list, reverse=True)

        # checks number of rounds with no improvement and sets annealing
        if score_list[0] == sorted_score_list[0]:
            fails += 1
            mutation_chance = set_annealing(fails, mutation_chance, anneal_amount)
        else:
            fails = 0
            mutation_chance = base_mutation_chance

        failed = False
        winner = None

        for i, score in enumerate(score_list):
            if score == sorted_score_list[0]:
                winner = copy.deepcopy(ais[i])
                if i == 0:
                    failed = True
                    second_place = copy.deepcopy(ais[0])
                print(f"{ai_names[i]} won by score: {score}")
                break
        if not winner:
            print("Failed!")
            break

        if not failed:
            for i, score in enumerate(score_list):
                if score == sorted_score_list[1]:
                    second_place = copy.deepcopy(ais[i])
                    break

        ai_parent = copy.deepcopy(winner)
        winner.export("best")
        winner.save_to_file("best")

        # restarts after a certain number of fails
        if fails > fails_before_reset:
            print("fail threshold exceeded, resetting...")
            winner.export(str(max(score_list)))
            winner.save_to_file(str(max(score_list)))
            fails = 0
            generation = 0
            ai_parent = AI.generate()  # ? create_seeds(threshold)


def run_ffa_four(
    threshold: int,
    load: bool,
    base_mutation_chance: float = CONFIG.default_mutation_chance,
    anneal_amount: int = CONFIG.anneal_amount,
    fails_before_reset: int = CONFIG.fails_before_reset,
    ai_names: Sequence[str] = AI_NAMES[:4],
    game_time_limit: int = 5000,
    map_size: MapSize = MapSize.TINY,
    **kwargs: Any,
) -> None:
    return run_ffa(
        threshold=threshold,
        load=load,
        base_mutation_chance=base_mutation_chance,
        anneal_amount=anneal_amount,
        fails_before_reset=fails_before_reset,
        ai_names=ai_names,
        game_time_limit=game_time_limit,
        map_size=map_size,
        **kwargs,
    )


# unused function
def run_vs(
    threshold: int,
    load: bool,
    ai_names: Sequence[str] = AI_NAMES[:2],
    base_mutation_chance: float = CONFIG.default_mutation_chance,
    anneal_amount: int = CONFIG.anneal_amount,
    instances: int = 7,
    **kwargs: Any,
) -> None:
    if load:
        ai_parent = AI.from_file("best")
    else:
        ai_parent = create_seeds(threshold)

    game_settings = GameSettings(
        civilisations=[Civilisation.default()] * len(ai_names),
        names=list(ai_names),
        **kwargs,
    )
    launcher = Launcher(
        executable_path=CONFIG.executable_path,
        settings=game_settings,
    )

    fails = 0
    winner = copy.deepcopy(ai_parent)
    mutation_chance = base_mutation_chance
    while True:
        ais = [ai_parent]
        ais.append(copy.deepcopy(ai_parent).mutate(mutation_chance))
        for i, name in enumerate(ai_names):
            ais[i].export(name)
        real_wins = sum(
            game.scores[1] > game.scores[0]
            for game in launcher.launch_games(instances)
            if game.is_valid
        )

        # checks number of rounds with no improvement and sets annealing
        if real_wins < 4:
            fails += 1
            mutation_chance = set_annealing(fails, mutation_chance, anneal_amount)
        else:
            print("new best")
            winner = copy.deepcopy(ais[1])
            fails = 0
            mutation_chance = base_mutation_chance

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
    base_mutation_chance: float = CONFIG.default_mutation_chance,
    anneal_amount: int = CONFIG.anneal_amount,
    instances: int = 7,
    **kwargs: Any,
) -> None:
    if load:
        ai_parent = AI.from_file("best")
    else:
        ai_parent = create_seeds(threshold)

    second_place = copy.deepcopy(ai_parent)

    game_settings = GameSettings(civilisations=civs, names=["b", trainer], **kwargs)
    launcher = Launcher(
        executable_path=CONFIG.executable_path,
        settings=game_settings,
    )

    mutation_chance = base_mutation_chance
    fails = 0
    generation = 0
    best = 0
    wins = 0

    while wins < 7 * robustness:
        generation += 1
        if generation == 1:
            b = copy.deepcopy(ai_parent)
        else:
            b = crossover(ai_parent, second_place, mutation_chance).mutate(
                mutation_chance
            )
        b.export("b")

        wins = 0
        nest_break = False
        for i in range(robustness):
            games = [game for game in launcher.launch_games(instances) if game.is_valid]
            wins += sum(game.winner == 1 for game in games)
            nest_break = any(game.elapsed_game_time < 100 for game in games)

            if wins == 0 or wins + (robustness - (i + 1)) * 7 < best or nest_break:
                break

        # checks number of rounds with no improvement and sets annealing
        if wins <= best:
            fails += 1
            mutation_chance = set_annealing(fails, mutation_chance, anneal_amount)
        else:
            best = wins
            print(f"b real wins: {wins}")
            winner = copy.deepcopy(b)
            fails = 0
            mutation_chance = base_mutation_chance

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
    base_mutation_chance: float = CONFIG.default_mutation_chance,
    anneal_amount: int = CONFIG.anneal_amount,
    instances: int = 7,
    **kwargs: Any,
) -> None:
    if load:
        ai_parent = AI.from_file("best")
    else:
        ai_parent = create_seeds(threshold)

    game_settings = GameSettings(
        civilisations=[Civilisation.default()] * 2,
        names=["b", "self"],
        **kwargs,
    )
    launcher = Launcher(
        executable_path=CONFIG.executable_path,
        settings=game_settings,
    )

    fails = 0
    generation = 0
    best = 0
    real_wins = 0
    max_real_wins = 0
    ai_parent.export("self")
    mutation_chance = base_mutation_chance
    winner = None

    while real_wins < 7 * robustness or infinite:
        generation += 1
        if generation == 1:
            b = copy.deepcopy(ai_parent)
        else:
            b = ai_parent.mutate(mutation_chance)
        b.export("b")

        real_wins = 0
        for i in range(robustness):
            real_wins += sum(
                1
                for game in launcher.launch_games(instances)
                if game.is_valid and game.winner == 1
            )
            # checks if possible to beat best, if not kills
            if real_wins + (robustness - i) * 7 < best:
                break

        # checks number of rounds with no improvement and sets annealing
        if real_wins <= best:
            fails += 1
            mutation_chance = set_annealing(fails, mutation_chance, anneal_amount)
        else:
            if real_wins > max_real_wins:
                max_real_wins = real_wins
            best = real_wins
            print(f"b real wins: {real_wins}")
            winner = copy.deepcopy(b)
            fails = 0
            mutation_chance = base_mutation_chance
            ai_parent = copy.deepcopy(winner)
            winner.export("best")
            winner.save_to_file("best")

        if fails <= 30 and real_wins != 7 * robustness:
            continue
        best = 0
        if max_real_wins <= 3.5 * robustness:
            continue
        # ! winner is defined in only one of the two previous if branches
        if not winner:
            print("Error, no winner")
            continue
        winner.export("self")
        print("success, reset!")
        backup()
        max_real_wins = 0
        generation = 1


def run_robin(
    iterations: int,
    ai_names: Sequence[str] = AI_NAMES[:4],
    default_mutation_chance: float = CONFIG.default_mutation_chance,
    anneal_amount: int = CONFIG.anneal_amount,
    **kwargs: Any,
) -> None:
    if iterations < 1:
        raise ValueError("At least 1 iteration required")
    ai_parent = AI.from_file("best")
    second_place = copy.deepcopy(ai_parent)

    game_settings = GameSettings(
        civilisations=[Civilisation.default()] * len(ai_names),
        names=list(ai_names),
        **kwargs,
    )
    launcher = Launcher(
        executable_path=CONFIG.executable_path,
        settings=game_settings,
    )

    winner = None
    fails = 0
    mutation_chance = default_mutation_chance
    while True:
        ais = {ai_names[0]: ai_parent}
        for name in ai_names[1:]:
            ais[name] = crossover(ai_parent, second_place, mutation_chance).mutate(
                mutation_chance
            )
        for name, ai in ais.items():
            ai.export(name)

        scores = {name: 0 for name in ai_names}
        score_list: list[int] = []

        skip = False
        fail = False
        for _ in range(iterations):
            # master_score_list = [[0,0],[0,0],[0,0],[0,0],[0,0],[0,0]]
            # [p,b],[p,c],[p,d],[b,c],[b,d][c,d]
            games = [
                game
                for game in launcher.launch_games(round_robin=True)
                if game.is_valid
            ]
            if len(games) < len(ai_names) * (len(ai_names) - 1) // 2:
                skip = True
                break

            for game in games:
                game_score = game.player_scores
                game_time = game.elapsed_game_time
                a, b = list(game_score.keys())
                p1, p2 = (game_score[name] for name in (a, b))
                x, y = extract_round_robin(p1, p2, game_time)
                scores[a] += x
                scores[b] += y

            score_list = sorted(list(scores.values()), reverse=True)

        if skip:
            continue

        # checks number of rounds with no improvement and sets annealing
        if scores[ai_names[0]] == score_list[0] or score_list[0] < 3 * iterations + 1:
            fails += 1
            mutation_chance = set_annealing(fails, mutation_chance, anneal_amount)
            fail = True
        else:
            fails = 0
            mutation_chance = default_mutation_chance

        if score_list[0] == 0 or scores[ai_names[0]] == score_list[0]:
            winner = copy.deepcopy(ai_parent)
            second_place = copy.deepcopy(ai_parent)
            print(f"parent won by score: {scores[ai_names[0]]}")
        else:
            for name, score in scores.items():
                if name == ai_names[0]:
                    continue
                if score == score_list[0]:
                    winner = copy.deepcopy(ais[name])
                    print(f"{name} won by score: {score}")
                    break

        if not fail:
            for name, score in scores.items():
                if score == score_list[1]:
                    second_place = copy.deepcopy(ais[name])
                    break

        if not winner:  # ! winner not necessarily defined
            print("Error, no winner")
            continue
        ai_parent = copy.deepcopy(winner)
        winner.export("best")
        winner.save_to_file("best")


class Outcome(StrEnum):
    WIN = auto()
    LOSS = auto()
    DRAW = auto()


@dataclass
class GameResult:
    outcome: Outcome
    score: int
    time: int
    opponent: str = ""

    def __str__(self) -> str:
        return f"{self.outcome},{self.time},{self.score}" + (
            f",{self.opponent}" if self.opponent else ""
        )


def benchmarker(
    ai1: str,
    ai2: str,
    rounds: int,
    civs: list[str],
    instances: int = 7,
    save_data: bool = True,
    **kwargs: Any,
) -> int:
    game_settings = GameSettings(civilisations=civs, names=[ai1, ai2], **kwargs)
    launcher = Launcher(
        executable_path=CONFIG.executable_path,
        settings=game_settings,
    )
    stats: dict[str, list[GameResult]] = {name: [] for name in (ai1, ai2)}
    for _ in range(int(rounds / instances)):
        local_wins = 0
        for game in launcher.launch_games(instances):
            if not game.is_valid:
                continue
            game_time = game.elapsed_game_time
            p1, p2 = game.scores
            if game.winner == 0 or game_time >= 0.9 * game_settings.game_time_limit:
                stats[ai1].append(GameResult(Outcome.DRAW, p1, game_time))
                stats[ai2].append(GameResult(Outcome.DRAW, p2, game_time))
            elif game.winner == 1:
                local_wins += 1
                stats[ai1].append(GameResult(Outcome.WIN, p1, game_time))
                stats[ai2].append(GameResult(Outcome.LOSS, p2, game_time))
            elif game.winner == 2:
                stats[ai1].append(GameResult(Outcome.LOSS, p1, game_time))
                stats[ai2].append(GameResult(Outcome.WIN, p2, game_time))
        if save_data:
            print(local_wins)

    ai1_wins = sum(1 for x in stats[ai1] if x.outcome == Outcome.WIN)
    if save_data:
        print(
            f"{ai1_wins}/"
            f"{sum(1 for x in stats[ai1] if x.outcome == Outcome.LOSS)}/"
            f"{sum(1 for x in stats[ai1] if x.outcome == Outcome.DRAW)}"
        )
    # print("Average gametime: " + str(time/(ai1_wins + ai2_wins + stalemates)))

    if save_data:
        with open(f"{ai1},{ai2}data.csv", "w", encoding="utf-8") as f:
            f.write("AI,result,game time,score\n")
            for name, results in stats.items():
                for result in results:
                    f.write(f"{name},{result}\n")

    return ai1_wins


def backup() -> None:
    print("backing up best")
    with open("AI/best.txt", encoding="utf-8") as f:
        a = f.read()

    letters = [str(i) for i in range(10)]
    filename = "".join(random.choice(letters) for _ in range(10))

    with open(f"AI/{filename}.txt", "w+", encoding="utf-8") as f:
        f.write(a)


def score_change(wins: int, robustness: int) -> float:
    if wins > 3.5 * robustness:
        return 3.5 * robustness + (wins - 3.5 * robustness) / 10
    return wins


def group_train(
    group_list: list[str],
    do_break: bool,
    robustness: int,
    base_mutation_chance: float = CONFIG.default_mutation_chance,
    anneal_amount: int = CONFIG.anneal_amount,
    game_time: int = 6000,
    instances: int = 7,
    **kwargs: Any,
) -> None:
    ai_parent = AI.from_file("best")
    second_place = AI.from_file("best")

    fails = 0
    generation = 0
    best = 0
    mutation_chance = base_mutation_chance

    while True:
        generation += 1
        if generation == 1:
            b = copy.deepcopy(ai_parent)
        else:
            b = crossover(ai_parent, second_place, mutation_chance).mutate(
                mutation_chance
            )
        b.export("b")

        string = ""
        b_score = 0
        score_dictionary = {x: 0 for x in group_list}
        start = time.time()

        for i, name in enumerate(group_list * robustness):
            game_settings = GameSettings(
                civilisations=[Civilisation.default()] * 2,
                names=["b", name],
                game_time_limit=game_time,
                **kwargs,
            )
            launcher = Launcher(
                executable_path=CONFIG.executable_path,
                settings=game_settings,
            )
            real_wins = sum(
                1
                for game in launcher.launch_games(instances)
                if game.is_valid and game.winner == 1
            )
            score_dictionary[name] += real_wins
            string += f"{name} : {real_wins} "
            if i == 0 and do_break and real_wins == 0:
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

        b_score = sum(
            score_change(wins, robustness) for wins in score_dictionary.values()
        )
        # print(str(b_score) + " " + str(time.time() - start))

        # checks number of rounds with no improvement and sets annealing
        if b_score <= best:
            fails += 1
            mutation_chance = set_annealing(fails, mutation_chance, anneal_amount)
        else:
            best = b_score
            print(f"{string}total score : {best} Time: {time.time() - start}")
            winner = copy.deepcopy(b)
            fails = 0
            mutation_chance = base_mutation_chance

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


def speed_train(
    trainer: str,
    base_mutation_chance: float = 0.01,
    anneal_amount: int = CONFIG.anneal_amount,
    game_time: float = 7200,
    instances: int = 10,
    **kwargs: Any,
) -> None:
    ai_parent = AI.from_file("best")
    second_place = copy.deepcopy(ai_parent)

    fails = 0
    generation = 0
    mutation_chance = base_mutation_chance
    default_score = -100000000000000000
    best = default_score
    real_wins = 0

    while True:
        generation += 1
        if generation == 1:
            b = copy.deepcopy(ai_parent)
        else:
            b = crossover(ai_parent, second_place, mutation_chance).mutate(
                mutation_chance
            )
        b.export("b")

        game_settings = GameSettings(
            civilisations=[Civilisation.default()] * 2,
            names=["b", trainer],
            game_time_limit=int(game_time),
            **kwargs,
        )
        launcher = Launcher(
            executable_path=CONFIG.executable_path,
            settings=game_settings,
        )

        games = [game for game in launcher.launch_games(instances) if game.is_valid]
        real_wins = sum(1 for game in games if game.winner == 1)
        if real_wins < 10:
            b_score = default_score
        else:
            b_score = -sum(game.elapsed_game_time for game in games)
        # print(real_wins)

        # checks number of rounds with no improvement and sets annealing
        if b_score <= best:
            fails += 1
            mutation_chance = set_annealing(fails, mutation_chance, anneal_amount)
        else:
            best = b_score
            print(f"New best: {best}")
            winner = copy.deepcopy(b)
            fails = 0
            mutation_chance = base_mutation_chance

            second_place = copy.deepcopy(ai_parent)
            ai_parent = copy.deepcopy(winner)
            winner.export("best")
            winner.save_to_file("best")

            if best > (-10 * game_time):
                game_time = (-1 * best / 10) / 0.75
                print(f"New time limit: {game_time}")

        if generation == 1 and best == default_score:
            generation = 0


def run_elo_once(
    ai: str,
    elo_dict: dict[str, float],
    group_list: list[str],
    instances: int = 7,
    game_time: int = 7200,
    **kwargs: Any,
) -> float:
    elo_league = Elo(k=20, g=1)
    for name in group_list:
        elo_league.add_player(name, rating=elo_dict[name])
    elo_league.add_player(ai, rating=1600)
    played = {ai}
    for x, name in enumerate(group_list):
        if name in played:
            continue
        played.add(name)
        game_settings = GameSettings(
            civilisations=[Civilisation.default()] * 2,
            names=[ai, name],
            game_time_limit=game_time,
            **kwargs,
        )
        launcher = Launcher(
            executable_path=CONFIG.executable_path,
            settings=game_settings,
        )

        games = [game for game in launcher.launch_games(instances) if game.is_valid]
        wins = 0
        for game in games:
            if game.winner == 1:
                wins += 1
                elo_league.game_over(winner=ai, loser=name, winner_home=False)
            elif game.winner == 2:
                elo_league.game_over(winner=name, loser=ai, winner_home=False)

        if x == 0 and wins == 0:
            # print("failed")
            return 0

    return elo_league.rating[ai]


def elo_train(
    elo_dict: dict[str, float] | None = None,
    base_mutation_chance: float = CONFIG.default_mutation_chance,
    anneal_amount: int = CONFIG.anneal_amount,
) -> None:
    elo_dict = elo_dict or CONFIG.elo_dict.copy()
    ai_parent = AI.from_file("best")
    second_place = AI.from_file("best")
    fails = 0
    generation = 0
    best = 0
    mutation_chance = base_mutation_chance
    while True:
        start = time.time()
        generation += 1
        if generation == 1:
            b = copy.deepcopy(ai_parent)
        else:
            b = crossover(ai_parent, second_place, mutation_chance).mutate(
                mutation_chance
            )

        b.export("b")
        b_score = run_elo_once("b", elo_dict.copy(), list(CONFIG.elo_dict.keys()))

        # checks number of rounds with no improvement and sets annealing
        if b_score <= best:
            # print(str(b_score))
            fails += 1
            mutation_chance = set_annealing(fails, mutation_chance, anneal_amount)
        else:
            best = b_score
            print("New Best: " + str(best))
            winner = copy.deepcopy(b)
            fails = 0
            mutation_chance = base_mutation_chance

            second_place = copy.deepcopy(ai_parent)
            ai_parent = copy.deepcopy(winner)
            winner.export("best")
            winner.save_to_file("best")

        if best == 0 and generation == 1:
            generation = 0

        print(time.time() - start)


def get_ai_data(
    group_list: list[str],
    instances: int = 7,
    game_time: int = 7200,
    **kwargs: Any,
) -> None:
    elo_league = Elo(k=20, g=1)
    for name in group_list:
        elo_league.add_player(name, rating=1600)

    stats: dict[str, list[GameResult]] = {name: [] for name in group_list}
    played: set[set[str]] = set()
    for name_1, name_2 in itertools.combinations(group_list, 2):
        print(name_1, name_2)
        if {name_1, name_2} in played:
            continue
        played.add({name_1, name_2})

        # REMOVE THIS later
        # civs = ["huns", "huns"]
        # if group_list[x] == 'best':
        #    civs = ['franks','byzantine']
        # elif group_list[y] == 'best':
        #    ['byzantine','franks']

        game_settings = GameSettings(
            civilisations=[Civilisation.default()] * 2,
            names=[name_1, name_2],
            game_time_limit=game_time,
            **kwargs,
        )
        launcher = Launcher(
            executable_path=CONFIG.executable_path,
            settings=game_settings,
        )

        for game in launcher.launch_games(instances):
            if not game.is_valid:
                continue
            if game.elapsed_game_time >= 0.9 * game_time or game.winner == 0:
                stats[name_1].append(
                    GameResult(
                        Outcome.DRAW,
                        game.player_scores[name_1],
                        game.elapsed_game_time,
                        name_2,
                    )
                )
                stats[name_2].append(
                    GameResult(
                        Outcome.DRAW,
                        game.player_scores[name_2],
                        game.elapsed_game_time,
                        name_1,
                    )
                )
                continue
            stats[name_1].append(
                GameResult(
                    Outcome.WIN if game.winner == 1 else Outcome.LOSS,
                    game.player_scores[name_1],
                    game.elapsed_game_time,
                    name_2,
                )
            )
            stats[name_2].append(
                GameResult(
                    Outcome.LOSS if game.winner == 1 else Outcome.WIN,
                    game.player_scores[name_2],
                    game.elapsed_game_time,
                    name_1,
                )
            )
            elo_league.game_over(
                winner=name_1 if game.winner == 1 else name_2,
                loser=name_2 if game.winner == 1 else name_1,
                winner_home=False,
            )

    print(elo_league.rating)
    print(stats)
    with open("data.csv", "w", encoding="utf-8") as f:
        f.write("AI,elo,result,game time,score,opponent\n")
        for name, results in stats.items():
            for result in results:
                f.write(f"{name},{elo_league.rating[name]},{result}\n")


def get_single_ai_data(
    civs: tuple[str],
    ai: str,
    group_list: list[str],
    dictionary: dict[str, int],
    runs: int,
    instances: int = 7,
    game_time: int = 7200,
) -> None:
    elo_league = Elo(k=20, g=1)
    for name in group_list:
        elo_league.add_player(name, rating=dictionary[name])
    elo_league.add_player(ai, rating=1600)

    stats: dict[str, list[GameResult]] = {ai: []}
    for name in group_list * runs:
        game_settings = GameSettings(
            civilisations=civs,
            names=[ai, name],
            game_time_limit=game_time,
        )
        launcher = Launcher(
            executable_path=CONFIG.executable_path,
            settings=game_settings,
        )

        for game in launcher.launch_games(instances):
            if not game.is_valid:
                continue
            if game.winner:
                elo_league.game_over(
                    winner=ai if game.winner == 1 else name,
                    loser=name if game.winner == 1 else ai,
                    winner_home=False,
                )
            stats[ai].append(
                GameResult(
                    Outcome.WIN
                    if game.winner == 1
                    else Outcome.DRAW
                    if game.winner == 0
                    else Outcome.LOSS,
                    game.player_scores[ai],
                    game.elapsed_game_time,
                    name,
                )
            )
    print(elo_league.rating)
    print(stats)
    with open("data.csv", "w", encoding="utf-8") as f:
        f.write("AI,elo,result,game time,score,opponent\n")
        for name, results in stats.items():
            for result in results:
                f.write(f"{name},{elo_league.rating[name]},{result}\n")


def benchmarker_slow(
    ai1: str,
    ai2: str,
    civs: list[str],
    rounds: int = 7 * 40,
    instances: int = 7,
    maps_size: MapSize = MapSize.TINY,
    save_data: bool = True,
    **kwargs: Any,
) -> int:
    return benchmarker(
        ai1=ai1,
        ai2=ai2,
        civs=civs,
        rounds=rounds,
        instances=instances,
        map_size=maps_size,
        save_data=save_data,
        speed=False,
        **kwargs,
    )


def run_vs_other_slow(
    threshold: int,
    load: bool,
    trainer: str,
    civs: list[str],
    instance_count: int,
    infinite: bool,
    default_mutation_chance: float = CONFIG.default_mutation_chance,
    anneal_amount: int = CONFIG.anneal_amount,
    game_time: int = 3600,
    **kwargs: Any,
) -> None:
    if load:
        ai_parent = AI.from_file(f"{CONFIG.network_drive}best")
    else:
        ai_parent = create_seeds(threshold)

    second_place = copy.deepcopy(ai_parent)

    game_settings = GameSettings(
        civilisations=civs,
        names=["b", trainer],
        game_time_limit=game_time,
        speed=False,
        **kwargs,
    )
    launcher = Launcher(
        executable_path=CONFIG.executable_path,
        settings=game_settings,
    )

    fails = 0
    generation = 0
    best = 0
    wins = 0
    mutation_chance = default_mutation_chance

    while wins < instance_count:
        ai_parent = AI.from_file(f"{CONFIG.network_drive}best")
        generation += 1
        if generation == 1:
            b = copy.deepcopy(ai_parent)
        else:
            b = crossover(ai_parent, second_place, mutation_chance).mutate(
                mutation_chance
            )
        b.export("b")

        games = [
            game for game in launcher.launch_games(instance_count) if game.is_valid
        ]
        wins = sum(
            game.scores[0] > game.scores[1]
            for game in games
            if game.elapsed_game_time < 0.9 * game_time
        )
        draws = sum(1 for game in games if game.elapsed_game_time >= 0.9 * game_time)

        # does nothing but keeping so I don't have to debug
        score = sum(game.scores[0] for game in games)
        bonus = 1 + sum(  # type: ignore
            10000000000 + 1000 / rate
            for game in games
            if game.scores[0] > game.scores[1]
            and (rate := game.elapsed_game_time / game_time) < 0.9
        )

        # score += bonus
        score = wins + draws / 100

        with open(f"{CONFIG.network_drive}score.txt", encoding="utf-8") as f:
            best_temp = float(f.read())

        if best_temp > best:
            best = best_temp
            fails = 0
        if score == 0:
            continue

        # checks number of rounds with no improvement and sets annealing
        if score < best:
            fails += 1
            mutation_chance = set_annealing(fails, mutation_chance, anneal_amount)
        else:
            best = score
            print(f"{best} real wins: {wins}")
            winner = copy.deepcopy(b)
            fails = 0
            mutation_chance = default_mutation_chance

            second_place = copy.deepcopy(ai_parent)
            ai_parent = copy.deepcopy(winner)
            winner.export("best")
            winner.save_to_file(f"{CONFIG.network_drive}best")

            with open(f"{CONFIG.network_drive}score.txt", "w", encoding="utf-8") as f:
                f.write(str(best))

        # if fails > 50:
        #    print("reset")
        #    best = 0
        #    generation = 0

        if wins < 1 and generation == 1:
            generation = 0
            print("fail")

    if infinite:
        speed_train(trainer)


def run_vs_self_slow(
    threshold: int,
    load: bool,
    instance_count: int,
    base_mutation_chance: float = CONFIG.default_mutation_chance,
    anneal_amount: int = CONFIG.anneal_amount,
    game_time: int = 3600,
    **kwargs: Any,
) -> None:
    if load:
        ai_parent = AI.from_file("best")
    else:
        ai_parent = create_seeds(threshold)

    second_place = copy.deepcopy(ai_parent)

    game_settings = GameSettings(
        civilisations=[Civilisation.default()] * 2,
        names=["b", "self"],
        game_time_limit=game_time,
        speed=False,
        **kwargs,
    )
    launcher = Launcher(
        executable_path=CONFIG.executable_path,
        settings=game_settings,
    )

    fails = 0
    generation = 0
    mutation_chance = base_mutation_chance
    ai_parent.export("self")

    while True:
        generation += 1
        b = crossover(ai_parent, second_place, mutation_chance).mutate(mutation_chance)
        b.export("b")
        games = [
            game for game in launcher.launch_games(instance_count) if game.is_valid
        ]

        wins = sum(1 for game in games if game.winner == 1)
        losses = sum(1 for game in games if game.winner == 2)
        draws = sum(1 for game in games if game.winner == 0)

        # checks number of rounds with no improvement and sets annealing
        if wins <= losses or wins < draws:
            fails += 1
            mutation_chance = set_annealing(fails, mutation_chance, anneal_amount)
        else:
            print(f"new best, scored {wins}")
            winner = copy.deepcopy(b)
            fails = 0
            mutation_chance = base_mutation_chance

            second_place = copy.deepcopy(ai_parent)
            ai_parent = copy.deepcopy(winner)
            winner.export("best")
            winner.export("self")
            winner.save_to_file("best")


def basic_benchmarker(
    ai1: str,
    ai2: str,
    rounds: int,
    civs: list[str],
    instances: int = 7,
    map_size: MapSize = MapSize.TINY,
    **kwargs: Any,
) -> int:
    return benchmarker(
        ai1=ai1,
        ai2=ai2,
        rounds=rounds,
        civs=civs,
        instances=instances,
        map_size=map_size,
        save_data=False,
        **kwargs,
    )


# get_ai_data(working_ais)
def run_vs_self_slow2(
    threshold: int,
    load: bool,
    robustness: int,
    infinite: bool,
    instances: int = 30,
    base_mutation_chance: float = CONFIG.default_mutation_chance,
    anneal_amount: int = CONFIG.anneal_amount,
    **kwargs: Any,
) -> None:
    if load:
        ai_parent = AI.from_file("best")
    else:
        ai_parent = create_seeds(threshold)

    game_settings = GameSettings(
        civilisations=[Civilisation.default()] * 2,
        names=["b", "self"],
        speed=False,
        **kwargs,
    )
    launcher = Launcher(
        executable_path=CONFIG.executable_path,
        settings=game_settings,
    )

    fails = 0
    generation = 0
    best = 0
    real_wins = 0
    max_real_wins = 0
    ai_parent.export("self")
    mutation_chance = base_mutation_chance
    winner = None

    while real_wins < 7 * robustness or infinite:
        generation += 1
        if generation == 1:
            b = copy.deepcopy(ai_parent)
        else:
            b = copy.deepcopy(ai_parent).mutate(mutation_chance)

        b.export("b")
        real_wins = 0

        for i in range(robustness):
            real_wins += sum(
                1
                for game in launcher.launch_games(instances)
                if game.is_valid and game.winner == 1
            )
            if (
                real_wins + (robustness - i) * 7 < best
            ):  # checks if possible to beat best, if not kills
                break

        # checks number of rounds with no improvement and sets annealing
        if real_wins <= best:
            fails += 1
            mutation_chance = set_annealing(fails, mutation_chance, anneal_amount)
        else:
            if real_wins > max_real_wins:
                max_real_wins = real_wins
            best = real_wins
            print(f"{best} real wins: {real_wins}")
            winner = copy.deepcopy(b)
            fails = 0
            mutation_chance = base_mutation_chance

            ai_parent = copy.deepcopy(winner)
            winner.export("best")
            winner.save_to_file("best")

        # ! winner may not be defined
        if not winner:
            continue
        if real_wins == 7 * robustness or fails > 30:
            if max_real_wins > 3.5 * robustness:
                winner.export("self")
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
    instances: int = 7,
    base_mutation_chance: float = CONFIG.default_mutation_chance,
    anneal_amount: int = CONFIG.anneal_amount,
    **kwargs: Any,
) -> None:
    if load:
        ai_parent = AI.from_file("best")
    else:
        ai_parent = create_seeds(threshold)

    # print("loading ais, please edit if unwanted")
    # self1 = copy.deepcopy(ai_parent)
    # self2 = read_ai("4076768862")
    # self3 = read_ai("7004446841")

    group_list = ["self", "self2", "self3"]
    ais = {name: copy.deepcopy(ai_parent) for name in group_list}
    for name, ai in ais.items():
        ai.export(name)

    mutation_chance = base_mutation_chance
    sets_to_be_run = len(group_list) * robustness
    fails = 0
    generation = 0
    best = 0
    real_wins = 0
    winner = None

    while infinite or real_wins < instances * robustness:
        generation += 1
        if generation == 1:
            b = copy.deepcopy(ai_parent)
        else:
            b = copy.deepcopy(ai_parent).mutate(mutation_chance)

        b.export("b")
        real_wins = 0
        game_settings = GameSettings(
            civilisations=[Civilisation.default()] * 2, names=["b", "king"], **kwargs
        )
        launcher = Launcher(
            executable_path=CONFIG.executable_path,
            settings=game_settings,
        )

        test_wins = sum(
            1
            for game in launcher.launch_games(instances)
            if game.is_valid and game.winner == 1
        )

        if test_wins < 6:
            continue

        sets_run = 1
        for i, name in enumerate(group_list * robustness):
            game_settings = GameSettings(
                civilisations=[Civilisation.default()] * 2,
                names=["b", name],
                **kwargs,
            )
            launcher = Launcher(
                executable_path=CONFIG.executable_path,
                settings=game_settings,
            )
            if (i + 1) % len(group_list) == 0:
                sets_run += 1
            real_wins += sum(
                1
                for game in launcher.launch_games(instances)
                if game.is_valid and game.winner == 1
            )
            if best > real_wins + (sets_to_be_run - sets_run) * instances:
                # print("impossible")
                break

        # checks number of rounds with no improvement and sets annealing
        if real_wins <= best:
            fails += 1
            mutation_chance = set_annealing(fails, mutation_chance, anneal_amount)
        else:
            best = real_wins
            print(f"{best} real wins: {real_wins}")
            winner = copy.deepcopy(b)
            fails = 0
            mutation_chance = base_mutation_chance

            ai_parent = copy.deepcopy(winner)
            winner.export("best")
            winner.save_to_file("best")

        if best == instances * robustness * len(group_list) or fails > 25:
            if best > instances / 2 * robustness * len(group_list):
                # ! winner may not be defined
                if not winner:
                    continue
                new_ais = [winner] + [ais[name] for name in group_list[:-1]]
                for name, new_ai in reversed(list(zip(group_list, new_ais))):
                    ais[name] = copy.deepcopy(new_ai)
                for name, ai in ais.items():
                    ai.export(name)
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
