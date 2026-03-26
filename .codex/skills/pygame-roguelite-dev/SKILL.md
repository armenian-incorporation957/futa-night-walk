---
name: pygame-roguelite-dev
description: Development conventions for this specific Python + pygame roguelite project. Use when implementing, refactoring, reviewing, or extending gameplay code in this repo, especially for scene/entity/system boundaries, JSON-driven content, test coverage, and project-specific validation commands.
---

# Pygame Roguelite Dev

Follow this skill when changing the game in this repository. Preserve the current package layout, keep gameplay logic modular, and validate changes with the existing lightweight test flow.

## Work Within The Current Architecture

- Keep `main.py` limited to startup and `GameApp` creation.
- Keep `game/app.py` responsible for pygame bootstrap, the main loop, scene switching, and global runtime objects.
- Keep each scene limited to `handle_event`, `update`, and `render`.
- Keep scenes responsible for orchestration and transitions, not low-level combat or spawn rules.
- Keep cross-entity gameplay logic in `game/systems/`.
- Keep runtime objects in `game/entities/` lightweight and stateful rather than turning them into large controller classes.
- Keep static definitions and run-state dataclasses in `game/models/`.
- Keep content loading and validation in `game/content/`.
- Keep HUD and overlays in `game/ui/`.
- Do not collapse the structure back into a giant `main.py` or a single scene file.
- Do not introduce ECS unless the user explicitly asks for a larger architecture change.

## Extend Content Through Data First

- Prefer changing numbers, wave schedules, and base content in `assets/data/*.json`.
- Keep `enemies.json`, `skills.json`, and `waves.json` as the source of truth for basic content definitions.
- Add a new enemy by adding JSON data first, then only extend runtime code if a new AI behavior is actually needed.
- Add a new skill by adding JSON data first, then only extend projectile or behavior handling if `behavior_type` requires new logic.
- Keep the split between definition objects like `EnemyDef` and runtime instances like `Enemy`.
- Stick with JSON unless the user explicitly wants YAML or JSON becomes materially limiting.

## Keep Responsibilities Clean

- Put movement decisions in `movement_system.py`.
- Put projectile spawning and hit resolution in `combat_system.py`.
- Put level-up logic and upgrade choice generation in `progression_system.py`.
- Put timed enemy scheduling in `spawn_system.py`.
- Keep drawing out of systems.
- Keep scene-level code from reimplementing system logic inline.
- Prefer simple placeholder visuals and deterministic rules over premature asset or rendering complexity.

## Add Tests With Each Behavior Change

- Add or update tests under `tests/` whenever loaders, progression, combat rules, spawn timing, or scene transitions change.
- Prefer headless tests that do not require a live pygame window.
- Cover invalid content data when touching loaders.
- Cover scene transition expectations when changing flow between menu, run, and game-over states.
- Cover extension paths such as new skill selection rules or new spawn timing logic before closing the task.

## Validate Before Finishing

- Run `python -m unittest discover -s tests`.
- Run `python -m compileall game tests main.py`.
- If the task requires launching the game, install dependencies first with `python -m pip install -r requirements.txt`.
- If pygame is unavailable, still complete all non-graphical checks and state clearly that the runtime was not launched.

## Use The Reference

- Read [references/project-layout.md](references/project-layout.md) when you need the current module map, extension recipes, or the standard validation checklist.
