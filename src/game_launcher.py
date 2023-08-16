from abc import ABC, abstractmethod
import asyncio
import copy
import datetime
import enum
import os
import subprocess
import time
from ctypes import windll
from dataclasses import dataclass
from typing import Self, Sequence

import msgpackrpc

DEFAULT_GAME_PATH = (
    "C:\\Program Files\\Microsoft Games\\age of empires ii\\Age2_x1\\age2_x1.exe"
)


class Setting(enum.Enum, ABC):
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
    @abstractmethod
    def default(cls) -> Self:
        ...


class Civilisation(Setting):
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


class Map(Setting):
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


class MapSize(Setting):
    TINY = 0
    SMALL = 1
    MEDIUM = 2
    NORMAL = 3
    LARGE = 4
    GIANT = 5

    @classmethod
    def default(cls) -> Self:
        return cls.MEDIUM


class Difficulty(Setting):
    HARDEST = 0
    HARD = 1
    MODERATE = 2
    STANDARD = 3
    EASIEST = 4

    @classmethod
    def default(cls) -> Self:
        return cls.HARD


class GameType(Setting):
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


class StartingResources(Setting):
    STANDARD = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3

    @classmethod
    def default(cls) -> Self:
        return cls.LOW


class RevealMap(Setting):
    NORMAL = 1
    EXPLORED = 2
    ALL_VISIBLE = 3

    @classmethod
    def default(cls) -> Self:
        return cls.NORMAL


class StartingAge(Setting):
    STANDARD = 0
    DARK = 2
    FEUDAL = 3
    CASTLE = 4
    IMPERIAL = 5
    POST_IMPERIAL = 6  # ! Check if the string _has_ to be "post-imperial"

    @classmethod
    def default(cls) -> Self:
        return cls.DARK


class VictoryType(Setting):
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
        game_time_limit: int = 0,
        speed: bool = True,
    ) -> None:
        names = names or []
        civilisations = list(civilisations) if civilisations else []
        self.names = names
        self.civilisations = self._correct_civilizations(civilisations, default="huns")
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
    def civs(self) -> list[Civilisation]:
        return self.civilisations

    def _correct_civilizations(
        self,
        civilizations: list[str | int | Civilisation],
        default: str = Civilisation.default().name.lower(),
    ) -> list[Civilisation]:
        civs = [Civilisation(civ) for civ in civilizations]
        if len(civilizations) < len(self.names):
            print(
                "The number of civilisations provided is less than the number of names."
                "For every player that does not have a civilisation provided for it, "
                f"it will default to {default}."
            )
            civs.extend(
                [Civilisation.default()] * (len(self.names) - len(civilizations))
            )
        return civs

    def clone(self) -> Self:
        return copy.deepcopy(self)


@dataclass
class PlayerStats:
    index: int
    name: str
    alive: bool = True
    score: int = 0

    def update(self, score: int, alive: bool) -> None:
        self.score = score
        self.alive = alive


class GameStats:
    elapsed_game_time: int
    player_stats: dict[int, PlayerStats]
    _settings: GameSettings
    winner: int = 0

    def __init__(self, settings: GameSettings) -> None:
        self.elapsed_game_time = 0
        self._settings = settings
        self.player_stats = {}
        for index, name in enumerate(settings.names):
            self.player_stats[index] = PlayerStats(index=index, name=name)

    def update_player(self, index: int, score: int, alive: bool) -> None:
        self.player_stats[index].update(score=score, alive=alive)

    @property
    def scores(self) -> list[int]:
        return [self.player_stats[i].score for i, _ in enumerate(self._settings.names)]

    @property
    def alives(self) -> list[bool]:
        return [self.player_stats[i].alive for i, _ in enumerate(self._settings.names)]

    def __str__(self) -> str:
        string = (
            f"Played @ {self._settings.map.name}"
            f"[{self._settings.map_size.name}] \n"
            f"Elapsed Game Time: {self.elapsed_game_time} \n\n"
        )
        for i, ps in self.player_stats.items():
            string += (
                f"Player {i} '{ps.name}' ({self._settings.civs[i].name}) \n"
                f"\t\t Score: {ps.score} \n"
                f"\t\t Alive: {ps.alive} \n"
            )
        return string


