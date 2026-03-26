from __future__ import annotations

from pathlib import Path

from game.content.enemies_loader import load_enemies
from game.content.skills_loader import load_skills
from game.content.waves_loader import load_waves
from game.core.config import GameConfig
from game.core.input import InputState
from game.core.pygame_support import require_pygame
from game.core.resources import ResourceCache
from game.scenes.game_over_scene import GameOverScene
from game.scenes.menu_scene import MenuScene
from game.scenes.run_scene import RunScene


class GameApp:
    def __init__(self, config: GameConfig | None = None) -> None:
        pygame = require_pygame()
        pygame.init()

        self.config = config or GameConfig()
        self.screen = pygame.display.set_mode((self.config.width, self.config.height))
        self.clock = pygame.time.Clock()
        self.resources = ResourceCache()
        self.input_state = InputState()
        self.running = True

        pygame.display.set_caption(self.config.title)

        data_dir = Path(self.config.data_dir)
        self.enemy_defs = load_enemies(data_dir / "enemies.json")
        self.skill_defs = load_skills(data_dir / "skills.json")
        self.waves = load_waves(data_dir / "waves.json")

        self.current_scene = None
        self.change_scene("menu")

    def change_scene(self, scene_name: str, **kwargs: object) -> None:
        scene_map = {
            "menu": MenuScene,
            "run": RunScene,
            "game_over": GameOverScene,
        }
        try:
            scene_cls = scene_map[scene_name]
        except KeyError as exc:
            raise ValueError(f"Unknown scene '{scene_name}'") from exc

        self.current_scene = scene_cls(self, **kwargs)

    def run(self) -> None:
        pygame = require_pygame()

        while self.running:
            dt = self.clock.tick(self.config.target_fps) / 1000.0
            self.input_state.poll()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.current_scene.handle_event(event)

            self.current_scene.update(dt)
            if self.current_scene.next_scene_name:
                next_name = self.current_scene.next_scene_name
                next_kwargs = dict(self.current_scene.next_scene_kwargs)
                self.change_scene(next_name, **next_kwargs)
                continue

            self.current_scene.render(self.screen)
            pygame.display.flip()

        pygame.quit()
