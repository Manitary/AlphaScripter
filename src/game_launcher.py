import asyncio
import copy
import datetime
import enum
import itertools
import os
import subprocess
import time
from ctypes import windll
from dataclasses import dataclass, field
from typing import Self, Sequence

import msgpackrpc  # type: ignore

from src.settings import CONFIG


DEFAULT_GAME_PATH = (
    "C:\\Program Files\\Microsoft Games\\age of empires ii\\Age2_x1\\age2_x1.exe"
)


class GameSetting(enum.Enum):
    @classmethod
    def _missing_(cls, value: object) -> Self:
        if isinstance(value, str):
            for member in cls:
                if member.name == value:
                    return member
        if isinstance(value, int):
            for member in cls:
                if member.value == value:
                    return member
        default = cls.default()
        print(
            f"{cls.__name__} {value} is not valid. Defaulting to {default.name.lower()}."
        )
        return default

    @classmethod
    def default(cls) -> Self:
        raise NotImplementedError()


class Civilisation(GameSetting):
    BRITONS = 1
    FRANKS = 2
    GOTHS = 3
    TEUTONS = 4
    JAPANESE = 5
    CHINESE = 6
    BYZANTINE = 7
    PERSIANS = 8
    SARACENS = 9
    TURKS = 10
    VIKINGS = 11
    MONGOLS = 12
    CELTS = 13
    SPANISH = 14
    AZTEC = 15
    MAYAN = 16
    HUNS = 17
    KOREANS = 18
    RANDOM = 19

    @classmethod
    def default(cls) -> Self:
        return cls.HUNS


class Map(GameSetting):
    ARABIA = 21
    ARCHIPELAGO = 10
    BALTIC = 11
    BLACK_FOREST = 12
    COASTAL = 13
    CONTINENTAL = 14
    CRATER_CAKE = 15
    FORTRESS = 16
    GOLD_RUSH = 17
    HIGHLAND = 18
    ISLANDS = 19
    MEDITERRANEAN = 20
    MIGRATION = 21
    RIVERS = 22
    TEAM_ISLANDS = 23
    RANDOM_MAP = 24
    RANDOM = 24
    SCANDINAVIA = 25
    MONGOLIA = 26
    YUCATAN = 27
    SALT_MARSH = 28
    ARENA = 29
    OASIS = 31
    GHOST_LAKE = 32
    NOMAD = 33
    IBERIA = 34
    BRITAIN = 35
    MIDEAST = 36
    TEXAS = 37
    ITALY = 38
    CENTRAL_AMERICA = 39
    FRANCE = 40
    NORSE_LANDS = 41
    SEA_OF_JAPAN = 42
    BYZANTIUM = 43
    RANDOM_LAND_MAP = 45
    RANDOM_REAL_WORLD_MAP = 47
    BLIND_RANDOM = 48
    CONVENTIONAL_RANDOM_MAP = 49

    @classmethod
    def default(cls) -> Self:
        return cls.ARABIA


class MapSize(GameSetting):
    TINY = 0
    SMALL = 1
    MEDIUM = 2
    NORMAL = 3
    LARGE = 4
    GIANT = 5

    @classmethod
    def default(cls) -> Self:
        return cls.TINY


class Difficulty(GameSetting):
    HARDEST = 0
    HARD = 1
    MODERATE = 2
    STANDARD = 3
    EASIEST = 4

    @classmethod
    def default(cls) -> Self:
        return cls.HARD


class GameType(GameSetting):
    RANDOM_MAP = 0
    REGICIDE = 1
    DEATH_MATCH = 2
    SCENARIO = 3
    KING_OF_THE_HILL = 4
    WONDER_RACE = 6
    TURBO_RANDOM_MAP = 8

    @classmethod
    def default(cls) -> Self:
        return cls.RANDOM_MAP


class StartingResources(GameSetting):
    STANDARD = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3

    @classmethod
    def default(cls) -> Self:
        return cls.LOW


