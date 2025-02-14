import sys
from PyQt5.QtWidgets import *

from genesis.ui import widgets, scene
from genesis.core.objects import nodes

class NodeEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        self.setGeometry(200, 200, 800, 600)
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

        self.scene = scene.Scene()

        self.graphics_view = widgets.GraphicsView(self.scene.graphics_scene, self)
        self.main_layout.addWidget(self.graphics_view)

        self.setWindowTitle("Node Editor")

        self.test_nodes()

    def test_nodes(self):
        node1 = widgets.NodeWidget(nodes.StringNode(name="NODE 1", value="Hello World!"), self.scene)
        node2 = widgets.NodeWidget(nodes.MathNode(name="NODE 2"), self.scene)

        node1.set_position(-350, -250)
        node2.set_position(200, -150)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = NodeEditor()
    editor.show()
    sys.exit(app.exec_())