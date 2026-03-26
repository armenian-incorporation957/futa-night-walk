from __future__ import annotations

from game.core.pygame_support import require_pygame


class UpgradePanel:
    def draw(self, surface, app, run_state) -> None:
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

        if run_state.stage_state == "starter_select":
            title_label = "\u9009\u62e9\u8d77\u59cb\u6280\u80fd"
            hint_label = "\u6309 1 / 2 / 3 / 4 / 5 \u8fdb\u884c\u9009\u62e9"
        else:
            title_label = "\u9009\u62e9\u5f3a\u5316"
            hint_label = "\u6309 1 / 2 / 3 \u8fdb\u884c\u9009\u62e9"

        title = font.render(title_label, True, (242, 231, 194))
        surface.blit(title, title.get_rect(center=(config.width // 2, config.height // 2 - 122)))

        for index, skill_id in enumerate(run_state.pending_upgrade_choices):
            skill = app.skill_defs[skill_id]
            level = run_state.stage_skill_levels.get(skill_id, 0)
            next_level = min(3, level + 1)
            row_rect = pygame.Rect(panel_rect.x + 28, panel_rect.y + 72 + index * 50, panel_rect.width - 56, 42)
            pygame.draw.rect(surface, (39, 46, 59), row_rect, border_radius=14)
            pygame.draw.rect(surface, (92, 112, 146), row_rect, 1, border_radius=14)

            name_text = small_font.render(
                f"{index + 1}. {skill.name}  Lv.{level} -> Lv.{next_level}",
                True,
                (231, 238, 245),
            )
            desc_text = note_font.render(skill.description, True, (182, 194, 208))
            surface.blit(name_text, (row_rect.x + 16, row_rect.y + 5))
            surface.blit(desc_text, (row_rect.x + 16, row_rect.y + 24))

        hint = note_font.render(hint_label, True, (174, 184, 202))
        surface.blit(hint, hint.get_rect(center=(config.width // 2, panel_rect.bottom - 26)))
