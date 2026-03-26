from __future__ import annotations

try:
    import pygame as _pygame
except ModuleNotFoundError:
    _pygame = None


def require_pygame():
    if _pygame is None:
        raise RuntimeError(
            "pygame is not installed. Run `python -m pip install -r requirements.txt` first."
        )
    return _pygame
