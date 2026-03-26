from __future__ import annotations

from game.core.pygame_support import require_pygame


class Hud:
    def draw(self, surface, app, player, run_state) -> None:
        pygame = require_pygame()
        width = 240
        hp_ratio = max(0.0, player.hp / player.max_hp)
        exp_ratio = 0.0 if player.exp_to_next == 0 else player.exp / player.exp_to_next

        font = app.resources.get_font(18)
        small_font = app.resources.get_font(16)

        pygame.draw.rect(surface, (34, 42, 54), (18, 16, width, 18))
        pygame.draw.rect(surface, (224, 87, 102), (18, 16, int(width * hp_ratio), 18))
        pygame.draw.rect(surface, (34, 42, 54), (18, 42, width, 12))
        pygame.draw.rect(surface, (94, 196, 165), (18, 42, int(width * exp_ratio), 12))

        stats_text = font.render(
            f"HP {int(player.hp)}/{int(player.max_hp)}  Lv.{player.level}  Time {int(run_state.current_time)}",
            True,
            (232, 236, 240),
        )
        skill_text = small_font.render(
            "符印: " + ", ".join(run_state.selected_skills),
            True,
            (205, 214, 225),
        )
        enemy_text = small_font.render(
            f"敌人 {run_state.active_entities['enemies']}  投射物 {run_state.active_entities['projectiles']}",
            True,
            (185, 197, 209),
        )

        surface.blit(stats_text, (18, 62))
        surface.blit(skill_text, (18, 88))
        surface.blit(enemy_text, (18, 110))
