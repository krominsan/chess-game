from chess.chessPiece import ChessPiece
from chess.color import Color
from boardgame.board import Board
from boardgame.position import Position

# Torre
class Rook(ChessPiece):

    def __init__(self, board: Board, color: Color):
        super().__init__(board, color)

    def __str__(self):
        return "R"
    
    def possibleMoves(self):

        """Retorna uma matriz com os possíveis movimentos da Torre.
        
        A Torre pode mover-se em quatro direções:
        - Para cima (decrementando row).
        - Para baixo (incrementando row).
        - Para a esquerda (decrementando column).
        - Para a direita (incrementando column).

        A movimentação para em dois casos:
        - Se encontrar uma peça da mesma cor.
        - Se encontrar uma peça adversária (pode ser capturada, então a posição é marcada como válida).
        """

        rows, cols = self.board.rows, self.board.columns
        mat = [[False for _ in range(cols)] for _ in range(rows)]

        if self._position is None:
            return mat

        currentRow = self.position.row
        currentCol = self.position.column

        # Direções: cima, baixo, esquerda, direita
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dRow, dCol in directions:
            newRow = currentRow + dRow
            newCol = currentCol + dCol

            while self.board._positionExists(newRow, newCol):
                pos = Position(newRow, newCol)
                if self.board.thereIsAPiece(pos):
                    if self._isThereOpponentPiece(pos):
                        mat[newRow][newCol] = True
                    break
                mat[newRow][newCol] = True
                newRow += dRow
                newCol += dCol

        return mat