class RevealMap(GameSetting):
    NORMAL = 1
    EXPLORED = 2
    ALL_VISIBLE = 3

    @classmethod
    def default(cls) -> Self:
        return cls.NORMAL


class StartingAge(GameSetting):
    STANDARD = 0
    DARK = 2
    FEUDAL = 3
    CASTLE = 4
    IMPERIAL = 5
    POST_IMPERIAL = 6  # ! Check if the string _has_ to be "post-imperial"

    @classmethod
    def default(cls) -> Self:
        return cls.DARK


class VictoryType(GameSetting):
    STANDARD = 0
    CONQUEST = 1
    RELICS = 4
    TIME_LIMIT = 7
    SCORE = 8

    @classmethod
    def default(cls) -> Self:
        return cls.CONQUEST


class GameStatus(enum.Enum):
    NONE = "No status"  # If we read this there is probably something wrong.
    INIT = "Initialized"  # This means no process or RPC client has been launched.
    LAUNCHED = "Game process launched"  # The process exists, but not RPC client has been launched and connected.
    CONNECTED = "RPC Client connected"  # The process and RPC client exist, but the game is still in the main menu.
    SETUP = "Game settings have been applied"  # The game has applied settings.
    RUNNING = "Game is running"  # The game is just running.
    ENDED = (
        "Game is no longer running"  # The game has ended and we are in the main menu.
    )
    QUIT = "Game has been quit and process killed"
    EXCEPTED = "This game has encountered an error and is therefore terminated"


class GameSettings:
    def __init__(
        self,
        names: list[str],
        civilisations: Sequence[str | int | Civilisation] | None,
        map_id: str | int | Map = Map.default(),
        map_size: str | int | MapSize = MapSize.default(),
        difficulty: str | int | Difficulty = Difficulty.default(),
        game_type: str | int | GameType = GameType.default(),
        resources: str | int | StartingResources = StartingResources.default(),
        reveal_map: str | int | RevealMap = RevealMap.default(),
        starting_age: str | int | StartingAge = StartingAge.default(),
        victory_type: str | int | VictoryType = VictoryType.default(),
        game_time_limit: int = CONFIG.game_time,
        speed: bool = True,
    ) -> None:
        civilisations = list(civilisations) if civilisations else []
        civilisations = self._correct_civilizations(
            num_players=len(names), civilizations=civilisations, default="huns"
        )
        self.players = {
            i: Player(name, civilisation)
            for i, (name, civilisation) in enumerate(zip(names, civilisations), 1)
        }
        self.map = Map(map_id)
        self.map_size = MapSize(map_size)
        self.difficulty = Difficulty(difficulty)
        self.game_type = GameType(game_type)
        self.resources = StartingResources(resources)
        self.reveal_map = RevealMap(reveal_map)
        self.starting_age = StartingAge(starting_age)
        self.victory_type = VictoryType(victory_type)
        self.victory_value = 0  # TODO: Make this work.
        self.game_time_limit = max(0, game_time_limit)
        self.speed = speed

    @property
    def map_id(self) -> int:
        return self.map.value

    @property
    def names(self) -> list[str]:
        return [p.name for p in self.players.values()]

    @property
    def civs(self) -> list[Civilisation]:
        return [p.civ for p in self.players.values()]

    def _correct_civilizations(
        self,
        num_players: int,
        civilizations: list[str | int | Civilisation],
        default: str = Civilisation.default().name.lower(),
    ) -> list[Civilisation]:
        civs = [Civilisation(civ) for civ in civilizations]
        if len(civs) < num_players:
            print(
                "The number of civilisations provided is less than the number of names."
                "For every player that does not have a civilisation provided for it, "
                f"it will default to {default}."
            )
            civs.extend([Civilisation.default()] * (num_players - len(civs)))
        return civs

    def make_round_robin(self) -> list[Self]:
        games_settings: list[Self] = []
        for player_1, player_2 in itertools.combinations(self.players.values(), r=2):
            game_settings = copy.deepcopy(self)
            game_settings.players = {1: player_1, 2: player_2}
            games_settings.append(game_settings)
        return games_settings


