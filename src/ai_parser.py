from __future__ import annotations

import os
import pickle
import re
from dataclasses import dataclass, field
from typing import Sequence


class AoError(Exception):
    ...


# ========== Utility Functions ============


def dir_exists(path: str, raise_exception: bool = False) -> bool:
    if os.path.isdir(path):
        return True
    if raise_exception:
        raise AoError(f"Directory {path} does not exist!")
    return False


def file_exists(path: str, raise_exception: bool = False) -> bool:
    if os.path.isfile(path):
        return True
    if raise_exception:
        raise AoError(f"File {path} does not exist!")
    return False


def write_to_file(
    path: str, contents: str, create_if_not_exists: bool = False, append: bool = False
) -> None:
    if not create_if_not_exists and not os.path.isfile(path):
        print(f"File writing failed: {path} does not exist!")
    mode = "a" if append else "w+"
    with open(path, mode, encoding="utf-8") as file:
        file.write(contents)


def read_file_raw(path: str) -> str:
    file_exists(path, raise_exception=True)
    with open(path, encoding="utf-8") as file:
        return file.read()


def str_to_int(string: str, allow_negative: bool = True) -> tuple[bool, int | str]:
    if string.isdigit():
        return True, int(string)
    if allow_negative and string.startswith("-"):
        return True, -int(string[1:])
    # print(f"String '{string}' cannot be converted to int, returning the string instead.")
    return False, string


def inside_outer_parentheses(string: str) -> str:
    first_parenthesis_index = string.find("(") + 1
    last_parenthesis_index = string.rfind(")")
    return string[first_parenthesis_index:last_parenthesis_index]


# =========================================

operators = {"and": "&", "or": "|", "not": "#", "nand": "$", "nor": "@"}


@dataclass
class FactBase:
    name: str  # For a simple, this the name of the fact. For a Complex, this is an operator.
    _depth: int = field(init=False, default=0)

    @property
    def is_simple(self) -> bool:
        return self.name not in operators

    @property
    def is_complex(self) -> bool:
        return self.name in operators

    @property
    def depth(self) -> int:
        return self._depth

    @depth.setter
    def depth(self, value: int) -> None:
        self._depth = value

    def set_depth(self, value: int) -> None:
        self._depth = value


@dataclass
class Simple(FactBase):
    params: list[str]
    length: int
    relevant_length: int

    def __init__(self, params: str | Sequence[str], *args: str) -> None:
        if isinstance(params, str):
            super().__init__(name=params)
            self.params = self.__get_params(args) if args else []
        else:
            if len(params) > 5:
                raise AoError("A Simple only take a name and a maximum of 4 arguments.")
            super().__init__(name=params[0])
            self.params = self.__get_params(list(params)[1:])
        if self.params:
            self.length = self.relevant_length = len(params)
        self._depth = 0

    @staticmethod
    def __get_params(params: Sequence[str]) -> list[str]:
        if not params:
            return []
        # If the params passed through are a list or tuple, we just use that one.
        if isinstance(params, (list, tuple, set)):
            if len(params) > 4:
                raise AoError("Cannot create Simple with more than 4 parameters!")
            return [str(x) for x in params]
        raise AoError("Arguments must be a single list, or multiple int and string")

    def __str__(self) -> str:
        string = f"({self.name}"
        if self.params:
            string += " " + " ".join(self.params[: self.relevant_length])
        string += ")"
        return string

    def __len__(self) -> int:
        return self.length


@dataclass
class Complex(FactBase):
    param1: FactBase
    param2: FactBase | None = None

    def __init__(
        self, name: str, param1: FactBase, param2: FactBase | None = None
    ) -> None:
        super().__init__(name=name)
        self.param1 = param1
        self.param2 = param2
        self.set_depth(0)  # Set the depths recursively

    def __str__(self) -> str:
        name_tabs = "\t" * (1 if len(self.name) > 2 else 2)
        result = f"({self.name}{name_tabs}{self.param1}"
        if self.param2:
            tabs = "\t" * (
                self.param2._depth * 2 + 1
            )  # The plus 1 is because every rule has every line indented 1 tab
            result += f"\n{tabs}{self.param2}"
        return result + ")"

    def set_depth(self, value: int) -> None:
        self._depth = value
        self.param1.set_depth(value + 1)
        if self.param2:
            self.param2.set_depth(value + 1)


