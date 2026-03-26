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
    description: str
    group: str
    cooldown: float
    damage: int
    projectile_speed: float
    behavior_type: str
    level_scaling: dict[int, dict[str, int | float]] = field(default_factory=dict)
    duration: float = 1.6
    shots: int = 1
    spread_angle: float = 18.0
    burn_duration: float = 0.0
    burn_damage: float = 0.0
    slow_factor: float = 1.0
    slow_duration: float = 0.0
    chain_targets: int = 0
    chain_range: float = 0.0
    chain_damage_ratio: float = 0.0
    explosion_radius: float = 0.0
    explosion_damage_ratio: float = 0.0
    orbit_count: int = 0
    orbit_radius: float = 0.0
    orbit_speed: float = 0.0
    homing_strength: float = 0.0
    hit_stun: float = 0.0
    healing_amount: float = 0.0


@dataclass(frozen=True)
class WaveDef:
    stage: int
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
    game_mode: str = "campaign"
    stage_index: int = 1
    stage_cycle: int = 1
    stage_state: str = "intro"
    level: int = 1
    exp: int = 0
    pending_stage_intro: bool = True
    selected_skills: list[str] = field(default_factory=list)
    stage_skill_pool: list[str] = field(default_factory=list)
    stage_skill_levels: dict[str, int] = field(default_factory=dict)
    stage_transition_timer: float = 0.0
    active_entities: dict[str, int] = field(
        default_factory=lambda: {
            "enemies": 0,
            "projectiles": 0,
            "pickups": 0,
        }
    )
    pending_upgrade_choices: list[str] = field(default_factory=list)
    is_game_over: bool = False
