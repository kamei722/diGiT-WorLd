from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Iterable, Tuple

import pygame

if __package__ in (None, ""):
    # スクリプト実行時でもパッケージインポートが通るようにパスを補正する
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from game.game_utils import FPS, SCREEN_HEIGHT, SCREEN_WIDTH, resource_path  # type: ignore
    from game.managers.soundmanager import SoundManager  # type: ignore
    from game.scenes.title_scene import TitleScene  # type: ignore
else:
    from .game_utils import FPS, SCREEN_HEIGHT, SCREEN_WIDTH, resource_path
    from .managers.soundmanager import SoundManager
    from .scenes.title_scene import TitleScene

LOGGER = logging.getLogger(__name__)

SoundSetting = Tuple[str, float]


def _load_splash_image(splash_size: Tuple[int, int]) -> pygame.Surface | None:
    splash_path = resource_path("assets/pics/splash.png")
    try:
        image = pygame.image.load(splash_path).convert()
        return pygame.transform.scale(image, splash_size)
    except pygame.error as exc:
        LOGGER.warning("Failed to load splash image '%s': %s", splash_path, exc)
        return None


def _draw_loading_screen(
    screen: pygame.Surface,
    splash_image: pygame.Surface | None,
    font: pygame.font.Font,
    current: int,
    total: int,
) -> None:
    if splash_image:
        screen.blit(splash_image, (0, 0))
    else:
        screen.fill((0, 0, 0))

    progress_text = font.render(f"Loading {current}/{total}", True, (255, 255, 255))
    text_rect = progress_text.get_rect(
        center=(screen.get_width() // 2, screen.get_height() - 30)
    )
    screen.blit(progress_text, text_rect)
    pygame.display.flip()


def _load_sounds(
    sound_manager: SoundManager,
    settings: Iterable[Tuple[str, SoundSetting]],
    splash_screen: pygame.Surface,
    splash_image: pygame.Surface | None,
) -> None:
    font = pygame.font.Font(None, 24)
    clock = pygame.time.Clock()
    settings_list = list(settings)
    total = len(settings_list)

    for index, (name, (filename, volume)) in enumerate(settings_list, start=1):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        sound_manager.load_sound(name, filename)
        sound_manager.set_volume(name, volume)

        _draw_loading_screen(splash_screen, splash_image, font, index, total)
        clock.tick(60)


def main() -> None:
    logging.basicConfig(level=logging.INFO)

    pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=256)
    pygame.init()
    pygame.mixer.init()
    pygame.font.init()

    splash_size = (200, 200)
    splash_screen = pygame.display.set_mode(splash_size)
    pygame.display.set_caption("Loading...")

    splash_image = _load_splash_image(splash_size)
    if splash_image is None:
        splash_screen.fill((0, 0, 0))
        pygame.display.flip()
    else:
        splash_screen.blit(splash_image, (0, 0))
        pygame.display.flip()

    sound_dir = Path(resource_path("assets/sound"))
    sound_manager = SoundManager(str(sound_dir))

    sound_settings = [
        ("jump", ("jump.mp3", 0.05)),
        ("hit", ("hit.mp3", 0.0)),
        ("pickup", ("pickup.mp3", 0.02)),
        ("stage_clear", ("stage_clear.mp3", 0.01)),
        ("enemy_spawn", ("enemy_spawn.mp3", 0.1)),
        ("miss", ("miss.mp3", 0.02)),
        ("pi", ("pi.mp3", 0.1)),
        ("speed_up", ("speed.mp3", 0.1)),
        ("loop_reset", ("loop_reset.mp3", 0.1)),
        ("key_spawn", ("key_spawn.mp3", 0.05)),
        ("select", ("select.mp3", 0.1)),
        ("stage_in", ("stage_in.mp3", 0.1)),
        ("unmove", ("unmove.mp3", 0.1)),
        ("ex_open", ("ex_open.mp3", 0.1)),
        ("title_in", ("title_in.mp3", 0.1)),
        ("spawn_one", ("spawn_one.mp3", 0.02)),
    ]
    _load_sounds(sound_manager, sound_settings, splash_screen, splash_image)

    os.environ["SDL_VIDEO_CENTERED"] = "1"
    game_screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("dIGIT WorLd")
    clock = pygame.time.Clock()

    current_scene = TitleScene(game_screen, sound_manager)

    while current_scene.is_running:
        dt = clock.tick(FPS) / 1000.0

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        current_scene.handle_events(events)
        current_scene.update(dt)
        current_scene.draw()
        pygame.display.flip()

        if current_scene.next_scene:
            current_scene.cleanup()
            current_scene = current_scene.next_scene

    pygame.quit()


if __name__ == "__main__":
    main()
