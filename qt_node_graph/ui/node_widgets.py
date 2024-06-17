from PyQt5 import QtWidgets

from qt_node_graph.utils import constants


class NodeWidget(QtWidgets.QGraphicsProxyWidget):
    def __init__(self, node, parent=None, name=None, label=''):
        super().__init__(parent)
        self._NAME = name
        self._LABEL = label
        self._NODE = node

        self._MAIN_LAYOUT = QtWidgets.QFormLayout()

        self._GROUP_BOX = QtWidgets.QGroupBox()
        self._GROUP_BOX.setTitle(name)
        self._GROUP_BOX.setLayout(self._MAIN_LAYOUT)

        self.setWidget(self._GROUP_BOX)
        self.setZValue(constants.Z_VALUE_NODE)

        self._init_attributes()

    @property
    def name(self):
        return self._NAME

    @property
    def label(self):
        return self._LABEL

    @property
    def node(self):
        return self._NODE

    @property
    def main_layout(self):
        return self._MAIN_LAYOUT

    @property
    def group_box(self):
        return self._GROUP_BOX

    def _init_attributes(self):
        for attr in self.node.attributes.values():
            self.add_attribute(attr)

    def add_attribute(self, attribute):
        return attribute
