from prefect import flow
from typing import Optional

from digest import send_digest
from engine import calculate_total_cp_loss_for_game, run_engine, EngineConfig
from platforms import ChessPlayer, retrieve_pgns_for_player


@flow(log_prints=True)
def weekly_digest(
    player: ChessPlayer,
    engine_config: Optional[EngineConfig] = None,
    n_days: int = 7,
    top_N_games: int = 3,
):
    """Send a weekly digest of chess games to the user."""

    print(f"♜♖ THIS ♞♘ is ♝♗ your ♛♕ weekly ♚♔ {player.platform} ♝♗ stats ♞♘ digest ♜♖")

    pgns = retrieve_pgns_for_player(player=player, n_days=n_days)

    if not pgns:
        print("No games found :( try increasing `n_days`")
        return

    with run_engine(engine_config) as engine:
        game_digests = [
            calculate_total_cp_loss_for_game(player, pgn, engine) for pgn in pgns
        ]

    game_digests.sort(key=lambda x: x.average_centipawn_loss, reverse=True)

    send_digest(player, game_digests, n_days, top_N_games)


if __name__ == "__main__":
    weekly_digest(
        player=dict(username="HowellV", platform="chess.com"),
        n_days=2,
    )
