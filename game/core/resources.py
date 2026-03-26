from __future__ import annotations

from pathlib import Path

from game.core.pygame_support import require_pygame


class ResourceCache:
    FONT_CANDIDATES = (
        "microsoftyaheiui",
        "microsoftyahei",
        "simhei",
        "dengxian",
        "simsun",
        "nsimsun",
        "kaiti",
        "fangsong",
        "notosanscjksc",
        "sourcehansanssc",
        "wenquanyizenhei",
        "arialunicodeMS",
    )

    def __init__(self) -> None:
        self._fonts: dict[int, object] = {}
        self._images: dict[str, object | None] = {}
        self._font_path: str | None = None

    def _resolve_font_path(self) -> str | None:
        if self._font_path is not None:
            return self._font_path

        pygame = require_pygame()
        for candidate in self.FONT_CANDIDATES:
            font_path = pygame.font.match_font(candidate)
            if font_path:
                self._font_path = font_path
                return self._font_path

        return None

    def get_font(self, size: int):
        pygame = require_pygame()
        if size not in self._fonts:
            self._fonts[size] = pygame.font.Font(self._resolve_font_path(), size)
        return self._fonts[size]

    def get_image(self, path: str | Path):
        normalized = str(Path(path))
        if normalized not in self._images:
            image_path = Path(normalized)
            if not image_path.exists():
                self._images[normalized] = None
            else:
                pygame = require_pygame()
                self._images[normalized] = pygame.image.load(str(image_path)).convert_alpha()
        return self._images[normalized]
