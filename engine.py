import chess.engine, chess.pgn, io

from contextlib import contextmanager
from prefect import task
from pydantic import BaseModel
from typing import Optional
from typing_extensions import Literal

from digest import GameDigest
from platforms import ChessPlayer
from settings import Color, OSBin

ChessEngine = Literal["stockfish"]


class EngineConfig(BaseModel):
    """Model for the chess engine configuration.

    Attrs:
        engine_name: The name of the chess engine.
        engine_location: The location of the chess engine.
        threads: The number of threads to use.
    """

    name: Literal["stockfish"] = "stockfish"
    location: OSBin = OSBin.macos_m1
    Threads: int = 4

    @property
    def executable_path(self):
        return f"{self.location.value}{self.name}"


@contextmanager
def engine_running(engine_config: Optional[EngineConfig] = None, **kwargs):
    """Context manager for the chess engine."""
    if not (engine_config or kwargs):
        print("Attempting to run stockfish @ default homebrew M1 MacOS location")

    config = engine_config or EngineConfig(**kwargs)

    engine = chess.engine.SimpleEngine.popen_uci(config.executable_path)

    engine.configure(config.dict(include={"Threads"}))

    print(
        f"Booted up {config.name!r} @ {config.executable_path} "
        f"using {config.Threads} thread(s)"
    )

    try:
        yield engine
    finally:
        engine.quit()


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
        f"between {Color.WHITE.value + game.headers['White'] + Color.RESET.value} "
        f"and {Color.BLACK.value + game.headers['Black'] + Color.RESET.value}"
    )

    game_url = (
        game.headers["Site"]
        if player.platform == "lichess.org"
        else game.headers["Link"]
    )

    for move in game.mainline_moves():
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
