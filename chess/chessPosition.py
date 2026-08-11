from chess.chessException import ChessException
from boardgame.position import Position

class ChessPosition:

    def __init__(self, column, row):
        if column < 'a' or column > 'h':
            raise ChessException("Invalid Column Values - valid values are 'a' to 'h'")
        if row < 1 or row > 8:
            raise ChessException("Invalid Line Values - valid values are '1' to '8'")
        self._column = column
        self._row = row

    @property
    def column(self):
        # Retorna a coluna da posição
        return self._column
    
    @property
    def row(self):
        return self._row
    
    def toPosition(self):
        # Converte a linha do xadrez (1-8) para a linha da matriz (0-7)
        matrixRow = 8 - self._row
        # Converte a coluna do xadrez (a-h) para a coluna da matriz (0-7)
        matrixCol = ord(self._column) - ord('a')
        return Position(matrixRow, matrixCol)
    
    @staticmethod
    def fromPosition(position: Position):
        # Converte uma Linha e Coluna numéricas da matriz numa posição de xadrez - notação letraNum (a1, b2, c7...)
        if position.row < 0 or position.row >= 8 or position.column < 0 or position.column >= 8:
            raise ChessException("Invalid matrix position.")
        return ChessPosition(chr(position.column + ord('a')), 8 - position.row)
    
    def __str__(self):
        return f'{self._column}{self._row}'