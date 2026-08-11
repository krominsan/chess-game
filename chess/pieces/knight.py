from chess.chessPiece import ChessPiece
from chess.color import Color
from boardgame.board import Board
from boardgame.position import Position


class Knight(ChessPiece):
    def __init__(self, board: Board, color: Color):
        """Inicializa um Cavalo com um tabuleiro e uma cor."""
        super().__init__(board, color)

    def __str__(self):
        return "N"

    def possibleMoves(self):
        """Retorna uma matriz indicando as posições onde o Cavalo pode se mover.
        
        O Cavalo move-se em **L**, ou seja:
        - Pode avançar duas casas na vertical e uma na horizontal.
        - Pode avançar duas casas na horizontal e uma na vertical.

        Ele **pode saltar sobre outras peças** e movimentar-se independentemente delas.
        """

        rows, cols = self.board.rows, self.board.columns
        moves = [[False for _ in range(cols)] for _ in range(rows)]

        # Se a peça ainda não estiver posicionada no tabuleiro, não há movimentos

        if self._position is None:
            return moves

        # Lista de possíveis deslocamentos em formato de 'L'
        moveOffsets = [
            (-1, -2), (-2, -1), (-2, 1), (-1, 2),  
            (1, 2), (2, 1), (2, -1), (1, -2)  
        ]

        # Itera sobre os vários Offsets possíveis

        for dRow, dCol in moveOffsets:
            newRow, newCol = self._position.row + dRow, self._position.column + dCol
            

            # Primeiro, verifica se a nova posição está dentro dos limites do tabuleiro

            if self._board._positionExists(newRow, newCol):
                newPosition = Position(newRow, newCol)
                # O Cavalo pode capturar um adversário OU simplesmente mover-se para uma casa vazia
                if not self.board.thereIsAPiece(newPosition) or self._isThereOpponentPiece(newPosition): 
                    moves[newRow][newCol] = True  # Marca a posição como válida

        return moves