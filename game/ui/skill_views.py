from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

from game.models.definitions import SkillDef


GROUP_LABELS = {
    "straight": "\u76f4\u7ebf\u8f93\u51fa",
    "control": "\u63a7\u573a\u51cf\u76ca",
    "burst": "\u7206\u53d1\u8303\u56f4",
    "defense": "\u9632\u5fa1\u53ec\u5524",
}


@dataclass(frozen=True)
class SkillDetailView:
    name: str
    group_label: str
    summary_line: str
    mechanic_lines: list[str]
    level_lines: dict[int, list[str]]
    icon_path: Path | None


@dataclass(frozen=True)
class UpgradeDeltaView:
    name: str
    from_level: int
    to_level: int
    summary_line: str
    change_lines: list[str]
    icon_path: Path | None


@dataclass(frozen=True)
class HudSkillView:
    skill_id: str
    name: str
    level: int
    icon_path: Path | None


def build_skill_level_snapshots(skill_def: SkillDef) -> dict[int, SkillDef]:
    snapshots: dict[int, SkillDef] = {1: skill_def}
    current = skill_def
    for level in range(2, 4):
        overrides = skill_def.level_scaling.get(level, {})
        if overrides:
            current = replace(current, **overrides)
        snapshots[level] = current
    return snapshots


def build_skill_detail_view(skill_def: SkillDef) -> SkillDetailView:
    snapshots = build_skill_level_snapshots(skill_def)
    return SkillDetailView(
        name=skill_def.name,
        group_label=GROUP_LABELS.get(skill_def.group, skill_def.group),
        summary_line=skill_def.description,
        mechanic_lines=_mechanic_lines(skill_def),
        level_lines={level: _stat_lines(snapshot) for level, snapshot in snapshots.items()},
        icon_path=_icon_path(skill_def.id),
    )


def build_upgrade_delta_view(skill_def: SkillDef, current_level: int) -> UpgradeDeltaView:
    snapshots = build_skill_level_snapshots(skill_def)
    from_level = max(0, min(3, current_level))
    to_level = min(3, from_level + 1)
    if from_level == 0:
        change_lines = _stat_lines(snapshots[1])
    else:
        change_lines = _delta_lines(snapshots[from_level], snapshots[to_level])
    return UpgradeDeltaView(
        name=skill_def.name,
        from_level=from_level,
        to_level=to_level,
        summary_line=skill_def.description,
        change_lines=change_lines,
        icon_path=_icon_path(skill_def.id),
    )


def build_hud_skill_views(
    skill_defs: dict[str, SkillDef],
    selected_skills: list[str],
    skill_levels: dict[str, int],
) -> list[HudSkillView]:
    views: list[HudSkillView] = []
    for skill_id in selected_skills:
        if skill_id not in skill_defs:
            continue
        views.append(
            HudSkillView(
                skill_id=skill_id,
                name=skill_defs[skill_id].name,
                level=skill_levels.get(skill_id, 0),
                icon_path=_icon_path(skill_id),
            )
        )
    return views


def _icon_path(skill_id: str) -> Path | None:
    root = Path(__file__).resolve().parents[2]
    path = root / "assets" / "images" / "skills" / f"{skill_id}.png"
    return path if path.exists() else None


def _mechanic_lines(skill_def: SkillDef) -> list[str]:
    base = {
        "burn_bolt": [
            "\u76f4\u7ebf\u7b26\u5f39\uff0c\u547d\u4e2d\u540e\u65bd\u52a0\u6301\u7eed\u4f24\u5bb3",
            "\u9002\u5408\u5355\u4f53\u7a33\u5b9a\u8f93\u51fa",
        ],
        "chain_bolt": [
            "\u4e3b\u76ee\u6807\u9ad8\u4f24\uff0c\u547d\u4e2d\u540e\u8fde\u5230\u9644\u8fd1\u654c\u4eba",
            "\u53ef\u4ee5\u540c\u65f6\u538b\u5236\u5c0f\u7fa4\u654c",
        ],
        "frost_spread": [
            "\u6247\u5f62\u6563\u5c04\uff0c\u547d\u4e2d\u9644\u52a0\u51cf\u901f",
            "\u9002\u5408\u63a7\u573a\u4e0e\u963b\u6b62\u8fd1\u8eab",
        ],
        "spread": [
            "\u591a\u5f39\u4f53\u6269\u6563\u6216\u73af\u5f62\u6253\u51fb",
            "\u9002\u5408\u8fd1\u4e2d\u8ddd\u79bb\u63a7\u573a",
        ],
        "homing_blast": [
            "\u5f39\u4f53\u4f1a\u8ffd\u8e2a\u654c\u4eba\uff0c\u547d\u4e2d\u540e\u53ef\u7206\u88c2",
            "\u5bf9\u79fb\u52a8\u76ee\u6807\u66f4\u7a33\u5b9a",
        ],
        "orbit_guard": [
            "\u62a4\u7b26\u73af\u7ed5\u89d2\u8272\u65cb\u8f6c\uff0c\u6301\u7eed\u78b0\u649e\u4f24\u5bb3",
            "\u9002\u5408\u6297\u538b\u4e0e\u8d34\u8eab\u9632\u7ebf",
        ],
        "bolt": [
            "\u9ad8\u901f\u5355\u4f53\u7b26\u5f39\uff0c\u4ee5\u76f4\u63a5\u547d\u4e2d\u4e3a\u4e3b",
            "\u6570\u503c\u589e\u957f\u76f4\u89c2",
        ],
        "healing_mark": [
            "\u5468\u671f\u6027\u6062\u590d\u751f\u547d\uff0c\u4e0d\u4f1a\u751f\u6210\u5f39\u4f53",
            "\u63d0\u9ad8\u7eed\u822a\u4e0e\u5bb9\u9519",
        ],
    }
    return list(base.get(skill_def.behavior_type, [skill_def.description]))


