from typing import Any


class SpreadsheetException(Exception):
    def __init__(self, message: str = 'Spreadsheet exception'):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message


class InvalidInput(SpreadsheetException):
    def __init__(self, message: str = 'Invalid input value',
                 value: Any = None, valueName: str = 'input'):
        super().__init__(message)
        self.value = value
        self.valueName = valueName
        if value is not None:
            self.message += f' ({valueName}: {value})'
