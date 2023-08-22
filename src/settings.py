from dataclasses import dataclass, field

import yaml


@dataclass
class Config:
    fails_before_reset: int
    game_time: int
    default_mutation_chance: float
    anneal_amount: int
    max_fact_length: int
    max_action_length: int
    ai_length: int
    simple_count: int
    attack_rule_count: int
    duc_count: int
    goal_rule_count: int
    goal_action_count: int
    executable_path: str
    network_drive: str
    local_drive: str
    working_ais: list[str]
    elo_dict: dict[str, float]
    arena_dict: dict[str, float]
    ai_ladder: list[str]
    all_ai_list: list[str]
    civ: str
    restart: bool
    force_age_up: bool
    allow_complex: bool
    force_house: bool
    allow_duc: bool
    villager_preset: bool
    force_imperial_age: bool
    force_barracks: bool
    force_scout: bool
    force_castle_age_units: bool
    allow_units: bool
    allow_towers: bool
    force_resign: bool = field(init=False)
    allow_attack_rule: bool = field(init=False)

    def __post_init__(self) -> None:
        self.force_resign = not self.restart
        self.allow_attack_rule = not self.restart


with open("config.yaml", encoding="utf-8") as f:
    data = yaml.safe_load(f)

CONFIG = Config(**data)
