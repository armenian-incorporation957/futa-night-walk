---
name: pygame-roguelite-dev
description: Development conventions for this specific Python + pygame roguelite project. Use when implementing, refactoring, reviewing, or extending gameplay code in this repo, especially for stage flow, skill presentation, JSON-driven content, runtime display behavior, and project-specific validation commands.
---

# Pygame Roguelite Dev

Follow this skill when changing the game in this repository. Preserve the current package layout, keep gameplay and UI logic modular, and validate changes with the existing lightweight test flow.

## Work Within The Current Architecture

- Keep `main.py` limited to startup and `GameApp` creation.
- Keep `game/app.py` responsible for pygame bootstrap, display-mode switching, the main loop, scene switching, and global runtime objects.
- Keep each scene limited to `handle_event`, `update`, and `render`.
- Keep scenes responsible for orchestration, modal flow, and transitions, not low-level combat or spawn rules.
- Keep cross-entity gameplay logic in `game/systems/`.
- Keep runtime objects in `game/entities/` lightweight and stateful rather than turning them into large controller classes.
- Keep static definitions and run-state dataclasses in `game/models/`.
- Keep content loading and validation in `game/content/`.
- Keep HUD, overlays, and shared skill-presentation helpers in `game/ui/`.
- Do not collapse the structure back into a giant `main.py` or a single scene file.
- Do not introduce ECS unless the user explicitly asks for a larger architecture change.

## Respect The Current Game Loop

- Preserve the dual-mode structure: `campaign` and `endless`.
- Preserve stage-based progression.
  Each stage uses a 5-skill pool, each skill levels from 0 to 3, and stage completion happens when all 5 skills are maxed.
- Keep stage-state flow explicit in `RunScene`.
  The current flow includes `stage_intro`, `starter_select`, `active`, `upgrade`, and `transition`.
- Keep stage intro, starter choice, upgrade choice, and stage transition as separate UI states rather than overlapping overlays.
- Keep leaderboard writes limited to endless mode and routed through the local leaderboard store.

## Extend Content Through Data First

- Prefer changing numbers, stage pools, wave schedules, and base content in `assets/data/*.json`.
- Keep `enemies.json`, `skills.json`, and `waves.json` as the source of truth for basic content definitions.
- Add a new enemy by adding JSON data first, then only extend runtime code if a new AI behavior is actually needed.
- Add a new skill by adding JSON data first, then only extend projectile or behavior handling if `behavior_type` requires new logic.
- Keep the split between definition objects like `EnemyDef` and runtime instances like `Enemy`.
- Preserve the 20-skill pool and grouped-skill assumptions unless the task explicitly changes the progression design.
- Keep skill level scaling in JSON through `level_scaling` instead of cloning each skill into separate skill ids.
- Stick with JSON unless the user explicitly wants YAML or JSON becomes materially limiting.

## Keep Responsibilities Clean

- Put movement decisions in `movement_system.py`.
- Put projectile spawning, hit resolution, pickup attraction, and projectile cleanup in `combat_system.py`.
- Put skill-pool assignment, upgrade choice generation, and effective leveled skill definitions in `progression_system.py`.
- Put stage-aware spawn scheduling and endless director logic in `spawn_system.py`.
- Keep drawing out of systems.
- Keep scene-level code from reimplementing system logic inline.
- Use `game/ui/skill_views.py` as the shared source for skill stats, icon rendering, and detail/upgrade presentation data.
- If a UI screen needs skill names, icons, per-level values, or upgrade deltas, reuse the shared skill-view helpers instead of formatting those ad hoc inside the scene.

## Preserve Current UI And Runtime Conventions

- Keep the main menu mouse-driven.
- Keep the help popup split between control instructions and the full skill compendium.
- Keep the skill compendium grouped into four tabs and treat the detail area as the only scrollable region.
- Keep upgrade options card-based rather than reverting to compact text rows.
- Keep the in-run skill list as a dedicated skill column rather than truncating skills into a single line.
- Keep runtime display-mode switching in `GameApp`; scenes may trigger it, but should not own display creation directly.
- Treat skill icons as programmatic defaults.
  If a PNG exists under `assets/images/skills/{skill_id}.png`, it may override the generated icon, but the game must still render cleanly without external art.

## Be Careful With Projectile Lifetime Rules

- Ordinary flying projectiles should be removed when they leave arena bounds, not because of a short default lifetime.
- Only persistent/time-boxed projectiles such as orbiting guards should rely on lifetime expiration.
- Prefer an explicit lifecycle flag on the projectile runtime object over scattered `behavior_type` checks.
- When touching projectile cleanup, verify both in-bounds persistence and out-of-bounds removal.

## Add Tests With Each Behavior Change

- Add or update tests under `tests/` whenever loaders, progression, combat rules, spawn timing, scene transitions, menu interaction, or display-mode behavior change.
- Prefer headless tests that do not require a live pygame window.
- Cover invalid content data when touching loaders.
- Cover scene transition expectations when changing flow between menu, run, and game-over states.
- Cover UI-state behavior such as help-tab selection, scroll resets, stage-intro dismissal, and display toggles when those paths change.
- Cover extension paths such as new skill behaviors, new stage rules, or new projectile cleanup logic before closing the task.

## Validate Before Finishing

- Run `python -m unittest discover -s tests`.
- Run `python -m compileall game tests main.py`.
- If the task requires launching the game, state clearly whether you actually ran `python main.py`.
- If pygame is unavailable, still complete all non-graphical checks and state clearly that the runtime was not launched.

## Use The Reference

- Read [references/project-layout.md](references/project-layout.md) when you need the current module map, flow states, extension recipes, or the standard validation checklist.
