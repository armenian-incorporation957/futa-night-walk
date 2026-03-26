from __future__ import annotations

from game.core.pygame_support import require_pygame
from game.scenes.base_scene import BaseScene


class GameOverScene(BaseScene):
    def __init__(
        self,
        app,
        score: int = 0,
        stage_reached: int = 1,
        game_mode: str = "campaign",
        victory: bool = False,
    ) -> None:
        super().__init__(app)
        self.score = score
        self.stage_reached = stage_reached
        self.game_mode = game_mode
        self.victory = victory

    def restart(self) -> None:
        self.request_scene_change("run", game_mode=self.game_mode)

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
        note_font = resources.get_font(18)

        title_label = "\u901a\u5173" if self.victory else "\u7b26\u5854\u6298\u621f"
        title_color = (205, 231, 196) if self.victory else (255, 190, 190)
        mode_label = "\u95ef\u5173\u6a21\u5f0f" if self.game_mode == "campaign" else "\u65e0\u9650\u6a21\u5f0f"

        title = title_font.render(title_label, True, title_color)
        score_text = body_font.render(f"\u575a\u6301\u65f6\u95f4: {self.score} \u79d2", True, (235, 220, 220))
        stage_text = body_font.render(f"{mode_label}  \u6700\u7ec8\u5173\u5361: {self.stage_reached}", True, (220, 224, 232))
        prompt = note_font.render("\u56de\u8f66\u91cd\u65b0\u5f00\u59cb\uff0cEsc \u8fd4\u56de\u83dc\u5355", True, (215, 205, 205))

        surface.blit(title, title.get_rect(center=(config.width // 2, config.height // 2 - 70)))
        surface.blit(score_text, score_text.get_rect(center=(config.width // 2, config.height // 2 - 12)))
        surface.blit(stage_text, stage_text.get_rect(center=(config.width // 2, config.height // 2 + 28)))
        surface.blit(prompt, prompt.get_rect(center=(config.width // 2, config.height // 2 + 78)))
