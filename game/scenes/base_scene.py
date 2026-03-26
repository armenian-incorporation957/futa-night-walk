from __future__ import annotations


class BaseScene:
    def __init__(self, app) -> None:
        self.app = app
        self.next_scene_name: str | None = None
        self.next_scene_kwargs: dict[str, object] = {}

    def request_scene_change(self, scene_name: str, **kwargs: object) -> None:
        self.next_scene_name = scene_name
        self.next_scene_kwargs = kwargs

    def handle_event(self, event) -> None:
        return None

    def update(self, dt: float) -> None:
        return None

    def render(self, surface) -> None:
        return None
