from typing import TYPE_CHECKING
from chess.chessPiece import ChessPiece
from chess.color import Color
from chess.pieces.rook import Rook
from boardgame.board import Board
from boardgame.position import Position

if TYPE_CHECKING:
    from chess.chessMatch import ChessMatch

# Rei
class King(ChessPiece):

    def __init__(self, board: Board, color: Color, chessMatch: "ChessMatch"):
        """Inicializa um Rei com um tabuleiro e uma cor."""
        super().__init__(board, color)
        self._chessMatch = chessMatch

    def __str__(self):
        return "K"
    
    def _canMove(self, position: Position):
        """Verifica se o Rei pode mover-se para a posição indicada.
        
        O Rei pode mover-se para uma posição se:
        - A posição estiver dentro dos limites do tabuleiro.
        - Não houver uma peça da mesma cor no local.
        """
        piece = self.board.pieceByPosition(position)
        return piece is None or piece.color != self.color
    
    def _testRookCastling(self, position: Position) -> bool:
        """Verifica se a torre na posição indicada reúne as condições para realizar Roque."""
        piece = self.board.pieceByPosition(position)
        return isinstance(piece, Rook) and piece.color == self.color and piece.moveCount == 0
    
    def _checkCastlingPath(self, *positions: Position) -> bool:
        """Verifica se todas as posições para Roque estão livres:
        - Retorna True se todas as posições passadas não contiverem peças;
        - Retorna False se pelo menos uma das posições tiver uma peça; """
        return all(self.board.pieceByPosition(pos) is None for pos in positions)
    
    def possibleMoves(self) -> list[list[bool]]:
        """Retorna uma matriz com os movimentos possíveis do Rei
        
        O Rei pode mover-se em todas as direções (vertical, horizontal e diagonal),
        mas apenas uma casa por vez.
        """

        rows, cols = self.board.rows, self.board.columns
        moves = [[False for _ in range(cols)] for _ in range(rows)]

        if self._position is None:  # Se a peça ainda não estiver posicionada, não há movimentos
            return moves

        # Direções possíveis para o Rei (1 casa em qualquer direção)
        directions = [
            (-1, 0), (1, 0),  # Cima e Baixo
            (0, -1), (0, 1),  # Esquerda e Direita
            (-1, -1), (-1, 1),  # Diagonal superior esquerda e direita
            (1, -1), (1, 1)  # Diagonal inferior esquerda e direita
        ]

        currentRow = self._position.row
        currentCol = self._position.column

        # Testar cada direção
        for dRow, dCol in directions:

            newRow = currentRow + dRow
            newCol = currentCol + dCol            

            # Verifica se o objeto atualizado é válido e se o rei se pode mover para lá
            if self.board._positionExists(newRow, newCol):
                p = Position(currentRow + dRow, currentCol + dCol)
                if self._canMove(p):
                    moves[newRow][newCol] = True

        # Specialmove Castling
        """
        As condições para o Roque (Castling) são as seguintes:
        ✅ A Torre correta ainda não se moveu.
        ✅ O Rei ainda não se moveu.
        ✅ O caminho entre Rei e Torre está livre.
        ✅ O Rei não está em Xeque durante o Roque.
        """
        if self.moveCount == 0 and not self._chessMatch.check:

            opponent = self._chessMatch._opponent(self.color)
            currentPos = Position(currentRow, currentCol)

            # Roque pelo lado do Rei (Kingside)
            if self.board._positionExists(currentRow, currentCol + 3): # Validação da coluna da Torre
                posT1 = Position(currentRow, currentCol + 3)

                if self._testRookCastling(posT1): # A Torre do lado do Rei está na posição esperada?
                    fSquare = Position(currentRow, currentCol + 1)
                    gSquare = Position(currentRow, currentCol + 2)

                    if ( # Verifica se as casas entre Rei e Torre estão desocupadas
                        self._checkCastlingPath(fSquare, gSquare) and 
                        not self._chessMatch._isSquareAttacked(currentPos, opponent) and
                        not self._chessMatch._isSquareAttacked(fSquare, opponent) and
                        not self._chessMatch._isSquareAttacked(gSquare, opponent)     
                    ):   
                        moves[currentRow][currentCol + 2] = True # Se a conjunção de condições se verifica, então marca 
                                                                 # que o Rei se pode mover 2 casas para a direita

            # Roque pelo lado da Rainha (Queenside)
            if self.board._positionExists(currentRow, currentCol - 4):  # Validação de coluna da torre
                posT2 = Position(currentRow, currentCol - 4)

                if self._testRookCastling(posT2): # A Torre do lado da Rainha está na posição esperada?
                    dSquare = Position(currentRow, currentCol - 1)
                    cSquare = Position(currentRow, currentCol - 2)
                    bSquare = Position(currentRow, currentCol - 3)

                    if ( # Verifica se todas as casas entre o Rei e a Torre estão vazias para permitir o Roque
                        self._checkCastlingPath(dSquare, cSquare, bSquare) and
                        not self._chessMatch._isSquareAttacked(currentPos, opponent) and
                        not self._chessMatch._isSquareAttacked(dSquare, opponent) and
                        not self._chessMatch._isSquareAttacked(cSquare, opponent)
                    ):
                        moves[currentRow][currentCol - 2] = True

        return moves


