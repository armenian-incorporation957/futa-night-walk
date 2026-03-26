from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class EnemyDef:
    id: str
    name: str
    hp: int
    speed: float
    contact_damage: int
    sprite_key: str
    ai_type: str
    exp_reward: int = 5


@dataclass(frozen=True)
class SkillDef:
    id: str
    name: str
    cooldown: float
    damage: int
    projectile_speed: float
    behavior_type: str
    shots: int = 1
    spread_angle: float = 18.0


@dataclass(frozen=True)
class WaveDef:
    time: float
    enemy_id: str
    count: int
    interval: float


@dataclass
class PlayerStats:
    max_hp: int = 100
    move_speed: float = 230.0
    contact_armor: int = 0


@dataclass
class RunState:
    current_time: float = 0.0
    level: int = 1
    exp: int = 0
    selected_skills: list[str] = field(default_factory=list)
    active_entities: dict[str, int] = field(
        default_factory=lambda: {
            "enemies": 0,
            "projectiles": 0,
            "pickups": 0,
        }
    )
    pending_upgrade_choices: list[str] = field(default_factory=list)
    is_game_over: bool = False
