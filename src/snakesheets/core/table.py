from copy import deepcopy
from functools import partial, singledispatchmethod
from itertools import product
from typing import Any, Optional

from snakesheets.core.exception import InvalidInput
from snakesheets.core.utils import indexToCoords, padRow


class Table:
    def __init__(self, data: Optional[list[list[Any]]] = None,
                 dimensions: Optional[tuple[int, int]] = None,
                 defaultValue: Any = None):
        if data is not None:
            self.data: list = []
            columns = 0

            if not isinstance(data, list):
                raise InvalidInput('data must be a list',
                                   value=data, valueName='data')
            if len(data) == 0:
                raise InvalidInput('data must have at least 1 row',
                                   value=data, valueName='data')
            for idx, row in enumerate(data):
                if not isinstance(row, list):
                    raise InvalidInput('rows must be lists',
                                       value=row, valueName=f'row {idx}')
                count = len(row)
                newRow = deepcopy(row)

                if count < columns:
                    newRow = padRow(newRow, columns, defaultValue)
                elif count > columns:
                    columns = count
                    for subidx in range(idx):
                        self.data[subidx] = padRow(self.data[subidx],
                                                   columns, defaultValue)
                self.data.append(newRow)
            if columns == 0:
                raise InvalidInput('data must have at least 1 column',
                                   value=data, valueName='data')
        elif dimensions is not None:
            errorStr = 'dimensions must be a tuple in the form (rows, columns)'
            if not isinstance(dimensions, tuple):
                raise InvalidInput(errorStr, value=dimensions)
            if len(dimensions) != 2:
                raise InvalidInput(errorStr, value=dimensions)

            rows, columns = dimensions
            for varName, varValue in ('rows', rows), ('columns', columns):
                invalidVar = partial(InvalidInput,
                                     value=varValue, valueName=varName)
                if not isinstance(varValue, int):
                    raise invalidVar(f'number of {varName} must be an integer')
                if varValue < 0:
                    raise invalidVar('table cannot have a negative number of '
                                     f'{varName}')
                if varValue == 0:
                    raise invalidVar('table must have at least 1 '
                                     f'{varName[:-1]}')  # trim trailing 's'
            self.data = [[defaultValue] * columns] * rows
        else:
            self.data = [[defaultValue]]

    def __eq__(self, table: object) -> bool:
        if not isinstance(table, Table):
            raise InvalidInput('tables can only be compared to other tables',
                               value=table)
        if self.rows != table.rows or self.columns != table.columns:
            return False
        for x, y in product(range(self.columns), range(self.rows)):
            if self[x, y] != table[x, y]:
                return False
        return True

    def __getitem__(self, idx: str | tuple[int, int]) -> Any:
        col, row = self._indexToCoords(idx)
        return self.data[row][col]

    def __setitem__(self, idx: str | tuple[int, int], value: Any):
        col, row = self._indexToCoords(idx)
        self.data[row][col] = value

    @singledispatchmethod
    def _indexToCoords(self, idx) -> tuple[int, int]:
        raise InvalidInput('invalid index', value=idx, valueName='index')

    @_indexToCoords.register
    def _(self, idx: str) -> tuple[int, int]:
        return indexToCoords(idx)

    @_indexToCoords.register
    def _(self, idx: tuple) -> tuple[int, int]:
        if len(idx) != 2:
            raise InvalidInput('index must be a tuple in the form '
                               '(rows, columns)',
                               value=idx, valueName='index')

        for varName, varValue in ('x', idx[0]), ('y', idx[1]):
            if not isinstance(varValue, int):
                raise InvalidInput(f'{varName} value must be an integer',
                                   value=varValue, valueName=varName)
            if varValue < 0:
                raise InvalidInput(f'{varName} value cannot be negative',
                                   value=varValue, valueName=varName)
        return idx

    @property
    def rows(self):
        return len(self.data)

    @property
    def columns(self):
        if self.rows:
            return len(self.data[0])
        return 0
