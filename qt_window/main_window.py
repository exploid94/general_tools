import sys

from PyQt5 import QtCore, QtWidgets, QtGui

ACTIVE_WINDOWS = {}


def register_window(title, window):
    if title in ACTIVE_WINDOWS:
        try:
            ACTIVE_WINDOWS[title].destroy()
        except Exception as e:
            Warning(f"Could not destroy instance of window with title {title}: {e}")
    ACTIVE_WINDOWS[title] = window


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None, title="Main Window"):
        super().__init__(parent)
        register_window(title, self)
        self.setWindowTitle(title)

        self.file_menu = self.menuBar().addMenu("&File")
        self.edit_menu = self.menuBar().addMenu("&Edit")
        self.help_menu = self.menuBar().addMenu("&Help")

        self._MAIN_WIDGET = QtWidgets.QWidget()
        self._MAIN_LAYOUT = QtWidgets.QGridLayout()
        self._MAIN_WIDGET.setLayout(self._MAIN_LAYOUT)
        self.setCentralWidget(self._MAIN_WIDGET)

    @property
    def main_layout(self):
        return self._MAIN_LAYOUT

    @property
    def main_widget(self):
        return self._MAIN_WIDGET



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    win = MainWindow()
    win.show()

    sys.exit(app.exec_())
