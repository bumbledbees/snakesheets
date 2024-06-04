# pylint: disable=unused-argument

from typing import Any, TypeAlias

from PySide6.QtCore import (QAbstractTableModel, QModelIndex,
                            QPersistentModelIndex, Qt)
from PySide6.QtWidgets import QAbstractItemView, QMainWindow, QTableView

from snakesheets.core.table import Table

QIndex: TypeAlias = QModelIndex | QPersistentModelIndex


class MainTableModel(QAbstractTableModel):
    def __init__(self, data: list[list[Any]]):
        super().__init__()
        self.table = Table(data)

    def data(self, index: QIndex, role: int = Qt.DisplayRole) -> Any:
        if role in (Qt.DisplayRole, Qt.EditRole):
            return str(self.table[index.column(), index.row()])
        return None

    def setData(self, index: QIndex, value: Any, role: int = Qt.DisplayRole):
        if role == Qt.EditRole:
            self.table[index.column(), index.row()] = value
            return True
        return None

    def flags(self, index: QIndex):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    def rowCount(self, parent: QIndex = QModelIndex()):
        return self.table.rows

    def columnCount(self, parent: QIndex = QModelIndex()):
        return self.table.columns


class Main(QMainWindow):  # pylint: disable=too-few-public-methods
    def __init__(self):
        super().__init__()

        self.data = [[1, 2, 3], [4, 5, 6]]
        self.model = MainTableModel(self.data)
        self.table = QTableView()
        self.table.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.table.setModel(self.model)

        self.setCentralWidget(self.table)
