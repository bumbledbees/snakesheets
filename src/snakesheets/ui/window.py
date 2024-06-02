from typing import Any

from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtWidgets import QAbstractItemView, QMainWindow, QTableView

from snakesheets.core.table import Table


class MainTableModel(QAbstractTableModel):
    def __init__(self, data: list[list[Any]]):
        super().__init__()
        self.table = Table(data)

    def data(self, index: QModelIndex, role: Qt.ItemDataRole):
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return str(self.table[index.column(), index.row()])

    def setData(self, index: QModelIndex, value: Any, role: Qt.ItemDataRole):
        if role == Qt.EditRole:
            self.table[index.column(), index.row()] = value
            return True

    def flags(self, index: QModelIndex):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    def rowCount(self, parent: QModelIndex):
        return self.table.rows

    def columnCount(self, parent: QModelIndex):
        return self.table.columns


class Main(QMainWindow):
    def __init__(self):
        super().__init__()

        self.data = [[1, 2, 3], [4, 5, 6]]
        self.model = MainTableModel(self.data)
        self.table = QTableView()
        self.table.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.table.setModel(self.model)

        self.setCentralWidget(self.table)
