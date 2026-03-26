from __future__ import annotations

from game.core.pygame_support import require_pygame
from game.ui.skill_views import build_hud_skill_views


class Hud:
    def build_skill_entries(self, app, player, run_state):
        return build_hud_skill_views(app.skill_defs, run_state.selected_skills, player.skill_levels)

    def draw(self, surface, app, player, run_state) -> None:
        pygame = require_pygame()
        width = 240
        hp_ratio = max(0.0, player.hp / player.max_hp)
        exp_ratio = 0.0 if player.exp_to_next == 0 else player.exp / player.exp_to_next
        mode_label = "\u95ef\u5173" if run_state.game_mode == "campaign" else "\u65e0\u9650"
        pool_progress = sum(1 for level in run_state.stage_skill_levels.values() if level >= 3)
        entries = self.build_skill_entries(app, player, run_state)

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
        surface.blit(stats_text, (18, 62))
        surface.blit(stage_text, (18, 88))

        self._draw_skill_column(surface, app, entries)

    def _draw_skill_column(self, surface, app, entries) -> None:
        pygame = require_pygame()
        title_font = app.resources.get_font(16)
        text_font = app.resources.get_font(15)
        panel_rect = pygame.Rect(app.config.width - 206, 16, 188, 44 + 48 * max(1, len(entries)))
        pygame.draw.rect(surface, (19, 25, 33), panel_rect, border_radius=16)
        pygame.draw.rect(surface, (92, 116, 152), panel_rect, 2, border_radius=16)
        title = title_font.render("\u672c\u5173\u6280\u80fd", True, (238, 242, 247))
        surface.blit(title, (panel_rect.x + 14, panel_rect.y + 12))

        if not entries:
            empty = text_font.render("\u672a\u89e3\u9501", True, (176, 189, 205))
            surface.blit(empty, (panel_rect.x + 14, panel_rect.y + 36))
            return

        for index, entry in enumerate(entries[:5]):
            row_rect = pygame.Rect(panel_rect.x + 10, panel_rect.y + 34 + index * 48, panel_rect.width - 20, 40)
            pygame.draw.rect(surface, (32, 41, 54), row_rect, border_radius=12)
            self._draw_icon(surface, app, entry.icon_path, pygame.Rect(row_rect.x + 6, row_rect.y + 4, 32, 32))
            name = text_font.render(entry.name, True, (229, 236, 244))
            level = text_font.render(f"Lv.{entry.level}", True, (167, 199, 229))
            surface.blit(name, (row_rect.x + 46, row_rect.y + 7))
            surface.blit(level, (row_rect.x + 46, row_rect.y + 21))

    def _draw_icon(self, surface, app, icon_path, rect) -> None:
        pygame = require_pygame()
        pygame.draw.rect(surface, (43, 55, 72), rect, border_radius=10)
        pygame.draw.rect(surface, (103, 128, 168), rect, 2, border_radius=10)
        image = app.resources.get_image(icon_path) if icon_path else None
        if image is not None:
            scaled = pygame.transform.smoothscale(image, (rect.width - 6, rect.height - 6))
            surface.blit(scaled, scaled.get_rect(center=rect.center))
            return

        placeholder_font = app.resources.get_font(12)
        text = placeholder_font.render("\u56fe", True, (216, 227, 240))
        surface.blit(text, text.get_rect(center=rect.center))
