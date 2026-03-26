from __future__ import annotations

import math

from game.core.pygame_support import require_pygame
from game.scenes.base_scene import BaseScene
from game.ui.skill_views import GROUP_LABELS, build_skill_detail_view


class MenuScene(BaseScene):
    BUTTON_LAYOUT = {
        "campaign": ("\u95ef\u5173\u6a21\u5f0f", -50),
        "endless": ("\u65e0\u9650\u6a21\u5f0f", 20),
        "help": ("\u8bf4\u660e", 90),
    }

    HELP_TABS = {
        "controls": "\u64cd\u4f5c\u8bf4\u660e",
        "skills": "\u6280\u80fd\u8bf4\u660e",
    }

    SKILL_GROUPS = ("straight", "control", "burst", "defense")

    def __init__(self, app) -> None:
        super().__init__(app)
        self.hovered_button: str | None = None
        self.pressed_button: str | None = None
        self.show_help = False
        self.help_tab = "controls"
        self.selected_help_group = self.SKILL_GROUPS[0]
        self.selected_help_skill_id: str | None = None
        self.animation_time = 0.0
        self._ensure_help_selection()

    def start_run(self, game_mode: str) -> None:
        self.request_scene_change("run", game_mode=game_mode)

    def update(self, dt: float) -> None:
        self.animation_time += dt

    def handle_event(self, event) -> None:
        pygame = require_pygame()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.show_help = False
            self.pressed_button = None
            return

        if self.show_help:
            if event.type == pygame.MOUSEMOTION:
                self.hovered_button = None
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self._handle_help_click(event.pos)
            return

        if event.type == pygame.MOUSEMOTION:
            self._update_hovered(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._update_hovered(event.pos)
            self.pressed_button = self.hovered_button
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._update_hovered(event.pos)
            if self.pressed_button and self.pressed_button == self.hovered_button:
                self._activate_button(self.pressed_button)
            self.pressed_button = None

    def render(self, surface) -> None:
        config = self.app.config
        resources = self.app.resources

        self._draw_background(surface)

        title_font = resources.get_font(56)
        subtitle_font = resources.get_font(22)
        title = title_font.render("\u7b26\u5854\u591c\u884c", True, (244, 232, 191))
        subtitle = subtitle_font.render(
            "\u591a\u5173\u5361\u6210\u957f\u5236\u8089\u9e3d  |  \u95ef\u5173\u4e0e\u65e0\u9650\u4e24\u79cd\u6a21\u5f0f",
            True,
            (214, 223, 235),
        )

        surface.blit(title, title.get_rect(center=(config.width // 2 - 140, 112)))
        surface.blit(subtitle, subtitle.get_rect(center=(config.width // 2 - 140, 164)))

        for button_id, (label, offset_y) in self.BUTTON_LAYOUT.items():
            hovered = self.hovered_button == button_id
            pressed = self.pressed_button == button_id
            self._draw_button(
                surface,
                label,
                self._button_rect(offset_y, hovered, pressed),
                hovered=hovered,
                pressed=pressed,
            )

        self._draw_leaderboard(surface)

        footer_font = resources.get_font(18)
        footer = footer_font.render(
            "\u9f20\u6807\u70b9\u51fb\u6309\u94ae\u5f00\u59cb\uff0c\u6392\u884c\u699c\u4ec5\u7edf\u8ba1\u65e0\u9650\u6a21\u5f0f",
            True,
            (170, 184, 201),
        )
        surface.blit(footer, footer.get_rect(center=(config.width // 2, config.height - 42)))

        if self.show_help:
            self._draw_help_popup(surface)

    def _activate_button(self, button_id: str) -> None:
        if button_id == "campaign":
            self.start_run("campaign")
        elif button_id == "endless":
            self.start_run("endless")
        elif button_id == "help":
            self.show_help = not self.show_help
            if self.show_help:
                self._ensure_help_selection()

    def _handle_help_click(self, pos: tuple[int, int]) -> None:
        if self._help_close_rect().collidepoint(pos):
            self.show_help = False
            return

        for tab_id in self.HELP_TABS:
            if self._help_tab_rect(tab_id).collidepoint(pos):
                self.help_tab = tab_id
                if tab_id == "skills":
                    self._ensure_help_selection()
                return

        if self.help_tab != "skills":
            return

        for group_id in self.SKILL_GROUPS:
            if self._skill_group_tab_rect(group_id).collidepoint(pos):
                self.selected_help_group = group_id
                self._ensure_help_selection(group_id)
                return

        for index, skill_id in enumerate(self._skills_for_group(self.selected_help_group)):
            if self._skill_button_rect(index).collidepoint(pos):
                self.selected_help_skill_id = skill_id
                return

    def _ensure_help_selection(self, group_id: str | None = None) -> None:
        if group_id is not None:
            self.selected_help_group = group_id
        skill_ids = self._skills_for_group(self.selected_help_group)
        if self.selected_help_skill_id not in skill_ids:
            self.selected_help_skill_id = skill_ids[0] if skill_ids else None

    def _skills_for_group(self, group_id: str) -> list[str]:
        return [skill_id for skill_id, skill in self.app.skill_defs.items() if skill.group == group_id]

    def _update_hovered(self, mouse_pos: tuple[int, int]) -> None:
        self.hovered_button = None
        for button_id, (_, offset_y) in self.BUTTON_LAYOUT.items():
            if self._button_rect(offset_y).collidepoint(mouse_pos):
                self.hovered_button = button_id
                break

    def _button_rect(self, offset_y: int, hovered: bool = False, pressed: bool = False):
        pygame = require_pygame()
        config = self.app.config
        base_width = 220
        base_height = 54
        pulse = 1.0 + (0.03 if hovered else 0.0) + math.sin(self.animation_time * 4.0) * (0.02 if hovered else 0.0)
        width = int(base_width * pulse)
        height = int(base_height * pulse)
        center_x = config.width // 2 - 150
        center_y = config.height // 2 + offset_y + (4 if pressed else 0)
        return pygame.Rect(center_x - width // 2, center_y - height // 2, width, height)

    def _draw_button(self, surface, label: str, rect, hovered: bool, pressed: bool) -> None:
        pygame = require_pygame()
        font = self.app.resources.get_font(24)
        fill_color = (47, 63, 83) if not hovered else (68, 95, 126)
        border_base = 165 + int(40 * (0.5 + 0.5 * math.sin(self.animation_time * 5.0)))
        border_color = (border_base, border_base, 235)

        shadow_rect = rect.move(0, 8 if not pressed else 4)
        pygame.draw.rect(surface, (8, 12, 20), shadow_rect, border_radius=18)
        pygame.draw.rect(surface, fill_color, rect, border_radius=18)
        pygame.draw.rect(surface, border_color, rect, width=2, border_radius=18)

        text = font.render(label, True, (244, 247, 250))
        surface.blit(text, text.get_rect(center=rect.center))

    def _draw_background(self, surface) -> None:
        pygame = require_pygame()
        width, height = self.app.config.width, self.app.config.height
        top_color = (18, 26, 39)
        bottom_color = (8, 13, 21)
        for y in range(height):
            blend = y / max(height - 1, 1)
            color = tuple(
                int(top_color[index] * (1.0 - blend) + bottom_color[index] * blend)
                for index in range(3)
            )
            pygame.draw.line(surface, color, (0, y), (width, y))

        pygame.draw.circle(surface, (30, 46, 69), (width // 2 - 160, 120), 150)
        pygame.draw.circle(surface, (20, 33, 49), (width - 110, height - 40), 180)

    def _draw_leaderboard(self, surface) -> None:
        pygame = require_pygame()
        resources = self.app.resources
        entries = self.app.leaderboard.load()
        panel_rect = pygame.Rect(self.app.config.width - 290, 86, 250, 268)
        pygame.draw.rect(surface, (20, 27, 36), panel_rect, border_radius=20)
        pygame.draw.rect(surface, (110, 140, 180), panel_rect, 2, border_radius=20)

        title_font = resources.get_font(24)
        body_font = resources.get_font(18)
        note_font = resources.get_font(16)
        title = title_font.render("\u65e0\u9650\u6392\u884c\u699c", True, (242, 231, 194))
        surface.blit(title, title.get_rect(center=(panel_rect.centerx, panel_rect.y + 30)))

        if not entries:
            empty = note_font.render("\u6682\u65e0\u8bb0\u5f55", True, (180, 191, 204))
            surface.blit(empty, empty.get_rect(center=panel_rect.center))
            return

        for index, entry in enumerate(entries[:5]):
            y = panel_rect.y + 64 + index * 36
            rank = body_font.render(f"{index + 1}.", True, (233, 239, 245))
            line = note_font.render(
                f"\u5173\u5361 {entry.stage_reached}  |  {entry.survival_time_seconds}\u79d2",
                True,
                (196, 207, 219),
            )
            surface.blit(rank, (panel_rect.x + 18, y))
            surface.blit(line, (panel_rect.x + 54, y + 2))

    def _draw_help_popup(self, surface) -> None:
        pygame = require_pygame()
        panel_rect = self._help_panel_rect()
        config = self.app.config
        resources = self.app.resources
        overlay = pygame.Surface((config.width, config.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        pygame.draw.rect(surface, (22, 29, 39), panel_rect, border_radius=22)
        pygame.draw.rect(surface, (126, 158, 208), panel_rect, width=2, border_radius=22)

        title_font = resources.get_font(28)
        small_font = resources.get_font(16)
        title = title_font.render("\u8bf4\u660e", True, (242, 231, 194))
        surface.blit(title, title.get_rect(center=(config.width // 2, panel_rect.y + 32)))

        for tab_id, label in self.HELP_TABS.items():
            rect = self._help_tab_rect(tab_id)
            active = self.help_tab == tab_id
            pygame.draw.rect(surface, (58, 78, 103) if active else (33, 42, 56), rect, border_radius=10)
            pygame.draw.rect(surface, (146, 172, 214), rect, 1, border_radius=10)
            tab_text = small_font.render(label, True, (237, 242, 246))
            surface.blit(tab_text, tab_text.get_rect(center=rect.center))

        if self.help_tab == "skills":
            self._draw_skill_help(surface)
        else:
            self._draw_controls_help(surface)

        close_rect = self._help_close_rect()
        pygame.draw.rect(surface, (70, 87, 108), close_rect, border_radius=12)
        pygame.draw.rect(surface, (160, 180, 214), close_rect, width=2, border_radius=12)
        close_text = small_font.render("\u5173\u95ed", True, (240, 244, 248))
        surface.blit(close_text, close_text.get_rect(center=close_rect.center))

    def _draw_controls_help(self, surface) -> None:
        body_font = self.app.resources.get_font(20)
        panel_rect = self._help_panel_rect()
        lines = [
            "\u79fb\u52a8\uff1aWASD \u6216\u65b9\u5411\u952e",
            "\u653b\u51fb\uff1a\u6280\u80fd\u4f1a\u81ea\u52a8\u91ca\u653e\uff0c\u9700\u8981\u8dd1\u4f4d\u4e0e\u8e72\u907f",
            "\u5347\u7ea7\uff1a\u5f39\u51fa\u5f3a\u5316\u9762\u677f\u540e\uff0c\u6309 1 / 2 / 3 \u9009\u62e9",
            "\u5f00\u5c40\uff1a\u6bcf\u5173\u4f1a\u5148\u67e5\u770b\u672c\u5173 5 \u4e2a\u6280\u80fd\uff0c\u5173\u95ed\u540e\u9009\u8d77\u59cb\u6280\u80fd",
            "\u8fd4\u56de\uff1a\u6e38\u620f\u4e2d\u6309 Esc \u56de\u5230\u83dc\u5355",
        ]
        for index, line in enumerate(lines):
            text = body_font.render(line, True, (223, 230, 238))
            surface.blit(text, (panel_rect.x + 34, panel_rect.y + 112 + index * 40))

    def _draw_skill_help(self, surface) -> None:
        pygame = require_pygame()
        resources = self.app.resources
        panel_rect = self._help_panel_rect()
        body_font = resources.get_font(16)
        small_font = resources.get_font(15)
        title_font = resources.get_font(22)

        for group_id in self.SKILL_GROUPS:
            rect = self._skill_group_tab_rect(group_id)
            active = group_id == self.selected_help_group
            pygame.draw.rect(surface, (63, 86, 115) if active else (33, 42, 56), rect, border_radius=10)
            pygame.draw.rect(surface, (146, 172, 214), rect, 1, border_radius=10)
            label = body_font.render(GROUP_LABELS[group_id], True, (237, 242, 246))
            surface.blit(label, label.get_rect(center=rect.center))

        for index, skill_id in enumerate(self._skills_for_group(self.selected_help_group)):
            rect = self._skill_button_rect(index)
            active = skill_id == self.selected_help_skill_id
            pygame.draw.rect(surface, (60, 82, 110) if active else (30, 39, 52), rect, border_radius=12)
            pygame.draw.rect(surface, (122, 150, 192), rect, 1, border_radius=12)
            text = body_font.render(self.app.skill_defs[skill_id].name, True, (232, 238, 245))
            surface.blit(text, text.get_rect(center=rect.center))

        if not self.selected_help_skill_id:
            return

        detail = build_skill_detail_view(self.app.skill_defs[self.selected_help_skill_id])
        detail_rect = self._skill_detail_rect()
        pygame.draw.rect(surface, (17, 23, 31), detail_rect, border_radius=16)
        pygame.draw.rect(surface, (94, 122, 164), detail_rect, 1, border_radius=16)

        self._draw_skill_icon(surface, detail.icon_path, pygame.Rect(detail_rect.x + 22, detail_rect.y + 20, 72, 72))

        name_text = title_font.render(detail.name, True, (242, 231, 194))
        group_text = small_font.render(detail.group_label, True, (174, 191, 213))
        summary_lines = self._wrap_text(detail.summary_line, body_font, detail_rect.width - 126)
        surface.blit(name_text, (detail_rect.x + 108, detail_rect.y + 22))
        surface.blit(group_text, (detail_rect.x + 108, detail_rect.y + 50))
        for index, line in enumerate(summary_lines[:2]):
            text = small_font.render(line, True, (210, 220, 233))
            surface.blit(text, (detail_rect.x + 108, detail_rect.y + 74 + index * 18))

        info_y = detail_rect.y + 116
        for line in detail.mechanic_lines:
            text = small_font.render("\u2022 " + line, True, (196, 208, 220))
            surface.blit(text, (detail_rect.x + 24, info_y))
            info_y += 20

        level_y = info_y + 4
        for level in (1, 2, 3):
            header = small_font.render(f"Lv.{level}", True, (236, 241, 248))
            surface.blit(header, (detail_rect.x + 24, level_y))
            level_y += 18
            summary = "\u3001".join(detail.level_lines[level])
            for line in self._wrap_text(summary, small_font, detail_rect.width - 58)[:2]:
                text = small_font.render(line, True, (181, 195, 210))
                surface.blit(text, (detail_rect.x + 40, level_y))
                level_y += 18
            level_y += 6

        footer = small_font.render("\u70b9\u51fb\u5de6\u4fa7\u6280\u80fd\u6309\u94ae\u53ef\u5207\u6362\u8be6\u60c5", True, (158, 173, 190))
        surface.blit(footer, footer.get_rect(center=(detail_rect.centerx, panel_rect.bottom - 52)))

    def _draw_skill_icon(self, surface, icon_path, rect) -> None:
        pygame = require_pygame()
        pygame.draw.rect(surface, (43, 55, 72), rect, border_radius=14)
        pygame.draw.rect(surface, (103, 128, 168), rect, 2, border_radius=14)
        image = self.app.resources.get_image(icon_path) if icon_path else None
        if image is not None:
            scaled = pygame.transform.smoothscale(image, (rect.width - 10, rect.height - 10))
            surface.blit(scaled, scaled.get_rect(center=rect.center))
            return

        placeholder_font = self.app.resources.get_font(14)
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

    def _help_panel_rect(self):
        pygame = require_pygame()
        config = self.app.config
        return pygame.Rect(config.width // 2 - 370, config.height // 2 - 210, 740, 420)

    def _help_tab_rect(self, tab_id: str):
        pygame = require_pygame()
        panel_rect = self._help_panel_rect()
        tabs = list(self.HELP_TABS)
        index = tabs.index(tab_id)
        width = 150
        x = panel_rect.x + 34 + index * 170
        return pygame.Rect(x, panel_rect.y + 58, width, 34)

    def _skill_group_tab_rect(self, group_id: str):
        pygame = require_pygame()
        panel_rect = self._help_panel_rect()
        groups = list(self.SKILL_GROUPS)
        index = groups.index(group_id)
        width = 122
        gap = 12
        x = panel_rect.x + 28 + index * (width + gap)
        return pygame.Rect(x, panel_rect.y + 112, width, 34)

    def _skill_button_rect(self, index: int):
        pygame = require_pygame()
        detail_rect = self._skill_detail_rect()
        x = detail_rect.x - 178
        y = detail_rect.y + index * 52
        return pygame.Rect(x, y, 154, 42)

    def _skill_detail_rect(self):
        pygame = require_pygame()
        panel_rect = self._help_panel_rect()
        return pygame.Rect(panel_rect.x + 210, panel_rect.y + 154, 500, 200)

    def _help_close_rect(self):
        pygame = require_pygame()
        panel_rect = self._help_panel_rect()
        return pygame.Rect(panel_rect.centerx - 54, panel_rect.bottom - 44, 108, 34)
