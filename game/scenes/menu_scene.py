from __future__ import annotations

import math

from game.core.pygame_support import require_pygame
from game.scenes.base_scene import BaseScene


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

    def __init__(self, app) -> None:
        super().__init__(app)
        self.hovered_button: str | None = None
        self.pressed_button: str | None = None
        self.show_help = False
        self.help_tab = "controls"
        self.animation_time = 0.0

    def start_run(self, game_mode: str) -> None:
        self.request_scene_change("run", game_mode=game_mode)

    def update(self, dt: float) -> None:
        self.animation_time += dt

    def handle_event(self, event) -> None:
        pygame = require_pygame()
        if event.type == pygame.MOUSEMOTION:
            self._update_hovered(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._update_hovered(event.pos)
            self.pressed_button = self.hovered_button
            if self.show_help:
                if self._help_close_rect().collidepoint(event.pos):
                    self.show_help = False
                    self.pressed_button = None
                else:
                    for tab_id in self.HELP_TABS:
                        if self._help_tab_rect(tab_id).collidepoint(event.pos):
                            self.help_tab = tab_id
                            self.pressed_button = None
                            break
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._update_hovered(event.pos)
            if self.pressed_button and self.pressed_button == self.hovered_button:
                self._activate_button(self.pressed_button)
            self.pressed_button = None
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.show_help = False

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
        config = self.app.config
        resources = self.app.resources
        overlay = pygame.Surface((config.width, config.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        panel_rect = pygame.Rect(config.width // 2 - 280, config.height // 2 - 185, 560, 370)
        pygame.draw.rect(surface, (22, 29, 39), panel_rect, border_radius=22)
        pygame.draw.rect(surface, (126, 158, 208), panel_rect, width=2, border_radius=22)

        title_font = resources.get_font(28)
        body_font = resources.get_font(20)
        small_font = resources.get_font(16)
        title = title_font.render("\u8bf4\u660e", True, (242, 231, 194))
        surface.blit(title, title.get_rect(center=(config.width // 2, panel_rect.y + 34)))

        for index, (tab_id, label) in enumerate(self.HELP_TABS.items()):
            rect = self._help_tab_rect(tab_id)
            active = self.help_tab == tab_id
            pygame.draw.rect(surface, (58, 78, 103) if active else (33, 42, 56), rect, border_radius=10)
            pygame.draw.rect(surface, (146, 172, 214), rect, 1, border_radius=10)
            tab_text = small_font.render(label, True, (237, 242, 246))
            surface.blit(tab_text, tab_text.get_rect(center=rect.center))

        lines = self._help_lines()
        for index, line in enumerate(lines):
            text = body_font.render(line, True, (223, 230, 238))
            surface.blit(text, (panel_rect.x + 34, panel_rect.y + 112 + index * 36))

        close_rect = self._help_close_rect()
        pygame.draw.rect(surface, (70, 87, 108), close_rect, border_radius=12)
        pygame.draw.rect(surface, (160, 180, 214), close_rect, width=2, border_radius=12)
        close_text = small_font.render("\u5173\u95ed", True, (240, 244, 248))
        surface.blit(close_text, close_text.get_rect(center=close_rect.center))

    def _help_lines(self) -> list[str]:
        if self.help_tab == "skills":
            return [
                "\u6bcf\u5173\u4f1a\u5206\u914d 5 \u4e2a\u672c\u5173\u53ef\u5347\u7ea7\u6280\u80fd",
                "\u6bcf\u4e2a\u6280\u80fd\u6700\u9ad8 3 \u7ea7\uff0cLv.1 \u624d\u5f00\u59cb\u751f\u6548",
                "\u5f53 5 \u4e2a\u6280\u80fd\u5168\u90e8\u5347\u6ee1 3 \u7ea7\u65f6\uff0c\u7acb\u5373\u8fdb\u5165\u4e0b\u4e00\u5173",
                "\u8fdb\u5165\u4e0b\u4e00\u5173\u540e\u751f\u547d\u56de\u590d 20\uff0c\u7ecf\u9a8c\u7b49\u7ea7\u6e05\u96f6",
                "\u65e0\u9650\u6a21\u5f0f\u4f1a\u4e0d\u65ad\u63d0\u9ad8\u5173\u5361\u96be\u5ea6",
            ]
        return [
            "\u79fb\u52a8\uff1aWASD \u6216\u65b9\u5411\u952e",
            "\u653b\u51fb\uff1a\u6280\u80fd\u4f1a\u81ea\u52a8\u91ca\u653e\uff0c\u9700\u8981\u8dd1\u4f4d\u4e0e\u8e72\u907f",
            "\u5347\u7ea7\uff1a\u5f39\u51fa\u5f3a\u5316\u9762\u677f\u540e\uff0c\u6309 1 / 2 / 3 \u9009\u62e9",
            "\u5f00\u5c40\uff1a\u6bcf\u5173\u4f1a\u5148\u9009 1 \u4e2a\u8d77\u59cb\u6280\u80fd",
            "\u8fd4\u56de\uff1a\u6e38\u620f\u4e2d\u6309 Esc \u56de\u5230\u83dc\u5355",
        ]

    def _help_tab_rect(self, tab_id: str):
        pygame = require_pygame()
        config = self.app.config
        tabs = list(self.HELP_TABS)
        index = tabs.index(tab_id)
        width = 150
        x = config.width // 2 - 170 + index * 170
        return pygame.Rect(x, config.height // 2 - 120, width, 34)

    def _help_close_rect(self):
        pygame = require_pygame()
        config = self.app.config
        return pygame.Rect(config.width // 2 - 54, config.height // 2 + 130, 108, 38)
