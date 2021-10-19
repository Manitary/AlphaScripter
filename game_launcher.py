import os
import subprocess
import time
from ctypes import windll

import msgpackrpc
import psutil

all_civilisations = {
    "britons": 1,
    "franks": 2,
    "goths": 3,
    "teutons": 4,
    "japanese": 5,
    "chinese": 6,
    "byzantine": 7,
    "persians": 8,
    "saracens": 9,
    "turks": 10,
    "vikings": 11,
    "mongols": 12,
    "celts": 13,
    "spanish": 14,
    "aztec": 15,
    "mayan": 16,
    "huns": 17,
    "koreans": 18,
    "random": 19
}

maps = {
    "arabia": 9,
    "archipelago": 10,
    "baltic": 11,
    "black_forest": 12,
    "coastal": 13,
    "continental": 14,
    "crater_cake": 15,
    "fortress": 16,
    "gold_rush": 17,
    "highland": 18,
    "islands": 19,
    "mediterranean": 20,
    "migration": 21,
    "rivers": 22,
    "team_islands": 23,
    "random_map": 24,
    "random": 24,
    "scandinavia": 25,
    "mongolia": 26,
    "yucatan": 27,
    "salt_marsh": 28,
    "arena": 29,
    "oasis": 31,
    "ghost_lake": 32,
    "nomad": 33,
    "iberia": 34,
    "britain": 35,
    "mideast": 36,
    "texas": 37,
    "italy": 38,
    "central_america": 39,
    "france": 40,
    "norse_lands": 41,
    "sea_of_japan": 42,
    "byzantium": 43,
    "random_land_map": 45,
    "random_real_world_map": 47,
    "blind_random": 48,
    "conventional_random_map": 49
}

map_sizes = {'tiny': 0, 'small': 1, 'medium': 2, 'normal': 3, 'large': 4, 'giant': 5}
difficulties = {'hardest': 0, 'hard': 1, 'moderate': 2, 'standard': 3, 'easiest': 4}
game_types = {'random_map': 0, 'regicide': 1, 'death_match': 2, 'scenario': 3, 'king_of_the_hill': 4, 'wonder_race': 6,
              'turbo_random_map': 8}
starting_resources = {'standard': 0, 'low': 1, 'medium': 2, 'high': 3}
reveal_map_types = {'normal': 1, 'explored': 2, 'all_visible': 3}
starting_ages = {'standard': 0, 'dark': 2, 'feudal': 3, 'castle': 4, 'imperial': 5, 'post-imperial': 6}
victory_types = {'standard': 0, 'conquest': 1, 'relics': 4, 'time_limit': 7, 'score': 8}


class GameSettings:
    def __init__(self, civilisations: list, map_id='arabia', map_size='medium', difficulty='hard',
                 game_type='random_map', resources='low', reveal_map='normal', starting_age='dark',
                 victory_type='conquest'):

        self.civilisations = self.correct_civilizations(civilisations, default='huns')
        self.map_id = self.correct_setting(map_id, maps, 'arabia', 'map name/type')
        self.map_size = self.correct_setting(map_size, map_sizes, 'medium', 'map size')
        self.difficulty = self.correct_setting(difficulty, difficulties, 'hard', 'difficulty')
        self.game_type = self.correct_setting(game_type, game_types, 'random_map', 'game type')
        self.resources = self.correct_setting(resources, starting_resources, 'standard', 'starting resources')
        self.reveal_map = self.correct_setting(reveal_map, reveal_map_types, 'normal', 'reveal map')
        self.starting_age = self.correct_setting(starting_age, starting_ages, 'standard', 'starting age')
        self.victory_type = self.correct_setting(victory_type, victory_types, 'standard', 'victory type (WIP)')

    @property
    def map(self):
        return self.map_id

    @staticmethod
    def correct_setting(value, possible_values: dict, default, setting_name):
        if value in possible_values.values():
            return value
        elif value.lower() in possible_values.keys():
            return possible_values[value.lower()]
        print(f"Warning! Value {value} not valid for setting {setting_name}. Defaulting to {default}.")
        return possible_values[default]

    @staticmethod
    def correct_civilizations(civilizations: list, default='huns'):
        if not civilizations:
            return []
        result = []
        for civ in civilizations:
            if civ in all_civilisations.values():
                result.append(civ)
            elif civ in all_civilisations.keys():
                result.append(all_civilisations[civ])
            else:
                print(f"Civ {civ} is not valid. Defaulting to {default}.")
                result.append(default)
        return result

    @property
    def civs(self):
        return self.civilisations


