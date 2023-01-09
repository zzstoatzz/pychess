import chess.engine, chess.pgn, httpx, io, lichess.api, re

from contextlib import contextmanager
from chessdotcom import get_player_game_archives
from datetime import datetime, timedelta
from enum import Enum
from lichess.format import PGN
from prefect import flow, task
from pydantic import BaseModel, HttpUrl
from typing import Any, Dict
from typing_extensions import Literal


class Color(Enum):
    """ANSI color codes."""

    BLACK = "\033[0;30m"
    WHITE = "\033[0;37m"


ChessEngine = Literal["stockfish"]
ChessPlatform = Literal["chess.com", "lichess.org"]


class EngineLocation(Enum):
    """Enum holding OS-specific location of binaries for the chess engine."""

    macos = "/opt/homebrew/bin/"
    linux = "/usr/bin/"
    windows = "C:\\Program Files\\"


class ChessPlayer(BaseModel):
    """Model for a chess player.

    Attributes:
        username: The username of the player.
        platform: The online platform the player is on.
    """

    username: str
    platform: ChessPlatform


class GameDigest(BaseModel):
    average_centipawn_loss: float
    game_url: HttpUrl


@contextmanager
def engine_running(engine_name: ChessEngine, engine_location: str, threads: int = 2):
    """Context manager for the chess engine."""

    engine = chess.engine.SimpleEngine.popen_uci(
        f"{engine_location.value}{engine_name}"
    )

    engine.configure({"Threads": threads})

    print(
        f"Booted up {engine_name!r} from {engine_location.value} using {threads} thread(s)"
    )

    try:
        yield engine
    finally:
        engine.quit()


def _date_from_pgn(pgn: str) -> datetime:
    """Extract the date from a PGN."""

    date_str = re.findall(r"""\[Date\s"(.*)"\]""", pgn)[0]

    return datetime.strptime(date_str, "%Y.%m.%d")


def _month_url_is_needed(url: str, since: datetime):
    """Check if the month of games is needed."""

    archive_year, archive_month = [int(x) for x in url.split("/")[-2:]]

    return archive_year >= since.year and archive_month >= since.month


def _get_game_urls_chessdotcom(username: str, since: datetime):
    """Get a month of PGNs from the chess.com API."""

    return [
        url
        for url in get_player_game_archives(username).archives
        if _month_url_is_needed(url, since)
    ]


@task
def get_games_from_chessdotcom(username: str, since: datetime):
    """Get a month of PGNs from the chess.com API."""

    month_urls = _get_game_urls_chessdotcom(username, since)

    game_objects = [httpx.get(url).json()["games"] for url in month_urls]

    return [
        game["pgn"]
        for games in game_objects
        for game in games
        if _date_from_pgn(game["pgn"]) >= since
    ]


@task
def get_games_from_lichess(username: str, since: datetime):
    """Get a month of PGNs from the lichess.org API."""
    pgn_generator = lichess.api.user_games(username, format=PGN)

    pgns = []
    last_date = datetime.now()

    while last_date >= since:
        pgn = next(pgn_generator)
        pgns.append(pgn)
        last_date = _date_from_pgn(pgn)
    return pgns


platform_map = {
    "chess.com": get_games_from_chessdotcom,
    "lichess.org": get_games_from_lichess,
}


@flow(log_prints=True)
def retrieve_pgns_for_player(player: ChessPlayer, n_days: int):
    """Retrieve games from the platform API."""
    print(f"Retrieving games for {player.username!r} on {player.platform}")

    epoch = datetime.now() - timedelta(days=n_days)

    get_games_from_platform = platform_map[player.platform]

    pgns = get_games_from_platform(username=player.username, since=epoch)

    print(
        f"Retrieved {len(pgns)} games for {player.username!r} "
        f"over the last {n_days} days on {player.platform}"
    )

    return pgns


@task
def calculate_total_cp_loss_for_game(
    player: ChessPlayer, pgn: str, engine: chess.engine.SimpleEngine
) -> Dict[str, Any]:
    """Analyze a game using the chess engine."""

    centipawn_losses = []
    board = chess.Board()
    game = chess.pgn.read_game(io.StringIO(pgn))
    player_color = "white" if player.username == game.headers["White"] else "black"

    print(
        f"Analyzing game on {player.platform} "
        f"between {Color.WHITE.value + game.headers['White']!r} "
        f"and {Color.WHITE.value + game.headers['Black']!r} "
    )

    game_url = (
        game.headers["Site"]
        if player.platform == "lichess.org"
        else game.headers["Link"]
    )

    for move in game.mainline_moves():
        analysis = engine.analyse(board, chess.engine.Limit(time=0.1))

        score = getattr(analysis["score"], player_color)()
        if isinstance(score, chess.engine.Cp):
            centipawn_losses.append(score.score())
        elif isinstance(score, chess.engine.Mate):
            centipawn_losses.append(score.score(mate_score=1000))

        board.push(move)

    return {
        "average_centipawn_loss": sum(centipawn_losses) / len(centipawn_losses),
        "game_url": game_url,
    }


@flow(log_prints=True)
def weekly_digest(
    player: ChessPlayer,
    n_days: int = 7,
    engine_name: ChessEngine = "stockfish",
    engine_location: EngineLocation = EngineLocation.macos,
    include_top_N_games: int = 5,
):
    """Send a weekly digest of chess games to the user."""

    print("Starting weekly digest")

    pgns = retrieve_pgns_for_player(player=player, n_days=n_days)

    with engine_running(engine_name, engine_location) as engine:

        centipawn_losses = [
            GameDigest.parse_obj(calculate_total_cp_loss_for_game(player, pgn, engine))
            for pgn in pgns
        ]

    centipawn_losses.sort(key=lambda x: x.average_centipawn_loss, reverse=True)

    top_games = centipawn_losses[:include_top_N_games]

    print(f"Sending weekly digest to {player.username!r}")

    print(f"{top_games!r}")


if __name__ == "__main__":

    weekly_digest(player=dict(username="n80n8", platform="chess.com"))
