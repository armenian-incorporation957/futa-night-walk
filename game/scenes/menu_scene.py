from __future__ import annotations

from game.core.pygame_support import require_pygame
from game.scenes.base_scene import BaseScene


class MenuScene(BaseScene):
    def start_run(self) -> None:
        self.request_scene_change("run")

    def handle_event(self, event) -> None:
        pygame = require_pygame()
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.start_run()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.start_run()

    def render(self, surface) -> None:
        config = self.app.config
        resources = self.app.resources

        surface.fill(config.background_color)
        title_font = resources.get_font(46)
        body_font = resources.get_font(24)

        title = title_font.render("符塔夜行", True, (239, 226, 185))
        prompt = body_font.render("按 Enter 开始，WASD 移动，数字键选择符印", True, (210, 220, 232))

        surface.blit(title, title.get_rect(center=(config.width // 2, config.height // 2 - 40)))
        surface.blit(prompt, prompt.get_rect(center=(config.width // 2, config.height // 2 + 16)))
