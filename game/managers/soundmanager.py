from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Dict, Set

import pygame

LOGGER = logging.getLogger(__name__)


class SoundManager:
    def __init__(self, sound_dir: str | Path):
        self.sound_dir = str(sound_dir)
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.sound_on = True
        self._missing_sounds: Set[str] = set()

    def load_sound(self, name: str, filename: str) -> None:
        path = os.path.join(self.sound_dir, filename)
        try:
            sound = pygame.mixer.Sound(path)
        except pygame.error as exc:
            LOGGER.warning(
                "Failed to load sound '%s' from '%s': %s", name, path, exc
            )
            self._missing_sounds.add(name)
            return

        self.sounds[name] = sound
        if name in self._missing_sounds:
            self._missing_sounds.remove(name)

    def play(self, name: str) -> None:
        if not self.sound_on:
            return

        sound = self.sounds.get(name)
        if not sound:
            self._warn_missing_sound(name)
            return

        channel = pygame.mixer.find_channel()
        if channel:
            channel.play(sound)
        else:
            sound.play()

    def set_volume(self, name: str, volume: float) -> None:
        sound = self.sounds.get(name)
        if sound:
            sound.set_volume(volume)
        else:
            self._warn_missing_sound(name)

    def toggle_sound(self) -> None:
        self.sound_on = not self.sound_on

    def play_music(self, file_name: str, loops: int = -1) -> None:
        if not self.sound_on:
            return

        path = os.path.join(self.sound_dir, file_name)
        if not os.path.exists(path):
            self._warn_missing_sound(file_name)
            return

        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(loops=loops)
        except pygame.error as exc:
            LOGGER.warning(
                "Error loading music '%s' from '%s': %s", file_name, path, exc
            )

    def stop_music(self) -> None:
        pygame.mixer.music.stop()

    def pause_music(self) -> None:
        pygame.mixer.music.pause()

    def unpause_music(self) -> None:
        pygame.mixer.music.unpause()

    def _warn_missing_sound(self, name: str) -> None:
        if name in self._missing_sounds:
            return
        self._missing_sounds.add(name)
        LOGGER.warning("Sound '%s' is not registered", name)
