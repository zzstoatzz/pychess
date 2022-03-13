from string import ascii_lowercase

from Piece import make
from Position import starting_position

alphabet = ascii_lowercase


class Board:
    def __init__(self: object, length: int = 8):
        self.size = length ** 2
        self.squares = {
            f"{letter}{number}": self.Square(f"{letter}{number}")
            for letter in alphabet[:length]
            for number in range(1, length + 1)
        }
        self.setup()

    def setup(self: object, position: dict = starting_position):
        for square, piece_info in position.items():
            self.squares[square].piece = make(square, piece_info)

    def __repr__(self) -> str:
        str_board = "\t\t\t --- PYCHESS ---"
        for square in self.squares:
            str_board += "  "
            if "1" in square:
                str_board += "\n" * 3
            str_board += repr(self.squares[square])

        return str_board

    class Square:
        def __init__(self: object, location: str):
            self.location = location
            self.piece = None

        def _delta(self: object, destination: object) -> None:
            destination = destination.location
            delta_y = abs(ord(self.location[0]) - ord(destination[0]))
            delta_x = abs(int(self.location[1]) - int(destination[1]))

            return delta_x, delta_y

        def along(self: object, destination: object) -> bool:

            delta = self._delta(destination)

            return sum([int(i == 0) for i in delta]) == 1

        def diagonal(self: object, destination: object) -> bool:

            delta_x, delta_y = self._delta(destination)

            return delta_x == delta_y

        def horsey(self: object, destination: object) -> bool:

            delta_x, delta_y = self._delta(destination)

            xyy = delta_x == 1 and delta_y == 2
            xxy = delta_x == 2 and delta_y == 1

            return xyy or xxy

        def touches(self: object, destination: object) -> bool:

            delta_x, delta_y = self._delta(destination)

            return delta_x < 2 and delta_y < 2

        def same_as(self: object, destination: object) -> bool:
            return self.location == destination.location

        def __repr__(self: object) -> str:
            if self.piece:
                return repr(self.piece)
            else:
                return " empty"


if __name__ == "__main__":
    board = Board()

    print(board)
