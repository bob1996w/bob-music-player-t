import math

def format_length(seconds: float) -> str:
    """Format the length in seconds to string."""
    seconds = math.floor(seconds)
    signStr = "" if seconds >= 0 else "-"
    second = seconds % 60
    minute = seconds // 60 % 60
    hour = seconds // 3600
    
    showHour = hour > 0
    hourStr = f"{hour}:" if showHour else ""
    minuteStr = f"{minute:02}:" if showHour else f"{minute}:"

    return f"{signStr}{hourStr}{minuteStr}{second:02}"