def _delta_lines(previous: SkillDef, current: SkillDef) -> list[str]:
    lines: list[str] = []
    for label, before, after in _stat_pairs(previous, current):
        if before == after:
            continue
        lines.append(f"{label}: {_format_value(label, before)} -> {_format_value(label, after)}")
    return lines or ["\u672c\u6b21\u5347\u7ea7\u4e3a\u7efc\u5408\u6027\u5f3a\u5316"]


def _stat_lines(skill: SkillDef) -> list[str]:
    lines = [
        f"{label}: {_format_value(label, value)}"
        for label, value in _display_stats(skill)
    ]
    return lines or ["\u63d0\u4f9b\u57fa\u7840\u6548\u679c"]


def _display_stats(skill: SkillDef) -> list[tuple[str, int | float]]:
    stats: list[tuple[str, int | float]] = [
        ("\u4f24\u5bb3", skill.damage),
        ("\u51b7\u5374", skill.cooldown),
    ]
    if skill.projectile_speed > 0:
        stats.append(("\u5f39\u901f", skill.projectile_speed))
    if skill.shots > 1:
        stats.append(("\u5f39\u4f53\u6570", skill.shots))
    if skill.spread_angle > 0 and skill.shots > 1:
        stats.append(("\u6563\u5c04\u89d2", skill.spread_angle))
    if skill.burn_damage > 0:
        stats.append(("\u707c\u70e7\u4f24\u5bb3", skill.burn_damage))
    if skill.burn_duration > 0:
        stats.append(("\u707c\u70e7\u65f6\u957f", skill.burn_duration))
    if skill.slow_duration > 0:
        stats.append(("\u51cf\u901f\u540e\u79fb\u901f", skill.slow_factor))
        stats.append(("\u51cf\u901f\u65f6\u957f", skill.slow_duration))
    if skill.chain_targets > 0:
        stats.append(("\u8fde\u9501\u76ee\u6807", skill.chain_targets))
    if skill.chain_range > 0:
        stats.append(("\u8fde\u9501\u8303\u56f4", skill.chain_range))
    if skill.chain_damage_ratio > 0:
        stats.append(("\u8fde\u9501\u4f24\u5bb3", skill.chain_damage_ratio))
    if skill.explosion_radius > 0:
        stats.append(("\u7206\u88c2\u8303\u56f4", skill.explosion_radius))
    if skill.explosion_damage_ratio > 0:
        stats.append(("\u7206\u88c2\u4f24\u5bb3", skill.explosion_damage_ratio))
    if skill.orbit_count > 0:
        stats.append(("\u62a4\u7b26\u6570\u91cf", skill.orbit_count))
    if skill.orbit_radius > 0:
        stats.append(("\u73af\u7ed5\u534a\u5f84", skill.orbit_radius))
    if skill.orbit_speed > 0:
        stats.append(("\u73af\u7ed5\u901f\u5ea6", skill.orbit_speed))
    if skill.homing_strength > 0:
        stats.append(("\u8ffd\u8e2a\u5f3a\u5ea6", skill.homing_strength))
    if skill.hit_stun > 0:
        stats.append(("\u786c\u76f4", skill.hit_stun))
    if skill.healing_amount > 0:
        stats.append(("\u6cbb\u7597", skill.healing_amount))
    return stats


def _stat_pairs(previous: SkillDef, current: SkillDef) -> list[tuple[str, int | float, int | float]]:
    previous_map = dict(_display_stats(previous))
    current_map = dict(_display_stats(current))
    labels = list(current_map)
    for label in previous_map:
        if label not in current_map:
            labels.append(label)
    return [(label, previous_map.get(label, 0), current_map.get(label, 0)) for label in labels]


def _format_value(label: str, value: int | float) -> str:
    if label in {"\u51b7\u5374", "\u707c\u70e7\u65f6\u957f", "\u51cf\u901f\u65f6\u957f", "\u786c\u76f4"}:
        return f"{float(value):.2f}\u79d2"
    if label in {"\u8fde\u9501\u4f24\u5bb3", "\u7206\u88c2\u4f24\u5bb3", "\u51cf\u901f\u540e\u79fb\u901f"}:
        return f"{int(round(float(value) * 100))}%"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    if isinstance(value, float):
        return f"{value:.1f}"
    return str(value)
