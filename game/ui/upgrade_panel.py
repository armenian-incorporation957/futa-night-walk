from __future__ import annotations

from game.core.pygame_support import require_pygame
from game.ui.skill_views import build_upgrade_delta_view


class UpgradePanel:
    def draw(self, surface, app, run_state) -> None:
        pygame = require_pygame()
        config = app.config
        title_font = app.resources.get_font(24)
        name_font = app.resources.get_font(18)
        body_font = app.resources.get_font(15)
        note_font = app.resources.get_font(16)

        overlay = pygame.Surface((config.width, config.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 156))
        surface.blit(overlay, (0, 0))

        count = len(run_state.pending_upgrade_choices)
        cards = self._card_layout(config.width, count)

        if run_state.stage_state == "starter_select":
            title_label = "\u9009\u62e9\u8d77\u59cb\u6280\u80fd"
            hint_label = "\u6309 1 / 2 / 3 / 4 / 5 \u9009\u62e9\uff0c\u53ea\u6709\u9009\u4e2d\u540e\u624d\u4f1a\u89e3\u9501"
        else:
            title_label = "\u9009\u62e9\u5f3a\u5316"
            hint_label = "\u6309 1 / 2 / 3 \u9009\u62e9\uff0c\u6bcf\u5f20\u5361\u7247\u663e\u793a\u672c\u6b21\u5347\u7ea7\u53d8\u5316"

        title = title_font.render(title_label, True, (242, 231, 194))
        surface.blit(title, title.get_rect(center=(config.width // 2, 38)))

        for index, skill_id in enumerate(run_state.pending_upgrade_choices):
            rect = cards[index]
            skill = app.skill_defs[skill_id]
            current_level = run_state.stage_skill_levels.get(skill_id, 0)
            detail = build_upgrade_delta_view(skill, current_level)

            pygame.draw.rect(surface, (28, 34, 44), rect, border_radius=18)
            pygame.draw.rect(surface, (110, 140, 180), rect, 2, border_radius=18)
            badge_rect = pygame.Rect(rect.x + 10, rect.y + 10, 30, 24)
            pygame.draw.rect(surface, (78, 98, 128), badge_rect, border_radius=10)
            badge = body_font.render(str(index + 1), True, (242, 246, 250))
            surface.blit(badge, badge.get_rect(center=badge_rect.center))

            icon_rect = pygame.Rect(rect.centerx - 24, rect.y + 14, 48, 48)
            self._draw_icon(surface, app, detail.icon_path, icon_rect)

            name_text = name_font.render(
                f"{detail.name}  Lv.{detail.from_level} -> Lv.{detail.to_level}",
                True,
                (236, 241, 247),
            )
            surface.blit(name_text, name_text.get_rect(center=(rect.centerx, rect.y + 76)))

            summary_lines = self._wrap_text(detail.summary_line, body_font, rect.width - 28)
            line_y = rect.y + 96
            for line in summary_lines[:2]:
                text = body_font.render(line, True, (198, 209, 222))
                surface.blit(text, text.get_rect(center=(rect.centerx, line_y)))
                line_y += 16

            for change_line in detail.change_lines[:4]:
                wrapped = self._wrap_text(change_line, body_font, rect.width - 34)
                for line in wrapped[:2]:
                    text = body_font.render(line, True, (172, 187, 204))
                    surface.blit(text, (rect.x + 18, line_y))
                    line_y += 16
                if line_y > rect.bottom - 22:
                    break

        hint = note_font.render(hint_label, True, (174, 184, 202))
        surface.blit(hint, hint.get_rect(center=(config.width // 2, config.height - 22)))

    def _card_layout(self, screen_width: int, count: int):
        pygame = require_pygame()
        if count <= 3:
            width = 250
            height = 208
            gap = 22
            total = width * count + gap * max(0, count - 1)
            start_x = (screen_width - total) // 2
            y = 145
            return [pygame.Rect(start_x + index * (width + gap), y, width, height) for index in range(count)]

        width = 236
        height = 142
        gap = 16
        total_top = width * 3 + gap * 2
        start_top = (screen_width - total_top) // 2
        top_row = [pygame.Rect(start_top + index * (width + gap), 96, width, height) for index in range(3)]
        total_bottom = width * 2 + gap
        start_bottom = (screen_width - total_bottom) // 2
        bottom_row = [pygame.Rect(start_bottom + index * (width + gap), 256, width, height) for index in range(2)]
        return top_row + bottom_row

    def _draw_icon(self, surface, app, icon_path, rect) -> None:
        pygame = require_pygame()
        pygame.draw.rect(surface, (43, 55, 72), rect, border_radius=12)
        pygame.draw.rect(surface, (103, 128, 168), rect, 2, border_radius=12)
        image = app.resources.get_image(icon_path) if icon_path else None
        if image is not None:
            scaled = pygame.transform.smoothscale(image, (rect.width - 8, rect.height - 8))
            surface.blit(scaled, scaled.get_rect(center=rect.center))
            return

        placeholder_font = app.resources.get_font(14)
        text = placeholder_font.render("\u56fe\u6807", True, (216, 227, 240))
        surface.blit(text, text.get_rect(center=rect.center))

    def _wrap_text(self, text: str, font, max_width: int) -> list[str]:
        wrapped: list[str] = []
        current = ""
        for char in text:
            candidate = current + char
            if current and font.size(candidate)[0] > max_width:
                wrapped.append(current)
                current = char
            else:
                current = candidate
        if current:
            wrapped.append(current)
        return wrapped
