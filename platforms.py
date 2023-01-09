import httpx, lichess.api

from chessdotcom import get_player_game_archives, types as chessdotcom_types
from datetime import datetime, timedelta
from lichess.format import PGN
from prefect import flow, task
from pydantic import BaseModel
from typing_extensions import Literal

import utils

ChessPlatform = Literal["chess.com", "lichess.org"]


class ChessPlayer(BaseModel):
    """Model for a chess player.

    Attrs:
        username: The username of the player.
        platform: The online platform the player is on.
    """

    username: str
    platform: ChessPlatform


def _get_game_urls_chessdotcom(username: str, epoch: datetime):
    """Get a month of PGNs from the chess.com API."""

    return [
        url
        for url in get_player_game_archives(username).archives
        if utils._month_url_is_needed(url, epoch)
    ]


@task(name="Get games from chess.com", retries=1, retry_delay_seconds=3)
def get_games_from_chessdotcom(username: str, epoch: datetime):
    """Get a month of PGNs from the chess.com API."""

    try:
        month_urls = _get_game_urls_chessdotcom(username, epoch)

    except chessdotcom_types.ChessDotComError as e:
        raise ValueError(
            f"Could not retrieve games for {username!r} from chess.com - "
            "please verify that this is a valid username."
        ) from e

    try:
        months_of_games = [httpx.get(url).json()["games"] for url in month_urls]
    except httpx.ReadTimeout:
        print("Chess.com times out sometimes")
        raise
    return [
        game["pgn"]
        for month_of_games in months_of_games
        for game in month_of_games
        if utils._date_from_pgn(game["pgn"]) >= epoch
    ]


@task(name="Get games from lichess.org")
def get_games_from_lichess(username: str, epoch: datetime):
    """Get a month of PGNs from the lichess.org API."""
    try:
        pgn_generator = lichess.api.user_games(username, format=PGN)

    except lichess.api.ApiHttpError as e:
        raise ValueError(
            f"Could not retrieve games for {username!r} from lichess.org - "
            "please verify that this is a valid username."
        ) from e

    pgns = []
    last_date = datetime.now()

    while last_date >= epoch:
        pgn = next(pgn_generator)
        pgns.append(pgn)
        last_date = utils._date_from_pgn(pgn)
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

    pgns = get_games_from_platform(username=player.username, epoch=epoch)

    print(
        f"Retrieved {len(pgns)} games for {player.username!r} "
        f"over the last {n_days} days on {player.platform}"
    )

    return pgns if len(pgns) > 0 else None
