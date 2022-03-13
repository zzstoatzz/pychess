from typing import List, Union

import numpy as np
from termcolor import colored


class Piece:
    color: str
    material_worth: int
    kind: str
    on: Union[str, List[str]]

    def remember(self: object, new_position: str):
        try:
            self.on.append(new_position)
        except TypeError:
            self.on = [self.on].append(new_position)

    def __repr__(self: object):
        color = self.color if self.color != "black" else "magenta"
        message = colored(f"{self.kind}", color)

        buffer = 16 - len(message)

        return " " * (buffer // 2) + message + " " * (buffer // 2)


class Pawn(Piece):
    def __init__(self, color: str, square_location: str):
        self.color = color
        self.kind = "pawn"
        self.on = square_location
        self.material_worth = 1


class Knight(Piece):
    def __init__(self, color: str, square_location: str):
        self.color = color
        self.kind = "knight"
        self.on = square_location
        self.material_worth = 3


class Bishop(Piece):
    def __init__(self, color: str, square_location: str):
        self.color = color
        self.kind = "bishop"
        self.on = square_location
        self.material_worth = 3


class Rook(Piece):
    def __init__(self, color: str, square_location: str):
        self.color = color
        self.kind = "rook"
        self.on = square_location
        self.material_worth = 5


class Queen(Piece):
    def __init__(self, color: str, square_location: str):
        self.color = color
        self.kind = "queen"
        self.on = square_location
        self.material_worth = 9


class King(Piece):
    def __init__(self, color: str, square_location: str):
        self.color = color
        self.kind = "king"
        self.on = square_location
        self.material_worth = np.inf


class Marker(Piece):
    def __init__(self, square_location: str, color: str = "blue"):
        self.color = color
        self.kind = "marker"
        self.on = square_location
        self.material_worth = None


mappy = {"B": Bishop, "K": King, "N": Knight, "P": Pawn, "Q": Queen, "R": Rook}


def make(square_location: str, info: tuple) -> Piece:

    color, piece_type_abbrev = info

    piece_type = mappy[piece_type_abbrev]

    return piece_type(color, square_location)
