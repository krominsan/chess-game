from chess.chessPiece import ChessPiece
from chess.color import Color
from boardgame.board import Board
from boardgame.position import Position


class Queen(ChessPiece):
    def __init__(self, board: Board, color: Color):
        """Inicializa uma Rainha com um tabuleiro e uma cor."""
        super().__init__(board, color)

    def __str__(self):
        return "Q"

    def possibleMoves(self):
        """Retorna uma matriz indicando as posições para onde a rainha se pode mover.

        A Rainha tem uma combinação dos movimentos de:
        - **Torre**: pode mover-se para cima, baixo, esquerda e direita.
        - **Bispo**: pode mover-se nas diagonais.

        O movimento para se:
        - Encontrar uma peça da mesma cor.
        - Encontrar uma peça adversária (pode capturá-la).
        """

        rows, cols = self.board.rows, self.board.columns
        moves = [[False for _ in range(cols)] for _ in range(rows)]


        # Se a peça ainda não estiver posicionada, não há movimento
        if self._position is None:
            return moves


        # Direções da Torre (reta) + Bispo (diagonal)
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),  # Torre (vertical/horizontal)
            (-1, -1), (-1, 1), (1, 1), (1, -1)  # Bispo (diagonal)
        ]

        for dRow, dCol in directions:
            row, col = self.position.row, self.position.column
            while True:
                row += dRow  
                col += dCol 
                if not self.board._positionExists(row, col):    # Valida row e col antes de criar Position
                    break
                pos = Position(row, col)
                if self.board.thereIsAPiece(pos): # Se houver uma peça na posição, verifica se é um adversário e encerra o movimento
                    if self._isThereOpponentPiece(pos):
                        moves[row][col] = True  # Permite captura
                    break           # A rainha para ao encontrar qualquer peça (não pode avançar por cima)
                moves[row][col] = True
        return moves