@dataclass(frozen=True)
class Player:
    name: str
    civ: Civilisation


@dataclass
class PlayerStats:
    player: Player
    index: int
    _alive: bool = field(default=True, init=False)
    _score: int = field(default=0, init=False)

    def update(self, score: int, alive: bool) -> None:
        self._score = score
        self._alive = alive

    @property
    def name(self) -> str:
        return self.player.name

    @property
    def score(self) -> int:
        return self._score

    @property
    def alive(self) -> bool:
        return self._alive

    def __str__(self) -> str:
        return (
            f"Player {self.index} '{self.player.name}' ({self.player.civ})\n"
            f"\t\tScore: {self.score}\n"
            f"\t\tAlive: {self.alive}\n"
        )


class GameStats:
    __slots__ = (
        "player_stats",
        "elapsed_game_time",
        "winner",
    )

    def __init__(self, players: dict[int, Player] | None = None) -> None:
        players = players or {}
        self.player_stats = {
            index: PlayerStats(player, index) for index, player in players.items()
        }
        self.elapsed_game_time = 0
        self.winner = 0

    def update_player(self, index: int, score: int, alive: bool) -> None:
        self.player_stats[index].update(score=score, alive=alive)

    def __bool__(self) -> bool:
        if self.player_stats:
            return True
        return False

    @property
    def scores(self) -> list[int]:
        return [player.score for player in self.player_stats.values()]

    @property
    def player_scores(self) -> dict[str, int]:
        return {player.name: player.score for player in self.player_stats.values()}

    @property
    def stats(self) -> dict[int, PlayerStats]:
        return self.player_stats

    @property
    def alives(self) -> list[bool]:
        return [player.alive for player in self.player_stats.values()]

    def __str__(self) -> str:
        return f"Elapsed Game Time: {self.elapsed_game_time}\n\n" + "".join(
            str(player) for player in self.player_stats.values()
        )


