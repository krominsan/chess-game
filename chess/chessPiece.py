from boardgame.piece import Piece
from boardgame.position import Position
from chess.color import Color
from chess.chessPosition import ChessPosition

class ChessPiece(Piece):
    """Representa uma Peça de Xadrez, herdando funcionalidades básicas de Piece"""

    def __init__(self, board, color: Color):
        super().__init__(board) # Invoca o construtor da classe base
        self._color = color
        self._moveCount = 0

    @property
    def color(self) -> Color:
        return self._color
    
    @property
    def moveCount(self) -> int:
        """Retorna o número de movimentos realizados pela peça."""
        return self._moveCount

    def _increaseMoveCount(self):
        """Incrementa o número de movimentos da peça."""
        self._moveCount += 1

    def _decreaseMoveCount(self):
        """Decrementa o número de movimentos da peça."""
        self._moveCount -= 1


    def getChessPosition(self):
        """Retorna a posição de xadrez da peça."""
        return ChessPosition.fromPosition(self._position)


    def _isThereOpponentPiece(self, position: Position) -> bool:
        """Verifica se há uma peça adversária na posição informada.
    
        Uma peça adversária é identificada pelo fato de:
        - Existir uma peça na posição dada.
        - Essa peça ser uma instância de ChessPiece.
        - Ter uma cor diferente da peça que está executando o movimento.
        """
        piece = self.board.pieceByPosition(position)
        return piece is not None and isinstance(piece, ChessPiece) and piece.color != self.color