import pygame
from pygame.mixer import music
import mutagen
import time
import asyncio

class AudioPlayer():
    """
    A wrapper to pygame.mixer.music for controlling playback in the application.
    There should only be once instance of this class (because pygame).
    """

    # The position in the song last time the song has an action (play or pause) in seconds.
    mLastActionPos = 0.0

    # The timestamp of the system last time the song has start action (play) in seconds.
    mLastStartTimestamp = time.time()

    mLoaded = False

    mPaused = True

    # Current playing filename
    mFilePath: str = ""

    # Metadata
    mMetadata: mutagen.File

    def __init__(self) -> None:
        pygame.init()
        pygame.mixer.init()

    def is_loaded(self) -> bool:
        return self.mLoaded

    def load(self, fileName: str) -> None:
        print(fileName)
        self.mLastActionPos = 0
        self.mPaused = True
        self.mFilePath = fileName
        self.mMetadata = mutagen.File(fileName)
        music.unload()
        music.load(fileName)
        self.mLoaded = True

    def play_from_start(self) -> None:
        music.play(loops=0, start=0, fade_ms=0)
        self.mLastActionPos = 0
        self.mLastStartTimestamp = time.time()
        self.mPaused = False
    
    def set_pos(self, pos: float) -> None:
        music.rewind()
        self.mLastActionPos = pos
        self.mLastStartTimestamp = time.time()
        music.set_pos(pos)
    
    def get_pos(self) -> float:
        reportTime = 0.0
        if self.mPaused:
            reportTime = self.mLastActionPos
        else:
            reportTime = time.time() - self.mLastStartTimestamp + self.mLastActionPos
        return min(reportTime, self.get_length())

    def is_playing(self) -> bool:
        return not self.mPaused

    def set_volume(self, value: float) -> None:
        music.set_volume(value)

    def get_volume(self) -> float:
        return music.get_volume()

    def pause(self) -> None:
        music.pause()
        self.mLastActionPos = self.get_pos()
        self.mPaused = True

    def unpause(self) -> None:
        self.mLastStartTimestamp = time.time()
        music.unpause()
        self.mPaused = False

    def get_info(self) -> str:
        if not self.mLoaded:
            return self.mFilePath
        else:
            title = getattr(self.mMetadata, "title", [""])[0]
            artist = getattr(self.mMetadata, "artist", [""])[0]
            if title and artist:
                return f"{title} - {artist}"
            elif title:
                return f"{title}"
            else:
                return self.mFilePath
    
    def get_length(self) -> float:
        if not self.mLoaded:
            return 0
        else:
            return self.mMetadata.info.length
    
    def is_busy(self) -> bool:
        """Check if the pygame module is still busy playing the music."""
        return music.get_busy()
    
    def is_paused(self) -> bool:
        return self.mPaused
