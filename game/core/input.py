from __future__ import annotations

from dataclasses import dataclass

from game.core.pygame_support import require_pygame


@dataclass
class InputState:
    move_x: int = 0
    move_y: int = 0

    def poll(self) -> None:
        pygame = require_pygame()
        keys = pygame.key.get_pressed()

        self.move_x = int(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - int(
            keys[pygame.K_a] or keys[pygame.K_LEFT]
        )
        self.move_y = int(keys[pygame.K_s] or keys[pygame.K_DOWN]) - int(
            keys[pygame.K_w] or keys[pygame.K_UP]
        )