class Game:
    __slots__ = (
        "name",
        "_settings",
        "status",
        "_process",
        "_rpc",
        "_port",
        "_stats",
        "debug",
    )

    def __init__(self, name: str = "GameWithoutName", debug: bool = False) -> None:
        self.name = name
        self.status = GameStatus.INIT
        self.debug = debug
        self._port = 0
        self._process: subprocess.Popen[bytes] | None = None
        self._rpc: msgpackrpc.Client | None = None
        self._settings: GameSettings | None = None
        self._stats = GameStats()

    async def launch_process(
        self, executable_path: str, dll_path: bytes, multiple: bool, port: int
    ) -> subprocess.Popen[bytes]:
        """
        Launch an instance of the game (i.e. open a new process)

        :param executable_path: The path to the executable of the game.
        :param dll_path: The path to the DLL needed to communicate with the process.
        :param multiple: Whether multiple processes are going to be launched.
        :param port: The port on which to start this process communication channels (using the DLL)
        :return: The process that was started of type ``subprocess.Popen``
        """

        if self.status != GameStatus.INIT:
            print(
                f"Warning! This game does not have the status {GameStatus.INIT}, "
                "so it's probably not the right time to call this launch_process method!"
            )

        launch_options = (
            f"{executable_path}"
            f"{' -multipleinstances' if multiple else ''}"
            f" -autogameport {port}"
        )
        aoc_proc = subprocess.Popen(launch_options)

        # write dll path into aoc memory
        aoc_handle = windll.kernel32.OpenProcess(
            0x1FFFFF, False, aoc_proc.pid
        )  # PROCESS_ALL_ACCESS
        remote_memory = windll.kernel32.VirtualAllocEx(aoc_handle, 0, 260, 0x3000, 0x40)
        windll.kernel32.WriteProcessMemory(
            aoc_handle, remote_memory, dll_path, len(dll_path), 0
        )

        # load the dll from the remote process
        # noinspection PyProtectedMember
        load_library = windll.kernel32.GetProcAddress(
            windll.kernel32._handle, b"LoadLibraryA"
        )
        remote_thread = windll.kernel32.CreateRemoteThread(
            aoc_handle, 0, 0, load_library, remote_memory, 0, 0
        )
        windll.kernel32.WaitForSingleObject(remote_thread, 0xFFFFFFFF)
        windll.kernel32.CloseHandle(remote_thread)

        # clean up
        windll.kernel32.VirtualFreeEx(aoc_handle, remote_memory, 0, 0x00008000)
        windll.kernel32.CloseHandle(aoc_handle)

        self._port = port
        self._process = aoc_proc
        self.status = GameStatus.LAUNCHED
        return aoc_proc

    def setup_rpc_client(self, custom_port: int = 0) -> msgpackrpc.Client:
        """
        Create a RPC client to manage this game remotely.

        :param custom_port: A custom port to connect to.
        If not specified (or set to 0 or lower), this will use the
        port assigned automatically when creating the game process.

        :return: A ``msgpackrpc.Client`` instance that is connected to the game process.
        """

        if self.debug and self.status != GameStatus.LAUNCHED:
            print(
                f"Warning! Game {self.name} does have the status {GameStatus.LAUNCHED}. "
                "Setting up the RPC client is probably not a good idea!"
            )

        setup_port = custom_port or self._port
        self._rpc = msgpackrpc.Client(msgpackrpc.Address("127.0.0.1", setup_port))
        self.status = GameStatus.CONNECTED
        return self._rpc

    async def apply_settings(self, settings: GameSettings) -> None:
        """
        Apply game settings to this game.

        :param settings: The GameSettings settings to apply.
        """

        if self.debug and self.status != GameStatus.CONNECTED:
            print(
                f"Warning! Status of game {self.name} is not {GameStatus.CONNECTED}."
                "It might not be a good time to setup the game..."
            )

        try:
            self._settings = settings
            self._rpc.call_async("ResetGameSettings")  # type: ignore
            self._rpc.call_async("SetGameMapType", settings.map_id)  # type: ignore
            self._rpc.call_async("SetGameDifficulty", settings.difficulty)  # type: ignore
            self._rpc.call_async("SetGameRevealMap", settings.reveal_map)  # type: ignore
            self._rpc.call_async("SetGameMapSize", settings.map_size)  # type: ignore
            self._rpc.call_async(  # type: ignore
                "SetGameVictoryType", settings.victory_type, settings.victory_value
            )
            self._rpc.call_async("SetRunUnfocused", True)  # type: ignore
            self._rpc.call_async("SetRunFullSpeed", settings.speed)  # type: ignore
            # self.call_safe('SetUseInGameResolution', False, game_index=game_index)
            for i, player in settings.players.items():
                self._rpc.call_async("SetPlayerComputer", i, player.name)  # type: ignore
                self._rpc.call_async("SetPlayerCivilization", i, player.civ)  # type: ignore
                self._rpc.call_async("SetPlayerTeam", i, 0)  # type: ignore
        except BaseException as e:
            message = (
                f"Warning! Game Settings could not be applied to game {self.name}"
                f"because of exception {e}"
                "\nThe rpc client will be closed and the game process will be terminated."
            )
            self.handle_except(e, message)
        self._stats = GameStats(settings.players)
        self.status = GameStatus.SETUP

    async def start_game(self) -> None:
        """
        Start the game.
        """

        if self.debug and self.status != GameStatus.SETUP:
            print(
                f"Warning! Game {self.name} has not the status {GameStatus.SETUP}. "
                "It might not be a good idea to try and start this game..."
            )
        try:
            self._rpc.call(  # type: ignore
                "StartGame"
            )  # self._rpc.call_async('StartGame') did not work.
            if self.debug:
                print(f"Game {self.name} launched.")
        except BaseException as e:
            message = (
                f"Could not start game {self.name} because it has excepted with exception {e}. "
                "The game will be ended and the process killed."
            )
            self.handle_except(e, message)
        self.status = GameStatus.RUNNING

    async def update_player(
        self, game_time: int, index: int, player: PlayerStats
    ) -> None:
        if self._settings is None:
            return
        try:
            if game_time >= 1.5 * self._settings.game_time_limit:
                score = 0
            else:
                score: int | None = self._rpc.call("GetPlayerScore", index)  # type: ignore
            alive: bool | None = self._rpc.call("GetPlayerAlive", index)  # type: ignore
            if score is not None and alive is not None:
                assert isinstance(score, int)
                assert isinstance(alive, bool)
                player.update(score=score, alive=alive)
            else:
                player.update(score=0, alive=False)
                if self.debug:
                    print(
                        f"Couldn't get score or alive status for player {player.name}. "
                        "Setting this score to 0"
                    )

        except BaseException as e:
            message = (
                f"Score and/or alive status for player {player.name} in game {self.name} "
                f"couldn't be retrieved because of {e}. "
                "Setting this players' score to 0."
            )
            player.update(score=0, alive=False)
            self.handle_except(e, message)

    async def update(self) -> None:
        """
        Check whether the game is still running and extract the stats if it isn't.
        """
        if self._settings is None:
            return
        try:
            game_time = 0
            self._stats.winner = 0
            try:
                game_time: int = self._rpc.call("GetGameTime")  # type: ignore
                self._stats.elapsed_game_time = game_time
            except BaseException as e:
                message = (
                    f"Couldn't get game time for game {self.name} because of {e}. "
                    "Closing the RPC client and killing process."
                )
                self.handle_except(e, message)

            is_running: bool = self._rpc.call("GetGameInProgress")  # type: ignore
            over_time = 0 < self._settings.game_time_limit < game_time
            if is_running and not over_time:
                return
            temp: list[int] = self._rpc.call("GetWinningPlayers")  # type: ignore
            if len(temp) > 1:
                self._stats.winner = 0
            else:
                self._stats.winner = temp[0]
            # print(self._rpc.call('GetWinningPlayer'))
            for index, player in self._stats.player_stats.items():
                await self.update_player(
                    game_time=game_time, index=index, player=player
                )
            self.status = GameStatus.ENDED
            self.kill()

        except BaseException as e:
            message = f"Warning! Game {self.name} could not be updated because of exception {e}."
            self.handle_except(e, message)

    def handle_except(self, exception: BaseException, extra_message: str = "") -> None:
        """
        Kill the process and disconnect the RPC client; print debug statements if relevant.

        :param exception: The exception that occurred.
        :param extra_message: An optional extra message to print as well.
        """

        if self.debug:
            if extra_message:
                print(extra_message)
            print(
                f"Exception {exception} occurred on {self.name}. "
                "Killing the process and closing the rpc client."
            )
        self.kill()  # Important to do before setting the Excepted state!
        self.status = GameStatus.EXCEPTED

    def kill(self) -> None:
        """
        Kill the process and disconnect the RPC client.
        """

        if self._rpc is not None:
            self._rpc.close()
            self._rpc = None
        if self._process is not None:
            self._process.kill()
            self._process = None
        self.status = GameStatus.QUIT

    def print_stats(self) -> None:
        if self._settings is None:
            print("Stats not available - settings not applied")
            return
        string = (
            f"Game {self.name} Stats\n"
            " ------------------------------------------- \n"
            f"Status: {self.status}\n"
            f"Played @ {self._settings.map.name.lower()} [{self._settings.map_size.name.lower()}]\n"
            f"{str(self._stats)}"
            "\n\n"
        )
        print(string)

    @property
    def is_valid(self) -> bool:
        return self.status != GameStatus.EXCEPTED and bool(self._stats)

    @property
    def scores(self) -> list[int]:
        return self._stats.scores

    @property
    def stats(self) -> dict[int, PlayerStats]:
        return self._stats.stats

    @property
    def player_scores(self) -> dict[str, int]:
        return self._stats.player_scores

    @property
    def elapsed_game_time(self) -> int:
        return self._stats.elapsed_game_time

    @property
    def winner(self) -> int:
        return self._stats.winner

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name


