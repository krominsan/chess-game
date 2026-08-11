
from boardgame.position import Position

# Classe base para todas as Peças do tabuleiro de Xadrez

class Piece:

    def __init__(self, board):
        self._board = board 
        self._position = None # Inicialmente, a peça não tem posição definida
    

    # Apenas a hierarquia de classes iniciada em Piece deve ter acesso ao Tabuleiro
    @property
    def board(self):
        return self._board

    @property
    def position(self) -> Position:
        return self._position

    @position.setter
    def position(self, value: Position):
        self._position = value

    def possibleMoves(self) -> list[list[bool]]:
        raise NotImplementedError("Subclasses must implement possibleMoves")
    
    def possibleMove(self, target: Position) -> bool:
        """Verifica se a peça pode mover-se para a posição alvo."""
        moves = self.possibleMoves()
        return moves[target.row][target.column]

    def isThereAnyPossibleMove(self):
        mat = self.possibleMoves()
        for row in mat:
            for move in row:
                if move:  # Se algum movimento for possível, retorna True
                    return True
        return False

