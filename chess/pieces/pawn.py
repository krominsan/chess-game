from typing import TYPE_CHECKING
from chess.chessPiece import ChessPiece
from chess.color import Color
from boardgame.board import Board
from boardgame.position import Position

if TYPE_CHECKING:
    from chess.chessMatch import ChessMatch

class Pawn(ChessPiece):
    def __init__(self, board: Board, color: Color, chessMatch: "ChessMatch"):
        """Inicializa um Peão com um tabuleiro e uma cor."""
        super().__init__(board, color)
        self._chessMatch = chessMatch

    def __str__(self):
        return "P"

    def possibleMoves(self):
        """Retorna uma matriz indicando as posições onde o Peão pode se mover.
        
        O Peão pode mover-se de acordo com as seguintes regras:
        - Move-se uma **casa para a frente**, se esta estiver vazia.
        - Se for o seu **primeiro movimento**, opcionalmente pode avançar duas casas.
        - **Captura** adversários nas diagonais (esquerda e direita).
        """

        rows, cols = self.board.rows, self.board.columns
        moves = [[False for _ in range(cols)] for _ in range(rows)]


        # Se a peça ainda não estiver posicionada, não há movimento
        if self._position is None: 
            return moves

        direction = -1 if self.color == Color.WHITE else 1  # Define a direção do avanço
        row, col = self._position.row, self._position.column

        # 🔹 Movimento normal do peão (avança uma casa)
        front_pos = Position(row + direction, col)
        if self.board.positionExists(front_pos) and not self.board.thereIsAPiece(front_pos):
            moves[front_pos.row][front_pos.column] = True

            # 🔹 Primeiro movimento (duas casas)
            two_squares_front = Position(row + (2 * direction), col)
            if self.board.positionExists(two_squares_front) and not self.board.thereIsAPiece(two_squares_front) and self.moveCount == 0:
                moves[two_squares_front.row][two_squares_front.column] = True

        # Capturas diagonais
        for dCol in [-1, 1]:
            newRow = row + direction
            newCol = col + dCol
            if self.board._positionExists(newRow, newCol):
                pos = Position(newRow, newCol)
                if self.board.thereIsAPiece(pos) and self._isThereOpponentPiece(pos):
                    moves[newRow][newCol] = True

        # 🔹 **Implementação do En Passant**
        enPassantRow = 3 if self.color == Color.WHITE else 4  # Define a linha onde En Passant pode ocorrer
        if self.position.row == enPassantRow:  # Verifica se o peão está na linha correta
            for dCol in [-1, 1]:  # Verifica ambos os lados (esquerda e direita)
                adjacentCol = self.position.column + dCol  # Calcula a coluna adjacente
                
                # Valida se a coluna adjacente existe no tabuleiro
                if 0 <= adjacentCol < self.board.columns:
                    adjacentPos = Position(self.position.row, adjacentCol)  # Cria Position adjacente
                    
                    # Verifica se há um peão adversário vulnerável a En Passant
                    if (self._isThereOpponentPiece(adjacentPos) and self.board.pieceByPosition(adjacentPos) is self._chessMatch.enPassantVulnerable):
                        
                        # Calcula a linha de destino (uma casa atrás/diagonal, dependendo da cor)
                        targetRow = enPassantRow - 1 if self.color == Color.WHITE else enPassantRow + 1
                        targetPos = Position(targetRow, adjacentCol)
                        
                        # Valida se a posição de destino existe e está vazia
                        if (self.board.positionExists(targetPos) and not self.board.thereIsAPiece(targetPos)):
                        
                            # Marca o movimento En Passant como válido
                            moves[targetRow][adjacentCol] = True

        return moves
