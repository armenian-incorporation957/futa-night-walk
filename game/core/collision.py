from __future__ import annotations

from game.entities.base import Entity


def circles_overlap(first: Entity, second: Entity) -> bool:
    dx = first.x - second.x
    dy = first.y - second.y
    radius = first.radius + second.radius
    return dx * dx + dy * dy <= radius * radius
