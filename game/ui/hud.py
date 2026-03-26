from __future__ import annotations

from game.core.pygame_support import require_pygame


class Hud:
    def draw(self, surface, app, player, run_state) -> None:
        pygame = require_pygame()
        width = 240
        hp_ratio = max(0.0, player.hp / player.max_hp)
        exp_ratio = 0.0 if player.exp_to_next == 0 else player.exp / player.exp_to_next
        skill_names = [
            app.skill_defs[skill_id].name if skill_id in app.skill_defs else skill_id
            for skill_id in run_state.selected_skills
        ]
        skill_label = "\u3001".join(skill_names) if skill_names else "\u65e0"

        font = app.resources.get_font(18)
        small_font = app.resources.get_font(16)

        pygame.draw.rect(surface, (34, 42, 54), (18, 16, width, 18))
        pygame.draw.rect(surface, (224, 87, 102), (18, 16, int(width * hp_ratio), 18))
        pygame.draw.rect(surface, (34, 42, 54), (18, 42, width, 12))
        pygame.draw.rect(surface, (94, 196, 165), (18, 42, int(width * exp_ratio), 12))

        stats_text = font.render(
            f"\u751f\u547d {int(player.hp)}/{int(player.max_hp)}  "
            f"\u7b49\u7ea7 {player.level}  "
            f"\u65f6\u95f4 {int(run_state.current_time)}\u79d2",
            True,
            (232, 236, 240),
        )
        skill_text = small_font.render(
            "\u7b26\u5370: " + skill_label,
            True,
            (205, 214, 225),
        )
        enemy_text = small_font.render(
            f"\u654c\u4eba {run_state.active_entities['enemies']}  "
            f"\u98de\u7b26 {run_state.active_entities['projectiles']}",
            True,
            (185, 197, 209),
        )

        surface.blit(stats_text, (18, 62))
        surface.blit(skill_text, (18, 88))
        surface.blit(enemy_text, (18, 110))
