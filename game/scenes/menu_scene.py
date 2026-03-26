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

        title = title_font.render("\u7b26\u5854\u591c\u884c", True, (239, 226, 185))
        prompt = body_font.render(
            "\u6309 Enter \u5f00\u59cb\uff0cWASD \u79fb\u52a8\uff0c\u6570\u5b57\u952e\u9009\u62e9\u7b26\u5370",
            True,
            (210, 220, 232),
        )

        surface.blit(title, title.get_rect(center=(config.width // 2, config.height // 2 - 40)))
        surface.blit(prompt, prompt.get_rect(center=(config.width // 2, config.height // 2 + 16)))
