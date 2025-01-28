from config import MUSIC_DIR
from random import randrange

import pygame
import os


class Music:
    CRASH = "game_over.mp3"
    NO_FUEL = "no_fuel.mp3"
    CRYING = "crying.mp3"
    DIALOG = "dialog.mp3"

    def __init__(self, playlist: dict):
        pygame.mixer.init()
        self.paused, self.stopped = False, False
        self.index = randrange(len(playlist))
        self.playlist = {os.path.join(MUSIC_DIR, file): value
                        for file, value in playlist.items()}

    def get(self):
        file = list(self.playlist.keys())[self.index]
        return self.playlist[file]

    def play(self):
        file = list(self.playlist.keys())[self.index]
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()

    def next(self):
        self.index = (self.index + 1) % len(self.playlist)
        self.play()
        if self.paused:
            self.pause()

    def pause(self):
        self.paused = not self.paused
        if self.paused:
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()

    def stop(self):
        self.stopped = True
        pygame.mixer.music.stop()

    def dialog(self):
        self.index = (self.index - 1) % len(self.playlist)
        file = os.path.join(MUSIC_DIR, self.DIALOG)
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()

    def game_over(self, file):
        self.stop()
        file = os.path.join(MUSIC_DIR, file)
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()
