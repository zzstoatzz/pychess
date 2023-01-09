import httpx

from prefect import task
from prefect.blocks.system import Secret
from pydantic import BaseModel, HttpUrl, validator
from typing import List, Optional

from platforms import ChessPlayer


class GameDigest(BaseModel):
    average_centipawn_loss: float
    game_url: HttpUrl

    @validator("average_centipawn_loss")
    def round_centipawn_loss(cls, v):
        return round(v, 2)


def _make_digest_blocks(player: ChessPlayer, games: List[GameDigest], n_days: int):

    make_text = lambda game: (
        f"You had an average centipawn loss of {game.average_centipawn_loss} "
        f"in this one: {game.game_url}"
    )

    n_games = " " + str(len(games)) if len(games) > 1 else ""

    greeting = (
        f"Hi {player.username} :slightly_smiling_face: "
        f"here's your{n_games} most accurate :chess_pawn: game(s) "
        f"on {player.platform} over the last {n_days} days:"
    )

    blocks = [greeting] + games

    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{make_text(b) if isinstance(b, GameDigest) else b}",
            },
        }
        for b in blocks
    ]


@task
def send_digest(
    player: ChessPlayer,
    webhook_url: str,
    games: List[GameDigest],
    n_days: int,
    top_N_games: Optional[int] = None,
):
    """Builds a Slack block from the GameDigest."""

    games_played = len(games)

    if top_N_games:
        games = games[:top_N_games]

    digest_blocks = _make_digest_blocks(player, games, n_days)

    response = httpx.post(
        url=Secret.load(webhook_url).get(),
        json={"blocks": digest_blocks},
        headers={"Content-type": "application/json"},
    )

    if response.status_code != 200:
        raise httpx.HTTPError(
            message=f"Error sending digest to Slack: {response.status_code} {response.text}"
        )
