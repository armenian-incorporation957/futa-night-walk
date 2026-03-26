from __future__ import annotations

from game.core.pygame_support import require_pygame


class UpgradePanel:
    def draw(self, surface, app, choices: list[str]) -> None:
        pygame = require_pygame()
        config = app.config
        font = app.resources.get_font(24)
        small_font = app.resources.get_font(20)
        note_font = app.resources.get_font(16)

        panel_rect = pygame.Rect(config.width // 2 - 280, config.height // 2 - 165, 560, 330)
        overlay = pygame.Surface((config.width, config.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        pygame.draw.rect(surface, (28, 34, 44), panel_rect)
        pygame.draw.rect(surface, (110, 140, 180), panel_rect, 2)

        title = font.render("\u9009\u62e9\u65b0\u7684\u7b26\u5370", True, (242, 231, 194))
        surface.blit(title, title.get_rect(center=(config.width // 2, config.height // 2 - 122)))

        for index, skill_id in enumerate(choices):
            skill = app.skill_defs[skill_id]
            row_rect = pygame.Rect(panel_rect.x + 28, panel_rect.y + 72 + index * 72, panel_rect.width - 56, 58)
            pygame.draw.rect(surface, (39, 46, 59), row_rect, border_radius=14)
            pygame.draw.rect(surface, (92, 112, 146), row_rect, 1, border_radius=14)

            name_text = small_font.render(f"{index + 1}. {skill.name}", True, (231, 238, 245))
            desc_text = note_font.render(skill.description, True, (182, 194, 208))
            surface.blit(name_text, (row_rect.x + 16, row_rect.y + 10))
            surface.blit(desc_text, (row_rect.x + 16, row_rect.y + 34))

        hint = note_font.render("\u6309 1 / 2 / 3 \u8fdb\u884c\u9009\u62e9", True, (174, 184, 202))
        surface.blit(hint, hint.get_rect(center=(config.width // 2, panel_rect.bottom - 26)))
