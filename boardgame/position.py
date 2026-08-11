class Position:

    def __init__(self, row: int, column: int):
        if row < 0 or column < 0:
            raise ValueError("Column and Row values must be Positive!")

        self.row = row
        self.column = column

    def __str__(self):
        return f"{self.row}, {self.column}"

    def __eq__(self, other):
        if not isinstance(other, Position):
            return NotImplemented
        return self.row == other.row and self.column == other.column

    def __hash__(self):
        return hash((self.row, self.column))