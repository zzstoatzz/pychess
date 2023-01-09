import re

from datetime import datetime

from settings import Color


def _date_from_pgn(pgn: str) -> datetime:
    """Extract the date from a PGN."""

    date_str = re.findall(r"""\[Date\s"(.*)"\]""", pgn)[0]

    return datetime.strptime(date_str, "%Y.%m.%d")


def _month_url_is_needed(url: str, epoch: datetime):
    """Check if the month of games is needed.

    e.g. https://api.chess.com/pub/player/username/games/yyyy/mm
    """
    archive_year, archive_month = [int(x) for x in url.split("/")[-2:]]

    return archive_year >= epoch.year and archive_month >= epoch.month


def black(text: str) -> str:
    """Colorize text black."""
    return f"{Color.BLACK.value}{text}{Color.RESET.value}"


def white(text: str) -> str:
    """Colorize text white."""
    return f"{Color.WHITE.value}{text}{Color.RESET.value}"
