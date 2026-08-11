from boardgame.piece import Piece
from boardgame.position import Position
from boardgame.boardException import BoardException

class Board: # Representa o tabuleiro de xadrez com controlo de posições e peças.

    def __init__(self, rows, columns):
        if (rows < 1 or columns < 1):
            raise BoardException("Error creating board: there must be at least 1 row and 1 column.")
        self._rows = rows
        self._columns = columns
        self._pieces = [[None] * columns for _ in range(rows)] # Cria uma "lista de listas" 2D que representa o tabuleiro de xadrez, com posições nulas

    @property
    def rows(self):
        # Retorna o número de linhas do tabuleiro.
        return self._rows

    @property
    def columns(self):
        # Retorna o número de colunas do tabuleiro.
        return self._columns

    # Método que retorna a peça numa posição específica, por coordenadas da matriz pieces
    def piece(self, row, column) -> Piece:
        if not self._positionExists(row, column):
            raise BoardException("Position not on the board.")
        return self._pieces[row][column]
    
    # Método que retorna a peça segundo um objeto Position (pela posição)
    def pieceByPosition(self, position: Position) -> Piece:
        if not self.positionExists(position):
            raise BoardException("Position not on the board.")
        return self.piece(position.row, position.column)

    # Método que coloca as peças no tabuleiro
    def placePiece(self, piece: Piece, position: Position):
        if self.thereIsAPiece(position):
            raise BoardException(f"There is already a piece on {position}")
        self._pieces[position.row][position.column] = piece
        piece.position = position

    def removePiece(self, position: Position) -> Piece:
        if not self.positionExists(position):
            raise BoardException(f"Position not on the board.")
        piece = self.pieceByPosition(position)
        if piece is None:
            return None
        piece.position = None
        self._pieces[position.row][position.column] = None
        return piece

    def _positionExists(self, row, column) -> bool:
        return 0 <= row < self.rows and 0 <= column < self.columns
    
    def positionExists(self, position: Position) -> bool:
        return self._positionExists(position.row, position.column)

    def thereIsAPiece(self, position: Position) -> bool:
        if not self.positionExists(position):
            raise BoardException("Position not on the board.")
        return self.pieceByPosition(position) is not None
