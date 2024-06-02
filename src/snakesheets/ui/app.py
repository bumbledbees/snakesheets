from PySide6.QtWidgets import QApplication

from snakesheets.ui.window import Main


class App(QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.window = Main()
        self.window.show()

