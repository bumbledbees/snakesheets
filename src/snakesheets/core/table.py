from functools import cache
from itertools import product
from typing import Any, Optional, Self, Tuple

from snakesheets.core import exception


class Table:
    def __init__(self, data: Optional[list[list[Any]]] = None,
                 rows: Optional[int] = None, columns: Optional[int] = None):
        self.data = []
        num_columns = 0
        if data:
            for idx, row in enumerate(data):
                count = len(row)
                if count < num_columns:
                    row = padRow(row, num_columns)
                elif count > num_columns:
                    num_columns = count
                    for subidx in range(0, idx):
                        self.data[idx] = padRow(self.data[idx], num_columns)
                self.data.append(row)
        elif rows and columns:
            self.data = ([None] * columns) * rows

    def __eq__(self, table: Self) -> bool:
        if self.rows != table.rows or self.columns != table.columns:
            return False
        for x, y in product(range(self.columns), range(self.rows)):
            if self[x, y] != table[x, y]:
                return False
        return True

    def __getitem__(self, idx: str | Tuple[int, int]) -> Any:
        if isinstance(idx, str):  # excel-like cell reference
            col, row = Table.indexToCoords(idx)
            return self.data[row][col]
        elif isinstance(idx, tuple):  # x, y coordinates
            return self.data[idx[1]][idx[0]]
        else:
            raise ValueError(f'Invalid index {idx}')

    def __setitem__(self, idx: str | Tuple[int, int], value: Any):
        if isinstance(idx, str):  # excel-like cell reference
            col, row = Table.indexToCoords(idx)
            self.data[row][col] = value
        elif isinstance(idx, tuple):  # x, y coordinates
            self.data[idx[1]][idx[0]] = value
        else:
            raise ValueError(f'Invalid index {idx}')

    @cache
    @staticmethod
    def alphaToInt(value: str) -> int:
        INT_A = ord('A')
        result = 0

        for idx, n in enumerate(reversed(value.upper())):
            n = ord(n) - INT_A + 1
            if n < 1 or n > 26:
                raise InvalidInput(value=value)
            result += n * (26 ** idx)

        return result - 1

    @cache
    @staticmethod
    def intToAlpha(value: int) -> str:
        if value < 0:
            raise InvalidInput(message='Index cannot be negative', value=value)

        INT_A = ord('A')
        result = ''
        value += 1

        while value > 0:
            result += chr((value - 1) % 26 + INT_A)
            value = (value - 1) // 26

        # if value is 0, result will be '' but it should be 'A'
        return result[::-1] or 'A'

    @cache
    @staticmethod
    def indexToCoords(idx: str) -> Tuple[int, int]:
        col = None
        row = None
        for ch in idx:
            if ch.isalpha():
                if row is not None:  # letter after number
                    raise ValueError(f'Parse error on input {idx}')
                col = ch if col is None else col + ch
            elif ch.isdigit():
                if col is None:  # number before letter 
                    raise ValueError(f'Parse error on input {idx}')
                row = ch if row is None else row + ch
            elif ch != '_':  # underscores are allowed but get ignored
                raise ValueError(f'Illegal character {ch} in index {idx}')
        if col is None or row is None:
            raise ValueError(f'Invalid index {idx}')
        return (Table.alphaToInt(col), int(row))

    @property
    def rows(self):
        return len(self.data)

    @property
    def columns(self):
        if self.rows:
            return len(self.data[0])
        else:
            return 0

    def padRow(self, row: list[Any], length: int,
               value: Any = None) -> list[Any]:
        if len(row) < length:
            row += [value] * (length - len(row))
        return row

