from chess.chessPiece import ChessPiece
from chess.color import Color
from boardgame.board import Board
from boardgame.position import Position


class Bishop(ChessPiece):
    def __init__(self, board: Board, color: Color):
        """Inicializa um Bispo com um tabuleiro e uma cor"""
        super().__init__(board, color)

    def __str__(self):
        return "B"
    
    def possibleMoves(self) -> list[list]:
        """Retorna uma matriz indicando as posições onde se pode mover o Bispo

        O Bispo move-se nas quatro diagonais:
        - Superior esquerda (-1, -1)
        - Superior direita (-1, +1)
        - Inferior direita (+1, +1)
        - Inferior esquerda (+1, -1)

        O movimento do Bispo pára se:
        - Encontrar uma peça da mesma cor.
        - Encontrar uma peça adversária (pode capturá-la)
        """

        rows, cols = self.board.rows, self.board.columns
        moves = [[False for _ in range(cols)] for _ in range(rows)]
            
        if self._position is None:  # Se a peça ainda não estiver posicionada, não há movimentos
            return moves
        
        directions = [(-1, -1), (-1, 1), (1, 1), (1, -1)]

        currentRow, currentCol = self._position.row, self._position.column
        for dRow, dCol in directions:
            row, col = currentRow, currentCol
            while True:  
                row += dRow
                col += dCol

                if not self.board._positionExists(row,col):
                    break
                pos = Position(row, col)  # Marca a posição como válida para movimento  
                # Se houver uma peça na posição, verifica se é um adversário e encerra o movimento
                if self.board.thereIsAPiece(pos):  
                    if self._isThereOpponentPiece(pos):  
                        moves[row][col] = True  # Permite captura  
                    
                    break  # O ciclo while sai quando existe uma peça adversária que pode ser capturada 
                moves[row][col] = True

        return moves
