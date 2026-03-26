from __future__ import annotations

from game.core.pygame_support import require_pygame
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
    def __init__(self, app, game_mode: str = "campaign") -> None:
        super().__init__(app)
        spawn_x, spawn_y = app.config.player_spawn

        self.player = Player(spawn_x, spawn_y, PlayerStats())
        self.run_state = RunState(game_mode=game_mode)
        self.enemies: list[Enemy] = []
        self.projectiles: list[Projectile] = []
        self.pickups: list[Pickup] = []
        self.stage_time = 0.0
        self.pending_result_saved = False

        self.spawn_system = SpawnSystem(app.waves)
        self.movement_system = MovementSystem()
        self.combat_system = CombatSystem()
        self.progression_system = ProgressionSystem(app.skill_defs)

        self.hud = Hud()
        self.upgrade_panel = UpgradePanel()

        self.start_stage(1, heal_amount=0)

    def start_stage(self, stage_index: int, heal_amount: int = 20) -> None:
        local_stage = ((stage_index - 1) % 4) + 1
        stage_cycle = ((stage_index - 1) // 4) + 1
        difficulty_multiplier = 1.0 + max(0, stage_cycle - 1) * 0.06
        if self.run_state.game_mode == "campaign":
            difficulty_multiplier = 1.0

        if heal_amount > 0:
            self.player.hp = min(self.player.max_hp, self.player.hp + heal_amount)

        self.progression_system.reset_stage_progress(self.player)
        self.stage_time = 0.0
        self.enemies.clear()
        self.projectiles.clear()
        self.pickups.clear()

        stage_skill_pool = self.progression_system.get_stage_skill_pool(stage_index)
        self.run_state.stage_index = stage_index
        self.run_state.stage_cycle = stage_cycle
        self.run_state.stage_state = "intro"
        self.run_state.stage_transition_timer = 1.0
        self.run_state.pending_stage_intro = True
        self.run_state.stage_skill_pool = stage_skill_pool
        self.run_state.stage_skill_levels = {skill_id: 0 for skill_id in stage_skill_pool}
        self.run_state.pending_upgrade_choices = []
        self.run_state.level = self.player.level
        self.run_state.exp = self.player.exp

        self.spawn_system.configure_stage(local_stage, difficulty_multiplier)
        self._sync_run_state()

    def complete_stage(self) -> None:
        self.run_state.stage_state = "transition"
        self.run_state.stage_transition_timer = 1.0
        self.run_state.pending_upgrade_choices.clear()
        self.enemies.clear()
        self.projectiles.clear()
        self.pickups.clear()
        self._sync_run_state()

    def advance_stage(self) -> None:
        if self.run_state.game_mode == "campaign" and self.run_state.stage_index >= 4:
            self.request_scene_change(
                "game_over",
                score=int(self.run_state.current_time),
                stage_reached=self.run_state.stage_index,
                game_mode=self.run_state.game_mode,
                victory=True,
            )
            return
        self.start_stage(self.run_state.stage_index + 1, heal_amount=20)

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

    def _choice_count(self) -> int:
        if self.run_state.stage_state == "starter_select":
            return 5
        return 3

    def _resolve_upgrade_selection(self, choice_index: int) -> None:
        choices = self.run_state.pending_upgrade_choices
        if not (0 <= choice_index < len(choices)):
            return

        skill_id = choices[choice_index]
        self.progression_system.apply_upgrade(self.player, skill_id, self.run_state.stage_skill_levels)
        self.run_state.pending_upgrade_choices.clear()

        if self.progression_system.all_stage_skills_maxed(
            self.run_state.stage_skill_pool,
            self.run_state.stage_skill_levels,
        ):
            self.complete_stage()
        else:
            self.run_state.stage_state = "active"
            self.run_state.pending_stage_intro = False

        self._sync_run_state()

    def _record_result_if_needed(self) -> None:
        if self.pending_result_saved or self.run_state.game_mode != "endless":
            return
        self.app.leaderboard.record(
            stage_reached=self.run_state.stage_index,
            survival_time_seconds=int(self.run_state.current_time),
        )
        self.pending_result_saved = True

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
            pygame.K_4: 3,
            pygame.K_5: 4,
        }
        if event.type == pygame.KEYDOWN and event.key in index_map:
            self._resolve_upgrade_selection(index_map[event.key])

    def update(self, dt: float) -> None:
        if self.run_state.is_game_over:
            return

        if not self.player.is_alive():
            self.run_state.is_game_over = True
            self._record_result_if_needed()
            self.request_scene_change(
                "game_over",
                score=int(self.run_state.current_time),
                stage_reached=self.run_state.stage_index,
                game_mode=self.run_state.game_mode,
                victory=False,
            )
            return

        if self.run_state.stage_state == "intro":
            self.run_state.stage_transition_timer = max(0.0, self.run_state.stage_transition_timer - dt)
            if self.run_state.stage_transition_timer == 0.0:
                self.run_state.stage_state = "starter_select"
                self.run_state.pending_upgrade_choices = list(self.run_state.stage_skill_pool)
            self._sync_run_state()
            return

        if self.run_state.stage_state == "transition":
            self.run_state.stage_transition_timer = max(0.0, self.run_state.stage_transition_timer - dt)
            if self.run_state.stage_transition_timer == 0.0:
                self.advance_stage()
            self._sync_run_state()
            return

        if self.run_state.pending_upgrade_choices:
            return

        self.run_state.current_time += dt
        self.stage_time += dt
        self.player.set_movement(self.app.input_state.move_x, self.app.input_state.move_y)
        self.player.update(dt, self._arena_bounds())

        self.spawn_system.set_active_enemy_count(sum(1 for enemy in self.enemies if enemy.is_alive()))
        spawned = self.spawn_system.update(self.stage_time, self.app.enemy_defs, self._arena_bounds())
        self.enemies.extend(spawned)

        self.movement_system.update_enemies(self.enemies, self.player, dt, self._arena_bounds())

        effective_skill_defs = self.progression_system.effective_skill_defs(self.player.skill_levels)
        new_projectiles = self.combat_system.spawn_player_projectiles(
            self.player,
            self.projectiles,
            effective_skill_defs,
            self.enemies,
        )
        self.projectiles.extend(new_projectiles)
        self.combat_system.update_projectiles(
            self.projectiles,
            dt,
            self._arena_bounds(),
            self.player,
            self.enemies,
        )
        self.combat_system.resolve(self.projectiles, self.enemies, self.pickups, self.player)
        self.combat_system.collect_enemy_drops(self.enemies, self.pickups)
        gained_exp = self.combat_system.update_pickups(self.pickups, self.player, dt)

        leveled_up = self.progression_system.grant_exp(self.player, gained_exp)
        if leveled_up:
            choices = self.progression_system.build_upgrade_choices(
                self.run_state.stage_skill_pool,
                self.run_state.stage_skill_levels,
                count=self._choice_count(),
            )
            self.run_state.pending_upgrade_choices = choices
            if choices:
                self.run_state.stage_state = "upgrade"

        self.enemies = [enemy for enemy in self.enemies if enemy.is_alive()]
        self.projectiles = [projectile for projectile in self.projectiles if projectile.is_alive()]
        self.pickups = [pickup for pickup in self.pickups if pickup.is_alive()]

        if not self.player.is_alive():
            self.run_state.is_game_over = True
            self._record_result_if_needed()
            self.request_scene_change(
                "game_over",
                score=int(self.run_state.current_time),
                stage_reached=self.run_state.stage_index,
                game_mode=self.run_state.game_mode,
                victory=False,
            )

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
            self.upgrade_panel.draw(surface, self.app, self.run_state)
        if self.run_state.pending_stage_intro or self.run_state.stage_state == "transition":
            self._draw_stage_overlay(surface)

    def _draw_stage_overlay(self, surface) -> None:
        pygame = require_pygame()
        config = self.app.config
        resources = self.app.resources
        overlay = pygame.Surface((config.width, config.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 135))
        surface.blit(overlay, (0, 0))

        panel_rect = pygame.Rect(config.width // 2 - 260, config.height // 2 - 150, 520, 300)
        pygame.draw.rect(surface, (21, 27, 36), panel_rect, border_radius=22)
        pygame.draw.rect(surface, (123, 158, 210), panel_rect, 2, border_radius=22)

        title_font = resources.get_font(30)
        body_font = resources.get_font(18)
        small_font = resources.get_font(16)

        if self.run_state.stage_state == "transition":
            title = title_font.render("\u5173\u5361\u5b8c\u6210", True, (242, 231, 194))
            subtitle = body_font.render(
                "\u751f\u547d\u6062\u590d 20\uff0c\u5373\u5c06\u8fdb\u5165\u4e0b\u4e00\u5173",
                True,
                (223, 232, 240),
            )
            surface.blit(title, title.get_rect(center=(config.width // 2, panel_rect.y + 72)))
            surface.blit(subtitle, subtitle.get_rect(center=(config.width // 2, panel_rect.y + 128)))
            return

        title = title_font.render(
            f"\u7b2c {self.run_state.stage_index} \u5173  "
            f"({ '\u95ef\u5173' if self.run_state.game_mode == 'campaign' else '\u65e0\u9650' })",
            True,
            (242, 231, 194),
        )
        subtitle = body_font.render("\u672c\u5173\u53ef\u5347\u7ea7\u7684 5 \u4e2a\u6280\u80fd", True, (223, 232, 240))
        surface.blit(title, title.get_rect(center=(config.width // 2, panel_rect.y + 42)))
        surface.blit(subtitle, subtitle.get_rect(center=(config.width // 2, panel_rect.y + 78)))

        for index, skill_id in enumerate(self.run_state.stage_skill_pool):
            skill = self.app.skill_defs[skill_id]
            text = small_font.render(f"{index + 1}. {skill.name}  -  {skill.description}", True, (194, 205, 218))
            surface.blit(text, (panel_rect.x + 28, panel_rect.y + 118 + index * 28))

        footer = small_font.render(
            "\u5f39\u7a97\u7ed3\u675f\u540e\u5148\u9009 1 \u4e2a\u8d77\u59cb\u6280\u80fd",
            True,
            (172, 185, 201),
        )
        surface.blit(footer, footer.get_rect(center=(config.width // 2, panel_rect.bottom - 28)))
