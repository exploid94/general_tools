import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from genesis.ui import widgets, scene
from genesis.core.objects import nodes, attributes

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
        node1 = widgets.NodeWidget(nodes.StringNode(value="Hello World!"), self.scene)
        node2 = widgets.NodeWidget(nodes.MathNode(), self.scene)
        node3 = widgets.NodeWidget(nodes.FloatNode(), self.scene)

        node1.set_position(-350, -250)
        node2.set_position(200, -150)
        node3.set_position(-50, -100)


class AttributeEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setMinimumWidth(250)

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.attribute_layout = QFormLayout()
        self.main_layout.addLayout(self.attribute_layout)

        self.main_layout.addStretch()

    def update_attributes(self, node=None):

        # remove all rows first
        for i in reversed(range(self.attribute_layout.count())):
            remove = self.attribute_layout.itemAt(i).widget()
            self.attribute_layout.removeWidget(remove)
            remove.setParent(None)

        if node:
            # add all attrs from the node
            for attribute in node.attributes:
                widget = None
                if type(attribute) is attributes.String:
                    widget = self._create_string_widget(attribute)
                    if attribute is node.name:
                        widget.textChanged.connect(lambda: node.widget.graphics_node.set_title(node.name.value))
                if type(attribute) is attributes.Bool:
                    widget = self._create_bool_widget(attribute)
                if type(attribute) is attributes.Integer:
                    widget = self._create_int_widget(attribute)
                if type(attribute) is attributes.Float:
                    widget = self._create_float_widget(attribute)
                if type(attribute) is attributes.Enum:
                    widget = self._create_enum_widget(attribute)

                if attribute in node.outputs:
                    self._update_outputs(attribute, widget)


    def _update_outputs(self, attribute, widget):
        if type(attribute) is attributes.String:
            attribute.value_changed.connect(lambda: widget.setText(attribute.value))
        if type(attribute) is attributes.Bool:
            attribute.value_changed.connect(lambda: widget.setState(attribute.value))
        if type(attribute) is attributes.Integer:
            attribute.value_changed.connect(lambda: widget.setValue(attribute.value))
        if type(attribute) is attributes.Float:
            attribute.value_changed.connect(lambda: widget.setValue(attribute.value))
        if type(attribute) is attributes.Enum:
            attribute.value_changed.connect(lambda: widget.setCurrentText(attribute.value))

    def _add_attr_widget(self, attribute, widget):
        name = QLabel(f"{attribute.name}:")
        if attribute.locked:
            widget.setEnabled(False)
        self.attribute_layout.addRow(name, widget)


    def _create_string_widget(self, attribute):
        widget = QLineEdit(attribute.value)
        widget.textChanged.connect(lambda: attribute.set(widget.text(), force=True))
        self._add_attr_widget(attribute, widget)
        return widget

    def _create_bool_widget(self, attribute):
        widget = QCheckBox()
        widget.setChecked(attribute.value)
        widget.stateChanged.connect(lambda: attribute.set(widget.isChecked(), force=True))
        self._add_attr_widget(attribute, widget)
        return widget

    def _create_int_widget(self, attribute):
        widget = QSpinBox()
        widget.setValue(attribute.value)
        widget.valueChanged.connect(lambda: attribute.set(widget.value(), force=True))
        self._add_attr_widget(attribute, widget)
        return widget

    def _create_float_widget(self, attribute):
        widget = QDoubleSpinBox()
        widget.setValue(attribute.value)
        widget.valueChanged.connect(lambda: attribute.set(widget.value(), force=True))
        self._add_attr_widget(attribute, widget)
        return widget

    def _create_enum_widget(self, attribute):
        widget = QComboBox()
        widget.addItems(attribute.options)
        widget.setCurrentText(attribute.value)
        widget.currentIndexChanged.connect(lambda: attribute.set(widget.currentText(), force=True))
        self._add_attr_widget(attribute, widget)
        return widget


class MainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Node Editor")

        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)

        self.node_editor = NodeEditor()
        self.attribute_editor = AttributeEditor()

        self.main_layout.addWidget(self.node_editor)
        self.main_layout.addWidget(self.attribute_editor)

        self.node_editor.scene.graphics_scene.selectionChanged.connect(self._update_attribute_editor)

    def _update_attribute_editor(self):
        selected = self.node_editor.scene.graphics_scene.selectedItems()
        filter_selected = [i for i in selected if isinstance(i, widgets.GraphicsNode)]
        if filter_selected:
            self.attribute_editor.update_attributes(selected[0].node_widget.node)
        else:
            self.attribute_editor.update_attributes(None)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = MainWindow()
    editor.show()
    sys.exit(app.exec_())