@dataclass
class Rule:
    facts: list[FactBase]
    primary_facts: list[FactBase]
    actions: list[Simple]
    actions_length: int
    comment_unused: bool  # If True, 'unused' actions and facts are commented out when printing

    def __init__(
        self,
        facts: list[FactBase],
        actions: list[Simple],
        facts_length: int = 0,
        actions_length: int = 0,
        comment_unused: bool = False,
    ) -> None:
        if not facts:
            raise AoError("Cannot create a rule without any facts!")
        if not actions:
            raise AoError("Cannot create a rule without any actions!")
        self.facts = facts
        self.primary_facts = self.get_facts(depth=0)
        self.actions = actions

        if facts_length < 0:
            print("Warning! Facts length cannot be negative. Defaulting to 0.")
            facts_length = 0
        if not 0 <= actions_length <= 4:
            print("Warning! Action length must be between 0 and 4. Defaulting to 0.")
            actions_length = 0

        self.facts_length = facts_length or len(self.facts)
        self.actions_length = actions_length or len(self.actions)
        self.comment_unused = comment_unused

    def get_facts(self, depth: int = 0) -> list[FactBase]:
        if not depth:
            return self.facts[:]
        if depth == 1:
            return self.primary_facts[:]
        return [fact for fact in self.facts if fact.depth == depth]

    def __str__(self) -> str:
        string = "(defrule\n"
        if self.comment_unused:
            for index, fact in enumerate(self.facts):
                string += (
                    f"{index}:{';' if index >= self.facts_length else ''}\t{fact}\n"
                )
            string += "=>\n"
            for index, action in enumerate(self.actions):
                string += (
                    f"{index}:{';' if index >= self.actions_length else ''}\t{action}\n"
                )
        else:
            for fact in self.primary_facts[: self.facts_length]:
                string += f"\t{fact}\n"
            string += "=>\n"
            for action in self.actions[: self.actions_length]:
                string += f"\t{action}\n"
        string += ")"
        return string

    def __repr__(self) -> str:
        return str(self)


class AIParser:
    @staticmethod
    def read_single(
        path: str = "C:\\Program Files\\Microsoft Games\\age of empires ii\\Ai\\Alpha.per",
        raise_exception: bool = True,
    ) -> AI | None:
        """
        Read a single .per file and return the AI.

        :param path: The path to the .per file.
        :param raise_exception: Whether to raise Exceptions if for example a file cannot be found.
        :return: An instance of the AI class if found, else None.
        """

        if os.path.isfile(path):
            if path.endswith(".per"):
                return AI(path=path)
            if path.endswith(".pickle"):
                with open(path, "rb") as f:
                    ai = pickle.load(f)
                return ai
            if raise_exception:
                raise AoError(f"Cannot read from {path}. The file is not a .per file.")
        elif raise_exception:
            raise AoError(f"Cannot read from {path}. No file found at that path.")
        return None

    @staticmethod
    def read_multiple(
        path: str, names: set[str] | None = None, as_dict: bool = True
    ) -> dict[str, AI] | list[AI]:
        """
        Read multiple AI .per files in a directory and return a list containing the found AI's.

        :param path: The path to the directory containing the .per files.
        :param names: An optional set of names that acts as a filter when reading AIs.
        :param as_dict: Return the result as a dictionary. If False, return a list.
        :return: A dict (keys are AI names) or list containing all the AIs.
        """
        names = names or set()
        if not os.path.isdir(path):
            raise AoError(f"The path {path} does not exist or is not a directory.")

        result: dict[str, AI] = {}
        for file in os.listdir(path):
            if file.endswith(".per"):
                name = file.removesuffix(".per")
            elif file.endswith(".pickle"):
                name = file.removesuffix(".pickle")
            else:
                continue
            if names and name not in names:
                continue
            ai = AIParser.read_single(os.path.join(path, file), raise_exception=False)
            if not ai:
                continue
            result[name] = ai

        if len(result) < len(names):
            print(f"We did not find all the AIs:\nquery={names}, found={len(result)}")

        if as_dict:
            return result
        return list(result.values())

    @staticmethod
    def write_single(ai: AI, target_directory: str, pickled: bool = True) -> bool:
        if not dir_exists(target_directory, raise_exception=True):
            print(f"Warning! Writing AI {ai} failed.")
            return False
        if pickled:
            with open(os.path.join(target_directory, ai.name + ".pickle"), "wb") as f:
                pickle.dump(ai, f)
            return True
        ai.write()
        return True


