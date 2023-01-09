import chess.engine, chess.pgn, io

from contextlib import contextmanager
from prefect import task
from pydantic import BaseModel
from rich.progress import track
from typing import Optional, Union
from typing_extensions import Literal

from digest import GameDigest
from platforms import ChessPlayer
from settings import DockerRepo, OSBin
from utils import black, white

ChessEngine = Literal["stockfish"]


class EngineConfig(BaseModel):
    """Model for the chess engine configuration.

    Attrs:
        engine_name: The name of the chess engine.
        engine_location: The location of the chess engine.
        threads: The number of threads to use.
    """

    name: ChessEngine = "stockfish"
    location: Union[DockerRepo, OSBin] = OSBin.macos_m1
    Threads: int = 2

    @property
    def exec_command(self):
        if isinstance(self.location, DockerRepo):
            return (
                "docker run --rm -i -p 5000:5000 " f"{self.location.value} {self.name}"
            ).split()

        return f"{self.location.value}{self.name}"


@contextmanager
def run_engine(engine_config: Optional[EngineConfig] = None, **kwargs):
    """Context manager for the chess engine."""
    if not (engine_config or kwargs):
        print(
            f"Attempting to run stockfish @ {EngineConfig.__fields__['location'].default}"
        )

    config = engine_config or EngineConfig(**kwargs)

    engine = chess.engine.SimpleEngine.popen_uci(config.exec_command)

    engine.configure(config.dict(include={"Threads"}))

    print(
        f"Booted up {config.name!r} from {config.location.value} "
        f"using {config.Threads} thread(s)"
    )

    try:
        yield engine
    finally:
        engine.close()


@task(log_prints=True)
def calculate_total_cp_loss_for_game(
    player: ChessPlayer, pgn: str, engine: chess.engine.SimpleEngine
) -> GameDigest:
    """Analyze a game using the chess engine."""

    centipawn_losses = []

    board = chess.Board()
    game = chess.pgn.read_game(io.StringIO(pgn))

    player_color = "white" if player.username == game.headers["White"] else "black"

    print(
        f"Analyzing game on {player.platform} "
        f"between {white(game.headers['White'])} "
        f"and {black(game.headers['Black'])}"
    )

    game_url = (
        game.headers["Site"]
        if player.platform == "lichess.org"
        else game.headers["Link"]
    )

    for move in track(game.mainline_moves()):
        analysis = engine.analyse(board, chess.engine.Limit(time=0.1))

        eval = getattr(analysis["score"], player_color)()

        # TODO - handle mate scores better
        if isinstance(eval, chess.engine.Cp):
            centipawn_losses.append(eval.score())
        elif isinstance(eval, chess.engine.Mate):
            centipawn_losses.append(eval.score(mate_score=1000))

        board.push(move)

    return GameDigest.parse_obj(
        {
            "average_centipawn_loss": sum(centipawn_losses) / len(centipawn_losses),
            "game_url": game_url,
        }
    )


# if __name__ == "__main__":
#     with run_engine() as engine:
#         print(engine.id)
