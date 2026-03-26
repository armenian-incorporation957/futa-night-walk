from __future__ import annotations

from game.core.pygame_support import require_pygame


class Hud:
    def draw(self, surface, app, player, run_state) -> None:
        pygame = require_pygame()
        width = 240
        hp_ratio = max(0.0, player.hp / player.max_hp)
        exp_ratio = 0.0 if player.exp_to_next == 0 else player.exp / player.exp_to_next
        mode_label = "\u95ef\u5173" if run_state.game_mode == "campaign" else "\u65e0\u9650"
        pool_progress = sum(1 for level in run_state.stage_skill_levels.values() if level >= 3)
        skill_names = [
            f"{app.skill_defs[skill_id].name} Lv.{player.skill_levels.get(skill_id, 0)}"
            for skill_id in run_state.selected_skills
            if skill_id in app.skill_defs
        ]
        skill_label = "\u3001".join(skill_names[:3]) if skill_names else "\u672a\u89e3\u9501"

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
        stage_text = small_font.render(
            f"{mode_label}  \u7b2c {run_state.stage_index} \u5173  "
            f"\u672c\u5173\u6ee1\u7ea7 {pool_progress}/5",
            True,
            (205, 214, 225),
        )
        skill_text = small_font.render(
            "\u5f53\u524d\u6280\u80fd: " + skill_label,
            True,
            (185, 197, 209),
        )

        surface.blit(stats_text, (18, 62))
        surface.blit(stage_text, (18, 88))
        surface.blit(skill_text, (18, 110))
