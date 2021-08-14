from rich.align import Align
from rich.console import RenderableType
from rich.panel import Panel

from textual import events
from textual.reactive import Reactive
from textual.widget import Widget

class LyricView(Widget):
    """
    View for displaying lyrics.
    """
    current_display_line: Reactive[int] = Reactive(0)
    mouse_over: Reactive[bool] = Reactive(False)
    lyric = [
        "今日はもう 引き返そうかな",
        "明日は もっといけるかな",
        "軋む",
        "",
        "見つけたい遠く 嬉しいを多く",
        "キラリ光るホーク 動く、動く",
        "とりとめないトーク どこまでも続く",
        "さよならさあ孤独 動く、動く",
        "",
        "難解なパズルを解くように",
        "きっと何回も 知りたいを知るから"
    ]

    async def on_mount(self, event: events.Mount) -> None:
        self.set_interval(1, callback=self.update)

    def render(self) -> RenderableType:
        display_height = self.console.height - 2
        offset = (display_height - 1) // 2
        start_display_lyric_line = max(0, self.current_display_line - offset)
        display_lyric = ["" for x in range(max(0, offset-self.current_display_line))] \
            + self.lyric[start_display_lyric_line:start_display_lyric_line + display_height]
        
        return Panel(
                Align.left(
                    '\n'.join(display_lyric), style=("on dark_green" if self.mouse_over else ""),
                    vertical="top"
                ),
                title="歌詞"
                )


    async def on_enter(self, event: events.Enter) -> None:
        self.mouse_over = True

    async def on_leave(self, event: events.Leave) -> None:
        self.mouse_over = False

    def update(self) -> None:
        self.current_display_line = sorted((0, self.current_display_line + 1, len(self.lyric)))[1]
