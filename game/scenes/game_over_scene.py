from __future__ import annotations

from game.core.pygame_support import require_pygame
from game.scenes.base_scene import BaseScene


class GameOverScene(BaseScene):
    def __init__(self, app, score: int = 0) -> None:
        super().__init__(app)
        self.score = score

    def restart(self) -> None:
        self.request_scene_change("run")

    def handle_event(self, event) -> None:
        pygame = require_pygame()
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.restart()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.request_scene_change("menu")

    def render(self, surface) -> None:
        config = self.app.config
        resources = self.app.resources
        surface.fill((19, 14, 18))

        title_font = resources.get_font(42)
        body_font = resources.get_font(24)

        title = title_font.render("\u7b26\u5854\u6298\u621f", True, (255, 190, 190))
        score_text = body_font.render(
            f"\u575a\u6301\u65f6\u95f4: {self.score} \u79d2",
            True,
            (235, 220, 220),
        )
        prompt = body_font.render(
            "\u56de\u8f66\u91cd\u5f00\uff0cEsc \u8fd4\u56de\u83dc\u5355",
            True,
            (215, 205, 205),
        )

        surface.blit(title, title.get_rect(center=(config.width // 2, config.height // 2 - 50)))
        surface.blit(score_text, score_text.get_rect(center=(config.width // 2, config.height // 2 + 4)))
        surface.blit(prompt, prompt.get_rect(center=(config.width // 2, config.height // 2 + 48)))
