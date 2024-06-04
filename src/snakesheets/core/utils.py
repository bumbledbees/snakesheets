from functools import cache
from typing import Any, Optional

from snakesheets.core.exception import InvalidInput


def padRow(row: list[Any], length: int, value: Any = None) -> list[Any]:
    rowLength = len(row)
    if rowLength < length:
        row += [value] * (length - rowLength)

    return row


@cache
def alphaToInt(value: str) -> int:
    intA = ord('A')
    result = 0

    for idx, n in enumerate(reversed(value.upper())):
        intN = ord(n) - intA + 1
        if intN < 1 or intN > 26:
            raise InvalidInput(value=value)
        result += intN * (26 ** idx)

    return result - 1


@cache
def intToAlpha(value: int) -> str:
    if value < 0:
        raise InvalidInput(message='Index cannot be negative', value=value)

    intA = ord('A')
    result = ''
    value += 1

    while value > 0:
        result += chr((value - 1) % 26 + intA)
        value = (value - 1) // 26

    # if value is 0, result will be '' but it should be 'A'
    return result[::-1] or 'A'


@cache
def indexToCoords(idx: str) -> tuple[int, int]:
    col: Optional[str] = None
    row: Optional[str] = None

    for ch in idx:
        if ch.isalpha():
            if row is not None:  # letter after number
                raise InvalidInput(f'Parse error on index {idx}')
            col = ch if col is None else col + ch
        elif ch.isdigit():
            if col is None:  # number before letter
                raise InvalidInput(f'Parse error on index {idx}')
            row = ch if row is None else row + ch
        elif ch != '_':  # underscores are allowed but get ignored
            raise InvalidInput(f'Illegal character {ch} in index {idx}')
    if col is None or row is None:
        raise InvalidInput(f'Invalid index {idx}')

    return (alphaToInt(col), int(row))
