# Project Layout

## Module Map

- `main.py`
  Thin entrypoint. Do not add gameplay logic here.
- `game/app.py`
  Bootstrap pygame, own the clock and screen, handle temporary fullscreen/window switching, load content, and switch scenes.
- `game/scenes/`
  Coordinate one screen or flow state at a time.
  `menu_scene.py` owns the start menu, help popup, skill compendium, and display toggle.
  `run_scene.py` owns stage flow and orchestration.
  `game_over_scene.py` owns end-of-run presentation.
- `game/entities/`
  Hold runtime actors and their local state.
- `game/systems/`
  Hold reusable gameplay rules shared across entities.
  `combat_system.py` owns projectile spawning, hit resolution, pickup attraction, and projectile cleanup.
  `progression_system.py` owns stage skill pools, upgrades, and leveled skill snapshots.
  `spawn_system.py` owns stage-aware scripted waves and the endless director.
- `game/content/`
  Parse and validate JSON definitions.
- `game/models/`
  Define dataclasses for content and run state.
- `game/ui/`
  Render HUD and overlays.
  `skill_views.py` is the shared helper for skill detail text, upgrade deltas, icon rendering, and layout data.
- `assets/data/`
  Store the project's data-driven gameplay content.
- `assets/images/skills/`
  Optional PNG overrides for skill icons.
  The runtime must still work without any actual files here.
- `save_data/`
  Store endless leaderboard data written at runtime.
- `tests/`
  Hold loader, system, scene, leaderboard, and skill-view coverage.

## Current Flow States

- Main menu:
  `campaign`, `endless`, `help`, and temporary display-mode toggle.
- Run scene stage flow:
  `stage_intro` -> `starter_select` -> `active` -> `upgrade` -> `transition`
- Stage completion:
  All 5 stage skills reach level 3, then transition to the next stage or final victory.
- Endless results:
  Record only on endless-mode loss through the leaderboard store.

## Extension Recipes

### Add A New Enemy

- Add the enemy definition to `assets/data/enemies.json`.
- Reuse an existing `ai_type` if possible.
- Extend `game/entities/enemy.py` only for runtime-facing attributes.
- Extend `game/systems/movement_system.py` only if the new enemy needs a truly new movement rule.
- Add or update tests for loader validation and any new AI behavior.

### Add Or Rework A Skill

- Add or edit the skill definition in `assets/data/skills.json`.
- Reuse an existing `behavior_type` if possible.
- Keep numeric growth in `level_scaling`.
- Extend `game/systems/combat_system.py` only when a new runtime behavior is necessary.
- Extend `game/ui/skill_views.py` if the new behavior needs new icon language or new stat-display formatting.
- Add or update tests for loader validity, projectile spawning, upgrade deltas, and any new cleanup rules.

### Change Stage Progression

- Keep the per-stage skill pool logic in `game/systems/progression_system.py`.
- Keep run-state stage transitions in `game/scenes/run_scene.py`.
- Keep stage intro, starter selection, and transition overlays as separate states.
- Add scene and system coverage for any new stage rule or modal flow.

### Add A New Scene

- Create the scene under `game/scenes/`.
- Preserve the `handle_event`, `update`, and `render` interface.
- Register the scene in `GameApp.change_scene`.
- Add scene-transition coverage under `tests/test_scenes.py`.

## Validation Checklist

- Run `python -m unittest discover -s tests`.
- Run `python -m compileall game tests main.py`.
- Mention whether you launched `python main.py`.
- Mention whether runtime-only behavior such as fullscreen switching or scroll interaction was manually exercised.
