from __future__ import annotations

import math

from game.core.pygame_support import require_pygame
from game.scenes.base_scene import BaseScene
from game.ui.skill_views import GROUP_LABELS, build_skill_detail_layout, build_skill_icon_surface


class MenuScene(BaseScene):
    BUTTON_OFFSETS = {
        "campaign": -50,
        "endless": 20,
        "help": 90,
        "display": 160,
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
        self.skill_detail_scroll = 0
        self.skill_detail_content_height = 0
        self.last_mouse_pos = (0, 0)
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
                self.last_mouse_pos = event.pos
                self.hovered_button = None
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.last_mouse_pos = event.pos
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.last_mouse_pos = event.pos
                self._handle_help_click(event.pos)
            elif event.type == pygame.MOUSEWHEEL:
                self._handle_help_scroll(event.y)
            return

        if event.type == pygame.MOUSEMOTION:
            self.last_mouse_pos = event.pos
            self._update_hovered(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.last_mouse_pos = event.pos
            self._update_hovered(event.pos)
            self.pressed_button = self.hovered_button
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.last_mouse_pos = event.pos
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

        for button_id, offset_y in self.BUTTON_OFFSETS.items():
            hovered = self.hovered_button == button_id
            pressed = self.pressed_button == button_id
            self._draw_button(
                surface,
                self._button_label(button_id),
                self._button_rect(offset_y, hovered, pressed),
                hovered=hovered,
                pressed=pressed,
            )

        self._draw_leaderboard(surface)

        footer_font = resources.get_font(18)
        footer = footer_font.render(
            "\u9f20\u6807\u70b9\u51fb\u6309\u94ae\u5f00\u59cb\uff0c\u8bf4\u660e\u9875\u53ef\u7528\u6eda\u8f6e\u67e5\u770b\u6280\u80fd\u8be6\u60c5",
            True,
            (170, 184, 201),
        )
        surface.blit(footer, footer.get_rect(center=(config.width // 2, config.height - 42)))

        if self.show_help:
            self._draw_help_popup(surface)

    def _button_label(self, button_id: str) -> str:
        if button_id == "campaign":
            return "\u95ef\u5173\u6a21\u5f0f"
        if button_id == "endless":
            return "\u65e0\u9650\u6a21\u5f0f"
        if button_id == "help":
            return "\u8bf4\u660e"
        return "\u5168\u5c4f\u6a21\u5f0f" if not self.app.is_fullscreen else "\u7a97\u53e3\u6a21\u5f0f"

    def _activate_button(self, button_id: str) -> None:
        if button_id == "campaign":
            self.start_run("campaign")
        elif button_id == "endless":
            self.start_run("endless")
        elif button_id == "help":
            self.show_help = not self.show_help
            if self.show_help:
                self._ensure_help_selection()
        elif button_id == "display":
            self.app.toggle_fullscreen()

    def _handle_help_click(self, pos: tuple[int, int]) -> None:
        if self._help_close_rect().collidepoint(pos):
            self.show_help = False
            return

        for tab_id in self.HELP_TABS:
            if self._help_tab_rect(tab_id).collidepoint(pos):
                self.help_tab = tab_id
                self.skill_detail_scroll = 0
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
                self.skill_detail_scroll = 0
                return

    def _handle_help_scroll(self, delta_y: int) -> None:
        if self.help_tab != "skills":
            return
        detail_rect = self._skill_detail_rect()
        if not detail_rect.collidepoint(self.last_mouse_pos):
            return
        visible_height = detail_rect.height - 20
        max_scroll = max(0, self.skill_detail_content_height - visible_height)
        if max_scroll <= 0:
            self.skill_detail_scroll = 0
            return
        self.skill_detail_scroll = min(max(0, self.skill_detail_scroll - delta_y * 28), max_scroll)

    def _ensure_help_selection(self, group_id: str | None = None) -> None:
        if group_id is not None:
            self.selected_help_group = group_id
        skill_ids = self._skills_for_group(self.selected_help_group)
        if self.selected_help_skill_id not in skill_ids:
            self.selected_help_skill_id = skill_ids[0] if skill_ids else None
        self.skill_detail_scroll = 0

    def _skills_for_group(self, group_id: str) -> list[str]:
        return [skill_id for skill_id, skill in self.app.skill_defs.items() if skill.group == group_id]

    def _update_hovered(self, mouse_pos: tuple[int, int]) -> None:
        self.hovered_button = None
        for button_id, offset_y in self.BUTTON_OFFSETS.items():
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
            "\u663e\u793a\uff1a\u4e3b\u83dc\u5355\u53ef\u4ee5\u5728\u7a97\u53e3\u4e0e\u5168\u5c4f\u95f4\u5207\u6362",
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
            icon_rect = pygame.Rect(rect.x + 6, rect.y + 5, 30, 30)
            icon = build_skill_icon_surface(self.app.skill_defs[skill_id], 24, self.app.resources)
            surface.blit(icon, icon.get_rect(center=icon_rect.center))
            text = body_font.render(self.app.skill_defs[skill_id].name, True, (232, 238, 245))
            surface.blit(text, (rect.x + 42, rect.y + 12))

        if not self.selected_help_skill_id:
            return

        skill = self.app.skill_defs[self.selected_help_skill_id]
        layout = build_skill_detail_layout(skill, self._skill_detail_rect().width - 20, self.app.resources)
        self.skill_detail_content_height = layout.content_height
        detail_rect = self._skill_detail_rect()
        pygame.draw.rect(surface, (17, 23, 31), detail_rect, border_radius=16)
        pygame.draw.rect(surface, (94, 122, 164), detail_rect, 1, border_radius=16)

        viewport_rect = pygame.Rect(detail_rect.x + 10, detail_rect.y + 10, detail_rect.width - 26, detail_rect.height - 20)
        content_height = max(viewport_rect.height, layout.content_height)
        content_surface = pygame.Surface((viewport_rect.width, content_height), pygame.SRCALPHA)

        icon = build_skill_icon_surface(skill, 62, self.app.resources)
        content_surface.blit(icon, icon.get_rect(center=(54, 52)))

        name_text = title_font.render(layout.name, True, (242, 231, 194))
        group_text = small_font.render(layout.group_label, True, (174, 191, 213))
        content_surface.blit(name_text, (96, 12))
        content_surface.blit(group_text, (96, 40))

        for index, line in enumerate(layout.summary_lines):
            text = small_font.render(line, True, (210, 220, 233))
            content_surface.blit(text, (96, 64 + index * 18))

        y = 108
        for line in layout.mechanic_lines:
            text = small_font.render(line, True, (196, 208, 220))
            content_surface.blit(text, (14, y))
            y += 20

        for level, lines in layout.level_sections:
            header = small_font.render(f"Lv.{level}", True, (236, 241, 248))
            content_surface.blit(header, (14, y))
            y += 20
            for line in lines:
                text = small_font.render(line, True, (181, 195, 210))
                content_surface.blit(text, (28, y))
                y += 18
            y += 6

        clipped_surface = content_surface.subsurface(
            pygame.Rect(0, self.skill_detail_scroll, viewport_rect.width, viewport_rect.height)
        )
        surface.blit(clipped_surface, viewport_rect.topleft)
        self._draw_scrollbar(surface, viewport_rect, content_height)

        footer = small_font.render("\u9f20\u6807\u79fb\u5165\u8be6\u60c5\u533a\u540e\u53ef\u7528\u6eda\u8f6e\u67e5\u770b\u66f4\u591a\u5185\u5bb9", True, (158, 173, 190))
        surface.blit(footer, footer.get_rect(center=(detail_rect.centerx, panel_rect.bottom - 52)))

    def _draw_scrollbar(self, surface, viewport_rect, content_height: int) -> None:
        pygame = require_pygame()
        if content_height <= viewport_rect.height:
            return
        bar_rect = pygame.Rect(viewport_rect.right + 4, viewport_rect.y, 8, viewport_rect.height)
        pygame.draw.rect(surface, (35, 44, 58), bar_rect, border_radius=8)
        thumb_height = max(24, int(viewport_rect.height * viewport_rect.height / content_height))
        max_scroll = max(1, content_height - viewport_rect.height)
        thumb_y = int(bar_rect.y + (self.skill_detail_scroll / max_scroll) * (bar_rect.height - thumb_height))
        thumb_rect = pygame.Rect(bar_rect.x + 1, thumb_y, bar_rect.width - 2, thumb_height)
        pygame.draw.rect(surface, (120, 145, 182), thumb_rect, border_radius=8)

    def _help_panel_rect(self):
        pygame = require_pygame()
        config = self.app.config
        return pygame.Rect(config.width // 2 - 370, config.height // 2 - 215, 740, 430)

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
        return pygame.Rect(panel_rect.x + 210, panel_rect.y + 154, 500, 220)

    def _help_close_rect(self):
        pygame = require_pygame()
        panel_rect = self._help_panel_rect()
        return pygame.Rect(panel_rect.centerx - 54, panel_rect.bottom - 42, 108, 34)
