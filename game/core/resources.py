from __future__ import annotations

from game.core.pygame_support import require_pygame


class ResourceCache:
    def __init__(self) -> None:
        self._fonts: dict[int, object] = {}

    def get_font(self, size: int):
        pygame = require_pygame()
        if size not in self._fonts:
            self._fonts[size] = pygame.font.SysFont("microsoftyaheiui", size)
        return self._fonts[size]
