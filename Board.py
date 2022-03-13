from string import ascii_lowercase

alphabet = ascii_lowercase

class Square:
    def __init__(self: object, location: str):
        self.location = location
        
    def _delta(self: object, destination_square: object) -> None:
        destination = destination_square.location
        delta_y = abs(ord(self.location[0]) - ord(destination[0]))
        delta_x = abs(int(self.location[1]) - int(destination[1]))
        
        return delta_x, delta_y
         
    def diagonal(self: object, destination_square: object) -> bool:

        delta_x, delta_y = self._delta(destination_square)
        
        return delta_x == delta_y
    
    def touches(self: object, destination_square: object) -> bool:
        
        delta_x, delta_y = self._delta(destination_square)
        
        return delta_x < 2 and delta_y < 2
    
    def along(self: object, destination_square: object) -> bool:
        
        delta = self._delta(destination_square)
        
        return sum([int(i == 0) for i in delta]) == 1
    
    def horsey(self: object, destination_square: object) -> bool:
        
        delta_x, delta_y = self._delta(destination_square)
        
        return (delta_x == 1 and delta_y == 2) or (delta_x == 2 and delta_y == 1)
    
    def __repr__(self: object) -> str:
        return self.location

class Board:
    def __init__(self: object, length: int = 8):
        self.size = length**2
        self.squares = {
            Square(f"{letter}{number}"): None for letter in alphabet[:length] for number in range(1, length + 1)
        }
        
board = Board()

test = Square('a1')

for square in board.squares:
    print(f"it is {square.horsey(test)} that a horse can go from {square} to {test}")
    input()