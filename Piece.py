from Board import Square
from typing import Callable, Iterable

import numpy as np


class Piece:
    material_worth: int
    kind: str
    location: str
    can_move: Callable
    
class Pawn(Piece):
    def __init__(self, location: Square):
        self.material_worth = 1
        self.kind = 'Pawn'
        self.can_move = lambda here, there: here 
        
class Knight(Piece):
    def __init__(self, location: Square):
        self.material_worth = 3
        self.kind = 'Knight'
        
class Bishop(Piece):
    def __init__(self, location: Square):
        self.material_worth = 3
        self.kind = 'Bishop'

class Rook(Piece):
    def __init__(self, location: Square):
        self.material_worth = 5
        self.kind = 'Rook'
        
class Queen(Piece):
    def __init__(self, location: Square):
        self.material_worth = 9
        self.kind = 'Queen'
        
class King(Piece):
    def __init__(self, location: Square):
        self.material_worth = np.inf
        self.kind = 'King'
