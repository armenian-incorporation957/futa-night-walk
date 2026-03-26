from __future__ import annotations

import math

from game.core.pygame_support import require_pygame
from game.scenes.base_scene import BaseScene


class MenuScene(BaseScene):
    BUTTON_LAYOUT = {
        "start": ("\u5f00\u59cb", -10),
        "help": ("\u8bf4\u660e", 70),
    }

    def __init__(self, app) -> None:
        super().__init__(app)
        self.hovered_button: str | None = None
        self.pressed_button: str | None = None
        self.show_help = False
        self.animation_time = 0.0

    def start_run(self) -> None:
        self.request_scene_change("run")

    def update(self, dt: float) -> None:
        self.animation_time += dt

    def handle_event(self, event) -> None:
        pygame = require_pygame()
        if event.type == pygame.MOUSEMOTION:
            self._update_hovered(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._update_hovered(event.pos)
            self.pressed_button = self.hovered_button
            if self.show_help and self._help_close_rect().collidepoint(event.pos):
                self.show_help = False
                self.pressed_button = None
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._update_hovered(event.pos)
            if self.pressed_button and self.pressed_button == self.hovered_button:
                self._activate_button(self.pressed_button)
            self.pressed_button = None
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.show_help = False

    def render(self, surface) -> None:
        pygame = require_pygame()
        config = self.app.config
        resources = self.app.resources

        self._draw_background(surface)

        title_font = resources.get_font(56)
        subtitle_font = resources.get_font(22)
        title = title_font.render("\u7b26\u5854\u591c\u884c", True, (244, 232, 191))
        subtitle = subtitle_font.render(
            "\u591c\u96fe\u7b26\u5854\u4e2d\uff0c\u5b88\u4f4f\u4f60\u7684\u8282\u594f",
            True,
            (214, 223, 235),
        )

        surface.blit(title, title.get_rect(center=(config.width // 2, 130)))
        surface.blit(subtitle, subtitle.get_rect(center=(config.width // 2, 182)))

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

        footer_font = resources.get_font(18)
        footer = footer_font.render(
            "\u9f20\u6807\u70b9\u51fb\u6309\u94ae\u64cd\u4f5c",
            True,
            (170, 184, 201),
        )
        surface.blit(footer, footer.get_rect(center=(config.width // 2, config.height - 52)))

        if self.show_help:
            self._draw_help_popup(surface)

    def _activate_button(self, button_id: str) -> None:
        if button_id == "start":
            self.start_run()
        elif button_id == "help":
            self.show_help = not self.show_help

    def _update_hovered(self, mouse_pos: tuple[int, int]) -> None:
        self.hovered_button = None
        for button_id, (_, offset_y) in self.BUTTON_LAYOUT.items():
            if self._button_rect(offset_y).collidepoint(mouse_pos):
                self.hovered_button = button_id
                break

    def _button_rect(
        self,
        offset_y: int,
        hovered: bool = False,
        pressed: bool = False,
    ):
        pygame = require_pygame()
        config = self.app.config
        base_width = 220
        base_height = 60
        pulse = 1.0 + (0.03 if hovered else 0.0) + math.sin(self.animation_time * 4.0) * (0.02 if hovered else 0.0)
        width = int(base_width * pulse)
        height = int(base_height * pulse)
        center_x = config.width // 2
        center_y = config.height // 2 + offset_y + (4 if pressed else 0)
        return pygame.Rect(center_x - width // 2, center_y - height // 2, width, height)

    def _draw_button(self, surface, label: str, rect, hovered: bool, pressed: bool) -> None:
        pygame = require_pygame()
        font = self.app.resources.get_font(26)
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

        pygame.draw.circle(surface, (30, 46, 69), (width // 2, 120), 150)
        pygame.draw.circle(surface, (20, 33, 49), (width // 2 + 220, height - 40), 180)

    def _draw_help_popup(self, surface) -> None:
        pygame = require_pygame()
        config = self.app.config
        resources = self.app.resources
        overlay = pygame.Surface((config.width, config.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 155))
        surface.blit(overlay, (0, 0))

        panel_rect = pygame.Rect(config.width // 2 - 250, config.height // 2 - 165, 500, 330)
        pygame.draw.rect(surface, (22, 29, 39), panel_rect, border_radius=22)
        pygame.draw.rect(surface, (126, 158, 208), panel_rect, width=2, border_radius=22)

        title_font = resources.get_font(28)
        body_font = resources.get_font(20)
        close_font = resources.get_font(16)
        title = title_font.render("\u8bf4\u660e", True, (242, 231, 194))
        surface.blit(title, title.get_rect(center=(config.width // 2, panel_rect.y + 42)))

        lines = [
            "\u79fb\u52a8\uff1aWASD \u6216\u65b9\u5411\u952e",
            "\u653b\u51fb\uff1a\u6280\u80fd\u4f1a\u81ea\u52a8\u91ca\u653e\uff0c\u9760\u8fd1\u63a9\u4f53\u53ca\u8dd1\u4f4d\u751f\u5b58",
            "\u5347\u7ea7\uff1a\u51fa\u73b0\u4e09\u9009\u4e00\u65f6\uff0c\u6309 1 / 2 / 3 \u9009\u62e9\u65b0\u7b26\u5370",
            "\u62fe\u53d6\uff1a\u9760\u8fd1\u6389\u843d\u7269\u540e\u4f1a\u81ea\u52a8\u5438\u53d6",
            "\u9000\u51fa\uff1a\u6e38\u620f\u4e2d\u6309 Esc \u8fd4\u56de\u83dc\u5355",
        ]
        for index, line in enumerate(lines):
            text = body_font.render(line, True, (223, 230, 238))
            surface.blit(text, (panel_rect.x + 32, panel_rect.y + 90 + index * 38))

        close_rect = self._help_close_rect()
        pygame.draw.rect(surface, (70, 87, 108), close_rect, border_radius=12)
        pygame.draw.rect(surface, (160, 180, 214), close_rect, width=2, border_radius=12)
        close_text = close_font.render("\u5173\u95ed", True, (240, 244, 248))
        surface.blit(close_text, close_text.get_rect(center=close_rect.center))

    def _help_close_rect(self):
        pygame = require_pygame()
        config = self.app.config
        return pygame.Rect(config.width // 2 - 54, config.height // 2 + 115, 108, 38)