class Launcher:
    def __init__(
        self,
        settings: GameSettings,
        executable_path: str = DEFAULT_GAME_PATH,
        debug: bool = False,
    ) -> None:
        self.executable_path = executable_path
        self.directory, self.aoc_name = os.path.split(executable_path)
        self.dll_path = (os.path.join(self.directory, "aoc-auto-game.dll")).encode(
            "UTF-8"
        )
        self.games: list[Game] = []
        self.base_port = 64720
        self.settings = settings
        self.debug = debug

    @property
    def names(self) -> list[str]:
        return self.settings.names

    @property
    def number_of_games(self) -> int:
        return len(self.games)

    @property
    def running_games(self) -> list[Game]:
        return [game for game in self.games if game.status == GameStatus.RUNNING]

    def launch_games(self, instances: int = 1, round_robin: bool = False) -> list[Game]:
        all_settings = (
            [self.settings] * instances
            if not round_robin
            else self.settings.make_round_robin()
        )
        if not round_robin:
            self.games = [Game(f"Game#{i + 1}", self.debug) for i in range(instances)]
        else:
            self.games = [
                Game(f"Game#{i + 1}", self.debug) for i in range(len(all_settings))
            ]

        asyncio.run(self._launch_games(), debug=self.debug)
        time.sleep(5.0)  # Make sure all games are launched.
        self._setup_rpc_clients()
        asyncio.run(
            self._apply_games_settings(settings=all_settings), debug=self.debug
        )  # Apply settings to the games
        time.sleep(2)
        asyncio.run(self._start_games())

        any_game_running = True
        while any_game_running:
            asyncio.run(self.update_games())
            if self.debug:
                print(f"({datetime.datetime.now()}) : {self.running_games}")
            time.sleep(1)
            any_game_running = len(self.running_games) > 0

        return self.games

    async def _launch_games(self) -> list[asyncio.Task[subprocess.Popen[bytes]]]:
        tasks = [
            asyncio.create_task(
                coro=game.launch_process(
                    executable_path=self.executable_path,
                    dll_path=self.dll_path,
                    multiple=self.number_of_games > 1,
                    port=self.base_port + index,
                ),
                name=f"GameLaunch{index}",
            )
            for index, game in enumerate(self.games)
        ]
        return await asyncio.gather(*tasks)

    def _setup_rpc_clients(self) -> None:
        for game in self.games:
            game.setup_rpc_client()

    async def _apply_games_settings(
        self, settings: list[GameSettings]
    ) -> list[asyncio.Task[None]]:
        tasks = [
            asyncio.create_task(
                coro=game.apply_settings(settings[index]),
                name=f"ApplyGameSettings-{game.name}",
            )
            for index, game in enumerate(self.games)
        ]
        return await asyncio.gather(*tasks)

    async def _start_games(self) -> list[asyncio.Task[None]]:
        tasks = [
            asyncio.create_task(
                coro=game.start_game(), name=f"StartingGame-{game.name}"
            )
            for game in self.games
        ]
        return await asyncio.gather(*tasks)

    async def update_games(self) -> None:
        tasks = [
            asyncio.create_task(coro=game.update(), name=f"UpdateGame-{game.name}")
            for game in self.running_games
        ]
        await asyncio.gather(*tasks)