class Game:
    name: str = "GameWithoutName"
    _settings: GameSettings | None = None
    status: GameStatus = GameStatus.NONE
    _process: subprocess.Popen[bytes] | None = None
    _rpc: msgpackrpc.Client | None = None
    _port: int = 0
    stats: GameStats | None = None

    def __init__(self, name: str, debug: bool = False) -> None:
        self.name = name
        self.status = GameStatus.INIT
        self.debug = debug

    async def launch_process(
        self, executable_path: str, dll_path: bytes, multiple: bool, port: int
    ) -> subprocess.Popen[bytes]:
        """
        Launch an instance of the game (i.e. open a new process)

        :param executable_path: The path to the executable of the game.
        :param dll_path: The path to the DLL needed to communicate with the process.
        :param multiple: Whether multiple processes are going to be launched. Used as a required launch parameter.
        :param port: The port on which to start this process communication channels (using the DLL)
        :return: The process that was started of type ``subprocess.Popen``
        """

        if self.status != GameStatus.INIT:
            print(
                f"Warning! This game does not have the status {GameStatus.INIT}, "
                "so it's probably not the right time to call this launch_process method!"
            )

        launch_options = f"{executable_path}{' -multipleinstances' if multiple else ''} -autogameport {port}"
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

    async def apply_settings(self, settings: GameSettings):
        """
        Apply game settings to this game.

        :param settings: The GameSettings settings to apply.
        """

        if self.debug and self.status != GameStatus.CONNECTED:
            print(
                f"Warning! Status of game {self.name} is not {GameStatus.CONNECTED}."
                "It might not be a good time to setup the game..."
            )

        self._settings = settings
        try:
            self._rpc.call_async("ResetGameSettings")  # type: ignore
            self._rpc.call_async("SetGameMapType", settings.map_id)  # type: ignore
            self._rpc.call_async(  # type: ignore
                "SetGameDifficulty", settings.difficulty
            )  # Set to hard
            self._rpc.call_async(  # type: ignore
                "SetGameRevealMap", settings.reveal_map
            )  # Set to standard exploration
            self._rpc.call_async(  # type: ignore
                "SetGameMapSize", settings.map_size
            )  # Set to medium map size
            self._rpc.call_async(  # type: ignore
                "SetGameVictoryType", settings.victory_type, settings.victory_value
            )
            self._rpc.call_async("SetRunUnfocused", True)  # type: ignore
            self._rpc.call_async("SetRunFullSpeed", settings.speed)  # type: ignore
            # self.call_safe('SetUseInGameResolution', False, game_index=game_index)
            for index, name in enumerate(settings.names):
                self._rpc.call_async("SetPlayerComputer", index + 1, name)  # type: ignore
                self._rpc.call_async(  # type: ignore
                    "SetPlayerCivilization", index + 1, settings.civilisations[index]
                )
                self._rpc.call_async("SetPlayerTeam", index + 1, 0)  # type: ignore
        except BaseException as e:
            message = (
                f"Warning! Game Settings could not be applied to game {self.name}"
                f"because of exception {e}"
                "\nThe rpc client will be closed and the game process will be terminated."
            )
            self.handle_except(e, message)
        self.stats = GameStats(settings=settings)
        self.status = GameStatus.SETUP

    async def start_game(self):
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

    async def update(self):
        """
        Check whether the game is still running and extract the stats if it isn't.
        """
        try:
            is_running: bool = self._rpc.call("GetGameInProgress")  # type: ignore
            game_time = 0
            assert isinstance(self.stats, GameStats)
            self.stats.winner = 0
            try:
                game_time: int = self._rpc.call("GetGameTime")  # type: ignore
                self.stats.elapsed_game_time = game_time
            except BaseException as e:
                message = (
                    f"Couldn't get game time for game {self.name} because of {e}. "
                    "Closing the RPC client and killing process."
                )
                self.handle_except(e, message)

            assert isinstance(self._settings, GameSettings)
            over_time = 0 < self._settings.game_time_limit < game_time

            if not is_running or over_time:
                temp: list[int] = self._rpc.call("GetWinningPlayers")  # type: ignore
                if len(temp) > 1:
                    self.stats.winner = 0
                else:
                    self.stats.winner = temp[0]
                # print(self._rpc.call('GetWinningPlayer'))
                for index, name in enumerate(self._settings.names):
                    try:
                        if game_time >= 1.5 * self._settings.game_time_limit:
                            score = 0
                        else:
                            score: int | None = self._rpc.call(  # type: ignore
                                "GetPlayerScore", index + 1
                            )
                        alive: bool | None = self._rpc.call("GetPlayerAlive", index + 1)  # type: ignore
                        # print(self.stats.winner)

                        if score is not None and alive is not None:
                            assert isinstance(score, int)
                            assert isinstance(alive, bool)
                            self.stats.update_player(
                                index=index, score=score, alive=alive
                            )
                        else:
                            self.stats.update_player(index=index, score=0, alive=False)
                            if self.debug:
                                print(
                                    f"Couldn't get score or alive status for player {name}. "
                                    "Setting this score to 0"
                                )
                    except BaseException as e:
                        message = (
                            f"Score and/or alive status for player {name} in game {self.name} "
                            f"couldn't be retrieved because of {e}. "
                            "Setting this players' score to 0."
                        )
                        self.stats.update_player(index=index, score=0, alive=False)
                        self.handle_except(e, message)
                self.status = GameStatus.ENDED
                self.kill()

        except BaseException as e:
            message = f"Warning! Game {self.name} could not be updated because of exception {e}."
            self.handle_except(e, message)

    def handle_except(self, exception: BaseException, extra_message: str = "") -> None:
        """
        Handle exceptions that occur during a running game by killing the process and disconnecting the RPC client.
        Also, print debug statements if relevant.

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
        string = (
            f"Game {self.name} Stats "
            "\n ------------------------------------------- \n"
            f"Status: {self.status} \n"
            f"{str(self.stats)}"
        )
        print(string)
        print("\n\n")

    @property
    def statistics(self) -> GameStats | None:
        return self.stats

    @property
    def scores(self) -> list[int] | None:
        if not self.stats:
            return None
        return self.stats.scores

    @property
    def overtime(self) -> bool | None:
        if self._settings and self.stats:
            return 0 < self._settings.game_time_limit < self.stats.elapsed_game_time
        return None

    @property
    def winner(self) -> int | None:
        if not self.stats:
            return None
        return self.stats.winner

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
            else self._apply_round_robin(self.settings)
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

    async def _launch_games(self) -> list[subprocess.Popen[bytes]]:
        tasks: list[asyncio.Task[subprocess.Popen[bytes]]] = []
        multiple = self.number_of_games > 1
        for index, game in enumerate(self.games):
            task = asyncio.create_task(
                coro=game.launch_process(
                    executable_path=self.executable_path,
                    dll_path=self.dll_path,
                    multiple=multiple,
                    port=self.base_port + index,
                ),
                name=f"GameLaunch{index}",
            )
            tasks.append(task)
        return await asyncio.gather(*tasks)

    def _setup_rpc_clients(self) -> None:
        for game in self.games:
            game.setup_rpc_client()

    async def _apply_games_settings(self, settings: list[GameSettings]):
        tasks: list[asyncio.Task[None]] = []
        for index, game in enumerate(self.games):
            task = asyncio.create_task(
                coro=game.apply_settings(settings[index]),
                name=f"ApplyGameSettings-{game.name}",
            )
            tasks.append(task)
        return await asyncio.gather(*tasks)

    @staticmethod
    def _apply_round_robin(original_settings: GameSettings) -> list[GameSettings]:
        settings: list[GameSettings] = []
        # Suppose the number of names = 5, then we want to go from 0 to (incl.) 3
        # And for index2, we want to go from 1 to (incl.) 4
        for index1 in range(len(original_settings.names) - 1):
            for index2 in range(index1 + 1, len(original_settings.names)):
                game_settings = original_settings.clone()
                game_settings.names = [
                    original_settings.names[index1],
                    original_settings.names[index2],
                ]
                game_settings.civilisations = [
                    original_settings.civilisations[index1],
                    original_settings.civilisations[index2],
                ]
                settings.append(game_settings)
        return settings

    async def _start_games(self):
        tasks: list[asyncio.Task[None]] = []
        for game in self.games:
            task = asyncio.create_task(
                coro=game.start_game(), name=f"StartingGame-{game.name}"
            )
            tasks.append(task)
        return await asyncio.gather(*tasks)

    async def update_games(self):
        tasks: list[asyncio.Task[None]] = []
        for game in self.running_games:
            task = asyncio.create_task(
                coro=game.update(), name=f"UpdateGame-{game.name}"
            )
            tasks.append(task)
        await asyncio.gather(*tasks)
