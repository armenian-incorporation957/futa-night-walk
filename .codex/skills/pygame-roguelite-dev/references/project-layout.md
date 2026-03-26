# Project Layout

## Module Map

- `main.py`
  Thin entrypoint. Do not add gameplay logic here.
- `game/app.py`
  Bootstrap pygame, own the clock and screen, load content, switch scenes.
- `game/scenes/`
  Coordinate one screen or flow state at a time.
- `game/entities/`
  Hold runtime actors and their local state.
- `game/systems/`
  Hold reusable gameplay rules shared across entities.
- `game/content/`
  Parse and validate JSON definitions.
- `game/models/`
  Define dataclasses for content and run state.
- `game/ui/`
  Render HUD and overlay components.
- `assets/data/`
  Store the project's data-driven gameplay content.
- `tests/`
  Hold loader, system, and scene coverage.

## Extension Recipes

### Add A New Enemy

- Add the enemy definition to `assets/data/enemies.json`.
- Reuse an existing `ai_type` if possible.
- Extend `game/entities/enemy.py` only for runtime-facing attributes.
- Extend `game/systems/movement_system.py` only if the new enemy needs a truly new movement rule.
- Add or update tests for loader validation and any new AI behavior.

### Add A New Skill

- Add the skill definition to `assets/data/skills.json`.
- Reuse existing projectile behavior if possible.
- Extend `game/systems/combat_system.py` only when a new `behavior_type` is necessary.
- Keep upgrade selection changes in `game/systems/progression_system.py`.
- Add or update tests for loader validity, projectile spawning, and upgrade choices.

### Add A New Scene

- Create the scene under `game/scenes/`.
- Preserve the `handle_event`, `update`, and `render` interface.
- Register the scene in `GameApp.change_scene`.
- Add scene-transition coverage under `tests/test_scenes.py`.

## Validation Checklist

- Run `python -m unittest discover -s tests`.
- Run `python -m compileall game tests main.py`.
- Mention whether `pygame` was installed and whether the interactive runtime was launched.
