from enum import Enum


class Color(Enum):
    """ANSI color codes."""

    BLACK = "\033[0;30m"
    WHITE = "\033[0;37m"
    RESET = "\x1b[0m"


class DockerRepo(Enum):
    """Enum holding Docker repository names."""

    STOCKFISH = "ghcr.io/x64squares/stockfish-socket-server"
    LCZERO = "..."


class OSBin(Enum):
    """Enum holding OS-specific location of binaries for the chess engine.

    Members:
        macos_m1: /opt/homebrew/bin/
        linux: /usr/bin/
        windows: C:\\Program Files\\ (maybe?)

    """

    macos_m1 = "/opt/homebrew/bin/"
    linux = "/usr/bin/"
    windows = "C:\\Program Files\\"
