from __future__ import annotations

from game.entities.enemy import Enemy
from game.entities.pickup import Pickup
from game.entities.player import Player
from game.entities.projectile import Projectile
from game.models.definitions import PlayerStats, RunState
from game.scenes.base_scene import BaseScene
from game.systems.combat_system import CombatSystem
from game.systems.movement_system import MovementSystem
from game.systems.progression_system import ProgressionSystem
from game.systems.spawn_system import SpawnSystem
from game.ui.hud import Hud
from game.ui.upgrade_panel import UpgradePanel


class RunScene(BaseScene):
    def __init__(self, app) -> None:
        super().__init__(app)
        spawn_x, spawn_y = app.config.player_spawn

        self.player = Player(spawn_x, spawn_y, PlayerStats())
        self.run_state = RunState()
        self.enemies: list[Enemy] = []
        self.projectiles: list[Projectile] = []
        self.pickups: list[Pickup] = []

        self.spawn_system = SpawnSystem(app.waves)
        self.movement_system = MovementSystem()
        self.combat_system = CombatSystem()
        self.progression_system = ProgressionSystem(app.skill_defs)

        self.hud = Hud()
        self.upgrade_panel = UpgradePanel()

        self.progression_system.apply_upgrade(self.player, "fire_talisman")
        self._sync_run_state()

    def _sync_run_state(self) -> None:
        self.run_state.level = self.player.level
        self.run_state.exp = self.player.exp
        self.run_state.selected_skills = list(self.player.owned_skills)
        self.run_state.active_entities["enemies"] = len(self.enemies)
        self.run_state.active_entities["projectiles"] = len(self.projectiles)
        self.run_state.active_entities["pickups"] = len(self.pickups)

    def _arena_bounds(self) -> tuple[float, float, float, float]:
        padding = self.app.config.arena_padding
        return (
            float(padding),
            float(padding),
            float(self.app.config.width - padding),
            float(self.app.config.height - padding),
        )

    def _resolve_upgrade_selection(self, choice_index: int) -> None:
        choices = self.run_state.pending_upgrade_choices
        if 0 <= choice_index < len(choices):
            self.progression_system.apply_upgrade(self.player, choices[choice_index])
            self.run_state.pending_upgrade_choices.clear()
            self._sync_run_state()

    def handle_event(self, event) -> None:
        pygame = require_pygame()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.request_scene_change("menu")
            return

        if not self.run_state.pending_upgrade_choices:
            return

        index_map = {
            pygame.K_1: 0,
            pygame.K_2: 1,
            pygame.K_3: 2,
        }
        if event.type == pygame.KEYDOWN and event.key in index_map:
            self._resolve_upgrade_selection(index_map[event.key])

    def update(self, dt: float) -> None:
        if self.run_state.is_game_over:
            return

        if not self.player.is_alive():
            self.run_state.is_game_over = True
            self.request_scene_change("game_over", score=int(self.run_state.current_time))
            return

        if self.run_state.pending_upgrade_choices:
            return

        self.run_state.current_time += dt
        self.player.set_movement(self.app.input_state.move_x, self.app.input_state.move_y)
        self.player.update(dt, self._arena_bounds())

        spawned = self.spawn_system.update(self.run_state.current_time, self.app.enemy_defs, self._arena_bounds())
        self.enemies.extend(spawned)

        self.movement_system.update_enemies(self.enemies, self.player, dt, self._arena_bounds())

        new_projectiles = self.combat_system.spawn_player_projectiles(
            self.player,
            self.app.skill_defs,
            self.enemies,
        )
        self.projectiles.extend(new_projectiles)
        self.combat_system.update_projectiles(self.projectiles, dt, self._arena_bounds())
        gained_exp = self.combat_system.resolve(self.projectiles, self.enemies, self.pickups, self.player)

        leveled_up = self.progression_system.grant_exp(self.player, gained_exp)
        if leveled_up:
            self.run_state.pending_upgrade_choices = self.progression_system.build_upgrade_choices(
                self.player,
                count=3,
            )

        self.enemies = [enemy for enemy in self.enemies if enemy.is_alive()]
        self.projectiles = [projectile for projectile in self.projectiles if projectile.is_alive()]
        self.pickups = [pickup for pickup in self.pickups if pickup.is_alive()]

        if not self.player.is_alive():
            self.run_state.is_game_over = True
            self.request_scene_change("game_over", score=int(self.run_state.current_time))

        self._sync_run_state()

    def render(self, surface) -> None:
        pygame = require_pygame()
        config = self.app.config
        surface.fill(config.background_color)

        for x in range(0, config.width, 32):
            pygame.draw.line(surface, config.grid_color, (x, 0), (x, config.height))
        for y in range(0, config.height, 32):
            pygame.draw.line(surface, config.grid_color, (0, y), (config.width, y))

        for pickup in self.pickups:
            pickup.draw(surface)
        for projectile in self.projectiles:
            projectile.draw(surface)
        for enemy in self.enemies:
            enemy.draw(surface)
        self.player.draw(surface)

        self.hud.draw(surface, self.app, self.player, self.run_state)
        if self.run_state.pending_upgrade_choices:
            self.upgrade_panel.draw(surface, self.app, self.run_state.pending_upgrade_choices)
