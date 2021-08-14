from textual import events
from textual.app import App
from textual.reactive import Reactive
from textual.widgets import Header, Footer, Placeholder

from widgets.LyricView import LyricView
from widgets.PlayProgressView import PlayProgressView, ProgressClick
from audioplayer.AudioPlayer import AudioPlayer

import sys

class MyApp(App):

    # How much seconds to skip when press foward/rewind
    SKIP_LENGTH = 5

    mShowBar: Reactive[bool] = Reactive(False)
    mPlayer: AudioPlayer = AudioPlayer()
    mPlayer.set_volume(0.5)

    # a list of paths to play
    mPlaylist = []

    # current playing song index in the playlist
    mCurrentPlayingSong = -1

    # views
    playerProgressView: PlayProgressView
    lyricView: LyricView

    async def on_load(self, event: events.Load) -> None:
        """
        This function is called when the App is first loaded.
        We bind shortcut keys with actions here.
        """

        await self.bind("j", "rewind", "◀◀")
        await self.bind("k", "play", "►||")
        await self.bind("l", "forward", "►►")
        await self.bind("b", "toggle_sidebar", "Toggle sidebar")
        await self.bind("q", "quit", "Quit")

        # add files from argument for playing (if there are any)
        if len(sys.argv) > 1:
            self.mPlaylist += sys.argv[1:]
        
        # if there are any songs in the playlist, we start playing the first one.
        if len(self.mPlaylist) > 0:
            self.mPlayer.load(self.mPlaylist[0])
            self.mPlayer.play_from_start()


    async def watch_mShowBar(self, showBar: bool) -> None:
        """
        A watcher function will be called when a Reactive component's value changed.
        The function has to be named watch_ReactionComponentName.
        Whether the Reactive component has to be a member variable in self is unknown.
        """
        self.mBar.animate("layout_offset_x", 0 if showBar else -40)

    async def action_toggle_sidebar(self) -> None:
        """Called when user hits b key."""
        self.mShowBar = not self.mShowBar

    async def on_mount(self, event: events.Mount) -> None:
        """Build layout here."""
        header = Header()
        footer = Footer()
        self.mLyricView = LyricView()
        self.mPlayProgressView = PlayProgressView()
        self.mBar = Placeholder(name="left")

        await self.view.dock(header, edge="top")
        await self.view.dock(footer, self.mPlayProgressView, edge="bottom")
        await self.view.dock(self.mLyricView)
        await self.view.dock(self.mBar, edge="left", size=40, z=1)

        self.mBar.layout_offset_x = -40
        self.set_interval(1, callback=self.update_audio_view)
        self.set_interval(0.1, callback=self.check_music_end)
        

    def update_audio_view(self):
        self.mPlayProgressView.update_playback_information(self.mPlayer)
    
    def check_music_end(self):
        """
        Check whether the music has ended.
        TODO: Should I should wrap music player in a view so we can leverage
        the events and set_interval callbacks by textual?
        """
        if self.mPlayer.is_loaded() and not self.mPlayer.is_paused() and not self.mPlayer.is_busy():
            self.next_song()

    async def message_progress_click(self, event: ProgressClick) -> None:
        """A message sent by the PlayProgress when we click on the progress bar."""
        seekTime = event.value * self.mPlayer.get_length()
        self.mPlayer.set_pos(seekTime)
        self.mPlayProgressView.update_playback_information(self.mPlayer)

    async def action_rewind(self) -> None:
        """An action bound to app that gets called when when we press j key."""
        seekTime = max(0, self.mPlayer.get_pos() - self.SKIP_LENGTH)
        self.mPlayer.set_pos(seekTime)
        self.mPlayProgressView.update_playback_information(self.mPlayer)

    async def action_forward(self) -> None:
        """An action bound to app that gets called when when we press l key."""
        seekTime = min(self.mPlayer.get_length(), self.mPlayer.get_pos() + self.SKIP_LENGTH)
        self.mPlayer.set_pos(seekTime)
        self.mPlayProgressView.update_playback_information(self.mPlayer)

    async def action_play(self) -> None:
        if self.mPlayer.is_playing():
            self.mPlayer.pause()
        else:
            self.mPlayer.unpause()

    async def action_next_song(self) -> None:
        self.next_song()

    def next_song(self) -> None:
        # TODO: There is some problem with this function; it just replay the same song.
        nextIndex = self.mCurrentPlayingSong + 1
        if nextIndex < len(self.mPlaylist):
            self.mPlayer.load(self.mPlaylist[nextIndex])
            self.mPlayer.play_from_start()
            self.mCurrentPlayingSong = nextIndex


MyApp.run(title="鮑伯音樂", log="textual.log")
