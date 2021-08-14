from rich.console import RenderableType
from rich.progress_bar import ProgressBar 
from rich.text import Text

from textual import events
from textual.reactive import Reactive
from textual.widget import Widget
from textual.views import GridView

from textual.message import Message, MessageTarget

from audioplayer.AudioPlayer import AudioPlayer

from utils.format_utils import format_length

import math

# event for clicking on a progress.
class ProgressClick(Message, bubble=True):
    def __init__(self, sender: MessageTarget, value: float) -> None:
        self.value = value
        super().__init__(sender)

class PlayProgress(Widget):

    # The actual playing progress
    progress_play: Reactive[float] = Reactive(0)

    # The progress user hovers mouse
    progress_select: Reactive[float] = Reactive(0)

    is_enter: Reactive[bool] = Reactive(False)

    def __init__(self) -> None:
        super().__init__()
        self.layout_size = 1

    def render(self) -> RenderableType:
        style = "bright_red" if self.is_enter else "bright_white"
        progress = self.progress_select if self.is_enter else self.progress_play
        return ProgressBar(total=1, completed=progress, complete_style=style)

    async def on_click(self, event: events.MouseDown) -> None:
        self.progress_play = self.progress_select
        await self.emit(ProgressClick(self, self.progress_select))
        
    async def on_enter(self, event: events.Enter) -> None:
        self.is_enter = True

    async def on_leave(self, event: events.Leave) -> None:
        self.is_enter = False

    async def on_mouse_move(self, event: events.MouseMove) -> None:
        self.progress_select = self.progress = event.x / self.console.width

    def update_play_time(self, percentage: float):
        self.progress_play = percentage



class PlayTime(Widget):

    time_seconds: Reactive[float] = Reactive(0.0)

    def render(self):
        return Text(format_length(self.time_seconds), justify="left")

    def update_seconds(self, seconds: float):
        self.time_seconds = seconds


class PlayTimeEnd(Widget):

    time_seconds: Reactive[float] = Reactive(0.0)

    def render(self):
        self.layout_fraction=1
        return Text(format_length(self.time_seconds), justify="right")

    def update_seconds(self, seconds: float):
        self.time_seconds = seconds

class PlayInfo(Widget):

    info: Reactive[str] = Reactive("")

    def render(self):
        return Text(self.info, justify="center", overflow="ellipsis")

    def update_info(self, info: str):
        self.info = info


class PlayProgressView(GridView):
    async def on_mount(self, event: events.Mount) -> None:
        # There is no layout_size=wrap_content thing,
        # only layout_size=None meaning match_parent,
        # so we have to manually modify the layout_size.
        self.layout_size = 2

        self.progress_bar = PlayProgress()
        self.play_time = PlayTime()
        self.play_time_end = PlayTimeEnd()
        self.play_info = PlayInfo()

        self.grid.set_gap(2, 0)

        self.grid.add_column("col1", size=10)
        self.grid.add_column("col2", fraction=1)
        self.grid.add_column("col3", size=10)
        self.grid.add_row("row", repeat=2)
        self.grid.add_areas(
            progress_bar="col1-start|col3-end,row1",
            time_current="col1,row2",
            time_total="col3,row2",
            play_info="col2, row2"
        )

        self.grid.place(
            progress_bar=self.progress_bar,
            time_current=self.play_time,
            time_total=self.play_time_end,
            play_info=self.play_info
        )

    def update_playback_information(self, player: AudioPlayer) -> None:
        if player.is_loaded():
            songLength = player.get_length()

            self.play_time.update_seconds(player.get_pos())
            self.play_time_end.update_seconds(songLength)
            self.progress_bar.update_play_time(player.get_pos() / songLength)
            self.play_info.update_info(player.get_info())
