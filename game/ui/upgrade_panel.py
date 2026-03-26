from __future__ import annotations

from game.core.pygame_support import require_pygame


class UpgradePanel:
    def draw(self, surface, app, choices: list[str]) -> None:
        pygame = require_pygame()
        config = app.config
        font = app.resources.get_font(24)
        small_font = app.resources.get_font(20)

        panel_rect = pygame.Rect(config.width // 2 - 240, config.height // 2 - 120, 480, 240)
        overlay = pygame.Surface((config.width, config.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        pygame.draw.rect(surface, (28, 34, 44), panel_rect)
        pygame.draw.rect(surface, (110, 140, 180), panel_rect, 2)

        title = font.render("选择新的符印", True, (242, 231, 194))
        surface.blit(title, title.get_rect(center=(config.width // 2, config.height // 2 - 80)))

        for index, skill_id in enumerate(choices):
            line = small_font.render(f"{index + 1}. {skill_id}", True, (225, 233, 240))
            surface.blit(line, (panel_rect.x + 40, panel_rect.y + 80 + index * 38))