class AI:
    def __init__(self, path: str) -> None:
        self.path = self.__repair_path(path)  # The path to the AI .per file
        # The directory in which this AI's .per file is located & The name of this AI.
        self.parent_directory, self.name = os.path.split(path)
        self.name = self.name.removesuffix(".per")
        # Whether this AI is visible in the selection dropdown in-game
        self.visible = os.path.isfile(
            os.path.join(self.parent_directory, (self.name + ".ai"))
        )
        self.raw_content = read_file_raw(path)
        self.simple_indicator = "*"
        self.complex_indicator = "%"
        self.operators = {"and": "&", "or": "|", "not": "#", "nand": "$", "nor": "@"}
        self.operators_inverse = {v: k for k, v in self.operators.items()}
        self.constants, self.rules = self._parse_raw_content(content=self.raw_content)

    @staticmethod
    def __repair_path(path: str) -> str:
        if os.path.isfile(path) and path.endswith(".per"):
            return path
        raise AoError(
            f"Cannot instance AI with incorrect path {path}."
            "\nPossible reasons:"
            "\n1. The path specified is not a valid location / file."
            "\n2. The path specified is not a .per file but some other type of file."
            "\n3. Between pickling and unpickling this AI, the .per file was deleted."
        )

    def _parse_raw_content(
        self, content: str
    ) -> tuple[dict[str | int, str | int], list[Rule]]:
        constants: dict[str | int, str | int] = {}
        current_rule_lines: list[str] = []
        rules: list[Rule] = []

        for line in content.split("\n"):
            line = line.strip()

            comment_index = line.find(";")
            if comment_index == 0:  # This line is a comment.
                continue
            if comment_index > 0:  # This line contains a comment.
                line = line[:comment_index].strip()
            # Skip empty lines.
            if not line:
                continue

            if line.startswith("(defrule"):
                # If we found the beginning of a rule and we are not busy with another rule,
                if current_rule_lines:
                    rules.append(self._lines_to_rule(current_rule_lines[:]))
                    current_rule_lines = []

            elif line.startswith("(load"):  # We need to load a different file as well!
                extra_file = line.split(' "')[1].removesuffix('")').strip()
                loaded_raw_content = read_file_raw(
                    os.path.join(self.parent_directory, (extra_file + ".per"))
                )
                loaded, _ = self._parse_raw_content(loaded_raw_content)
                constants.update(loaded)

                if current_rule_lines:
                    rules.append(self._lines_to_rule(current_rule_lines[:]))
                    current_rule_lines = []

            elif line.startswith("(defconst"):  # This line is a constant
                name, value = self._line_to_constant(line)
                is_digit, value = str_to_int(value, allow_negative=True)

                # If our constant value is a string, it must be an existing constants' value
                if not is_digit and value in constants:
                    value = constants[value]
                constants[name] = value

                if current_rule_lines:
                    # TODO : convert list to string here, instead of later in the function
                    rules.append(self._lines_to_rule(current_rule_lines[:]))
                    current_rule_lines = []

            # If we are working on a rule, add the current line, unless it's the closing parenthesis
            elif current_rule_lines and len(line.strip()) > 0:
                current_rule_lines.append(line.strip())

        return constants, rules

    @staticmethod
    def _line_to_constant(line: str) -> tuple[str, str]:
        clean = inside_outer_parentheses(line).split()
        if clean[0] != "defconst":
            raise AoError(f"Line '{line}' is not a constant!")
        return clean[1], clean[2]

    def _lines_to_rule(self, lines: list[str]) -> Rule:
        splitter_index = lines.index("=>")
        fact_lines = lines[:splitter_index]
        facts = self._lines_to_facts(fact_lines)
        # TODO parse actions correctly
        action_lines = lines[splitter_index + 1 :]
        actions = self._lines_to_actions(action_lines)
        return Rule(facts, actions)

    @staticmethod
    def _lines_to_actions(lines: list[str]) -> list[Simple]:
        actions: list[Simple] = []
        string = "".join(lines)
        string = re.sub(r"[\s\t\n\r]*\([\s\t\n\r]*", "(", string)  # Remove whitespace
        string = re.sub(r"[\s\t\n\r]*\)[\s\t\n\r]*", ")", string)  # Remove whitespace
        pattern = r"\([a-zA-Z0-9\- ><=!:\+]+\)"
        for action_string in re.findall(pattern, string):
            action_string = action_string.removesuffix(")")
            action_string = action_string.removeprefix("(")
            if len(action_string) > 0:
                actions.append(Simple(action_string.split()))
        return actions

    def _lines_to_facts(self, lines: list[str]) -> list[FactBase]:
        string = "".join(lines)
        string = re.sub(
            r"[\s\t\n\r]*\([\s\t\n\r]*", "(", string
        )  # Remove all irrelevant whitespace
        string = re.sub(
            r"[\s\t\n\r]*\)[\s\t\n\r]*", ")", string
        )  # Remove all irrelevant whitespace

        # Replace all operator keywords for symbols
        for operator, value in self.operators.items():
            string = re.sub(r"\(\s*" + operator + r"\s*\(", f"({value}(", string)

        simples, string, without_globals = self._extract_simple_facts(string)
        complexes = self._extract_complex_facts(without_globals, simples)
        facts: list[FactBase] = []
        facts.extend(simples)
        facts.extend(complexes)
        return facts

    def _extract_simple_facts(self, string: str) -> tuple[list[Simple], str, str]:
        without_globals = string
        simples: list[Simple] = []
        pattern = r"\([a-zA-Z0-9\- ><=!:]+\)"
        match = re.search(pattern, string)
        while match:
            depth = string.count("(", 0, match.start())
            depth -= string.count(")", 0, match.start())
            simple_as_list = match[0][
                1:-1
            ].split()  # Remove the parenthesis TODO Maybe remove using regex.
            simples.append(Simple(simple_as_list))
            string = string.replace(
                match[0], f"({self.simple_indicator}{len(simples) - 1})"
            )
            if depth == 0:
                without_globals = without_globals.replace(match[0], "")
            else:
                without_globals = without_globals.replace(
                    match[0], f"({self.simple_indicator}{len(simples) - 1})"
                )
            match = re.search(pattern, string)
        return simples, string, without_globals

    def _extract_complex_facts(
        self, string: str, simples: list[Simple]
    ) -> list[Complex]:
        if len(string) == 0:
            return []

        pattern = r"\([&|#@$](\((\*|\%)[0-9]+\)){1,2}\)"
        match = re.search(pattern, string)
        complexes: list[Complex] = []
        # If we find a match, we most certainly have a valid complex fact
        while match:
            complexes.append(self.string_to_complex(match[0], simples, complexes))
            string = string.replace(
                match[0], f"({self.complex_indicator}{len(complexes) - 1})"
            )
            match = re.search(pattern, string)
        return complexes

    def string_to_complex(
        self, string: str, simples: list[Simple], complexes: list[Complex]
    ) -> Complex:
        string = string.removesuffix(")")
        string = string.removeprefix("(")
        # The operator symbol, followed by the simple/complex indicator and then the index
        end = string.find(")")
        index1 = int(string[3:end])
        param1 = (
            simples[index1]
            if (string[2] == self.simple_indicator)
            else complexes[index1]
        )
        if string[0] == self.operators["not"]:
            return Complex(name="not", param1=param1)

        if string[0] in self.operators.values():
            start = string.rfind("(")
            end = string.rfind(")")
            index2 = int(string[7:end])
            param2 = (
                simples[index2]
                if (string[start + 1] == self.simple_indicator)
                else complexes[index2]
            )
            return Complex(
                name=self.operators_inverse[string[0]], param1=param1, param2=param2
            )

        raise AoError(f"{string[0]} is not a valid operator symbol!")

    def write(self, target_directory: str = "") -> None:
        destination: str = ""
        if target_directory and dir_exists(target_directory, raise_exception=True):
            destination = os.path.join(target_directory, self.name + ".per")
        elif file_exists(self.path, raise_exception=True):
            destination = self.path
        else:
            raise AoError(
                f"AI {self.name} couldn't write its content to {destination}, "
                "destination doesn't exist!"
            )

        with open(destination, "w", encoding="utf-8") as f:
            # Write constants
            for constant_name, constant_value in self.constants.items():
                f.write(f"(defconst {constant_name} {constant_value}) \n")

            # Write rules
            for rule in self.rules:
                f.write(str(rule) + "\n\n")


# ai_path = "C:\\Program Files\\Microsoft Games\\age of empires ii\\Ai"
# example_path = "C:\\Program Files\\Microsoft Games\\age of empires ii\\Ai\\Alpha.per"
# ai = AIParser.read_single(example_path)
# ai.write("C:\\Users\\Gabi\\Documents\\GitHub\\AlphaScripter")
# names = {"parent", "a", "b", "c", "d", "e", "f"}