class Launcher:
    def __init__(self,
                 executable_path: str = "C:\\Program Files\\Microsoft Games\\age of empires ii\\Age2_x1\\age2_x1.exe"):
        self.executable_path = executable_path
        self.directory, self.aoc_name = os.path.split(executable_path)
        self.dll_path = (os.path.join(self.directory, 'aoc-auto-game.dll')).encode('UTF-8')
        self.names = None
        self.games: list[tuple[msgpackrpc.Client, subprocess.Popen]] = []

    @property
    def number_of_games(self):
        if not self.games:
            return 0
        return len(self.games)

    def launch_game(self, names: list[str], game_settings: GameSettings, real_time_limit: int = 0,
                    game_time_limit: int = 0, instances: int = 1):
        self.quit_all_games(quit_program=True)
        self.names = names
        if names is None or len(names) < 2 or len(names) > 8:
            raise Exception(f"List of names {names} not valid! Expected list of a least 2 and at most 8.")

        if game_settings.civs is not None and len(game_settings.civs) != len(names):
            raise Exception(
                f"The length of the civs {game_settings.civs} does not match the length of the names {names}")

        for i in range(instances):
            port = 64720 + i
            process = self._launch(multiple=instances > 1, port=port)
            rpc_client = msgpackrpc.Client(msgpackrpc.Address("127.0.0.1", port))
            self.games.append((rpc_client, process))

        current_time = 0
        self._start_all_games(names, game_settings)
        scores = [[0] * len(names)] * len(self.games)
        running_games = self.get_running_games()
        while running_games:
            time.sleep(1)
            current_time += 1

            for running_game_index in running_games:
                scores[running_game_index] = self.get_scores(running_game_index)

            if game_time_limit > 0:
                for i in range(len(self.games)):
                    game_time = self.call_safe(i, 'GetGameTime')
                    if game_time is None:
                        print(f"Warning! Wasn't able to get the in game time of game {i}. If the in-game time"
                              f"is over the limit, we can't check now.")
                    elif game_time > game_time_limit:
                        # print(f"Time's up for game {i}!")
                        self.quit_game(i)

            # print(f"Time {current_time} , Scores {scores}")
            if 0 < real_time_limit < current_time:
                print("Real time's up!")
                break
            running_games = self.get_running_games()

        self.quit_all_games()
        # print(scores)
        return scores

    def get_running_games(self) -> list:
        result = []
        for index, game in enumerate(self.games):
            rpc, proc = game
            if rpc is None or proc is None:
                continue
            if self.call_safe(index, 'GetGameInProgress'):
                result.append(index)
        return result

    def _launch(self, multiple: bool = False, port: int = 64720) -> subprocess.Popen:
        # kill any previous aoc processes
        # aoc_procs = [proc for proc in psutil.process_iter() if proc.name() == self.aoc_name]
        # for aoc_proc in aoc_procs: aoc_proc.kill()

        if multiple:
            aoc_proc = subprocess.Popen(self.executable_path + " -multipleinstances -autogameport " + str(port))
        else:
            aoc_proc = subprocess.Popen(self.executable_path)

        # to launch the rpc server with another port, it could be launched like this:
        # aoc_proc = subprocess.Popen(aoc_path + " -autogameport 64721")

        # write dll path into aoc memory
        aoc_handle = windll.kernel32.OpenProcess(0x1FFFFF, False, aoc_proc.pid)  # PROCESS_ALL_ACCESS
        remote_memory = windll.kernel32.VirtualAllocEx(aoc_handle, 0, 260, 0x3000, 0x40)
        windll.kernel32.WriteProcessMemory(aoc_handle, remote_memory, self.dll_path, len(self.dll_path), 0)

        # load the dll from the remote process
        # noinspection PyProtectedMember
        load_library = windll.kernel32.GetProcAddress(windll.kernel32._handle, b'LoadLibraryA')
        remote_thread = windll.kernel32.CreateRemoteThread(aoc_handle, 0, 0, load_library, remote_memory, 0, 0)
        windll.kernel32.WaitForSingleObject(remote_thread, 0xFFFFFFFF)
        windll.kernel32.CloseHandle(remote_thread)

        # clean up
        windll.kernel32.VirtualFreeEx(aoc_handle, remote_memory, 0, 0x00008000)
        windll.kernel32.CloseHandle(aoc_handle)
        return aoc_proc

    def _start_all_games(self, names, game_settings: GameSettings, minimize: bool = False):
        for i in range(self.number_of_games):
            self._setup_game(i, names, game_settings)
        for i in range(len(self.games)):
            self._start_game(i, minimize)

    def _setup_game(self, game_index: int, names, settings: GameSettings):
        self.call_safe(game_index, 'ResetGameSettings')
        self.call_safe(game_index, 'SetGameMapType', settings.map)
        self.call_safe(game_index, 'SetGameDifficulty', settings.difficulty)  # Set to hard
        self.call_safe(game_index, 'SetGameRevealMap', settings.reveal_map)  # Set to standard exploration
        self.call_safe(game_index, 'SetGameMapSize', settings.map_size)  # Set to medium map size
        self.call_safe(game_index, 'SetRunUnfocused', True)
        self.call_safe(game_index, 'SetRunFullSpeed', True)
        # self.call_safe('SetUseInGameResolution', False, game_index=game_index)
        for index, name in enumerate(names):
            self.call_safe(game_index, 'SetPlayerComputer', index + 1, name)
            self.call_safe(game_index, 'SetPlayerCivilization', index + 1, settings.civilisations[index])

    def _start_game(self, game_index, minimize: bool = False):
        self.call_safe(game_index, 'StartGame')
        if minimize:
            self.call_safe(game_index, 'SetWindowMinimized', True)

    def get_scores(self, game_index: int) -> list[int]:
        """
        Get the scores of a certain game that is currently running.
        :param game_index: The index of the game to get the scores from.
        :return: A list of scores, where every index represents the score of a player.
        """
        if game_index < 0 or game_index >= len(self.games):
            print(f"Cannot return scores of game {game_index} because this is not a valid index."
                  f"The index must be greater than zero and less than the length of the games list ({len(self.games)})")

        rpc_client, process = self.games[game_index]
        if process is None or rpc_client is None or not self.call_safe(game_index, 'GetGameInProgress'):
            print("Cannot return scores when there's no game running! Returning zeroed scores.")
            return [0] * len(self.names)

        scores = []
        for i in range(len(self.names)):
            score = self.call_safe(game_index, "GetPlayerScore", i + i)
            if score:
                scores.append(score)
            else:
                scores.append(0)
                print(f"Couldn't get score for player {i + 1}. Setting this score to 0")

        return scores

    def call_safe(self, game_index: int, method: str, param1=None, param2=None, kill_on_except: bool = True, ):
        """
        Call a method in the autogame in a safe way, where exceptions are handled.
        :param game_index: The index of the game
        :param method: The name of the method to call.
        :param param1: The first parameter for the method.
        :param param2: The second parameter for the method.
        :param kill_on_except: Whether to kill the process if calling fails.
        :return: The return of the method call, if available. None if exception occurs or game isn't running.
        """
        if not self.games:
            return None

        rpc_client, process = self.games[game_index]

        if rpc_client is None or process is None:
            print(f"Couldn't call method {method} on game {game_index} because either game process or rpc client "
                  f"doesn't exist.")
            if kill_on_except:
                self.kill_game(game_index)
            return None

        try:
            if param1 is not None and param2 is not None:
                return rpc_client.call(method, param1, param2)
            elif param1 is not None:
                return rpc_client.call(method, param1)
            else:
                return rpc_client.call(method)

        except msgpackrpc.error.TimeoutError:
            print("Request to game timed out.")
            if kill_on_except:
                self.kill_game(game_index)
            return None

    def quit_all_games(self, quit_program: bool = True, force_kill_on_fail: bool = True):
        for i in self.get_running_games():
            self.quit_game(game_index=i, quit_program=quit_program, force_kill_on_fail=force_kill_on_fail)

    def quit_game(self, game_index: int = 0, quit_program: bool = True, force_kill_on_fail: bool = True):
        """
        Quit the game to the main menu.
        :param game_index: The index of the game that will be quit.
        :param force_kill_on_fail: Whether to force stop the process when quitting to main menu fails.
        :param quit_program: If True, closes the window and quits the program. Else just stays in the main menu.
        """

        rpc_client, process = self.games[game_index]

        if rpc_client is not None:
            try:
                rpc_client.call("QuitGame")
                time.sleep(1.0)
                if quit_program:
                    rpc_client.close()
                    if process is not None:
                        process.kill()
                    self.games[game_index] = (None, None)

            except msgpackrpc.error.TimeoutError:
                print("Quitting to main menu failed.")
                if force_kill_on_fail:
                    self.kill_game(game_index=game_index)

    def kill_game(self, game_index: int):
        """
        Kill the game forcefully. The process will be killed as well.
        """
        rpc_client, process = self.games[game_index]

        if rpc_client is not None:
            try:
                rpc_client.close()
            except msgpackrpc.error.TimeoutError:
                print("Game not responding. Closing game failed.")

        if process is not None:
            try:  # Try killing the process normally
                process.kill()
            except BaseException:  # If that fails for whatever reason, terminate the process.
                p: psutil.Process = psutil.Process(process.pid)
                p.terminate()

        self.games[game_index] = (None, None)


# n = ['Barbarian'] * 4
# c = ['huns'] * 4
# gs = GameSettings(c)
# launcher = Launcher()
# launcher.launch_game(n, gs, real_time_limit=10)
