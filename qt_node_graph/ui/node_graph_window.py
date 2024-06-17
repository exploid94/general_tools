from qt_window.main_window import MainWindow
from qt_node_graph.ui.node_widgets import NodeWidget
from qt_node_graph.core import nodes

from PyQt5 import QtWidgets, QtCore, QtGui
import sys
import os

class NodeGraphWindow(MainWindow):
    def __init__(self, parent=None, title="Node Graph"):
        super().__init__(parent, title)

        # create a splitter
        self.splitter = QtWidgets.QSplitter()
        self.main_layout.addWidget(self.splitter)

        # create the tab widgets
        self.tab_widget = QtWidgets.QTabWidget()
        self.nodes_widget = NodesList()
        self.attr_widget = QtWidgets.QWidget()
        self.tab_widget.addTab(self.nodes_widget, "Nodes")
        self.tab_widget.addTab(self.attr_widget, "Attributes")

        self.splitter.addWidget(self.tab_widget)

        # create the node editor
        self.node_view = NodeView()
        self.splitter.addWidget(self.node_view)

        self._set_splitter_pos(self.splitter)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)

        self.resize(1200, 800)

    def _set_splitter_pos(self, splitter, ratio=0.5):
        if splitter.orientation() == QtCore.Qt.Horizontal:
            splitter.moveSplitter(int(self.width() * ratio), 1)
        else:
            splitter.moveSplitter(int(self.height() * ratio), 1)


class NodeView(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        super(NodeView, self).__init__(parent)

        self._PANNING = False

        self._ZOOM_MIN = -10
        self._ZOOM_MAX = 10
        self._ZOOM = 0.0

        self._panning = None
        self._pan_start_x = None
        self._pan_start_y = None

        self.setScene(NodeScene(parent=self))
        self._SCENE_RANGE = QtCore.QRectF(0, 0, self.size().width(), self.size().height())

        self.setRenderHint(QtGui.QPainter.Antialiasing, True)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)
        self.setCacheMode(QtWidgets.QGraphicsView.CacheBackground)
        self.setOptimizationFlag(QtWidgets.QGraphicsView.DontAdjustForAntialiasing)

    @property
    def zoom(self):
        return self._ZOOM

    @property
    def zoom_min(self):
        return self._ZOOM_MIN

    @property
    def zoom_max(self):
        return self._ZOOM_MAX

    @property
    def scene_range(self):
        return self._SCENE_RANGE

    def _update_scene(self):
        self.setSceneRect(self.scene_range)
        self.fitInView(self.scene_range, QtCore.Qt.KeepAspectRatio)

    def _set_viewer_pan(self, pos_x, pos_y):
        self.scene_range.translate(pos_x, pos_y)
        self._update_scene()

    def _get_pan_value(self):
        if self.zoom > 1:
            return 1 / self.zoom
        elif self.zoom == 0:
            return 1
        else:
            return abs(self.zoom) / 2

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MiddleButton:
            self._panning = True
            self._pan_start_x = event.x()
            self._pan_start_y = event.y()
            self.setCursor(QtCore.Qt.ClosedHandCursor)
            event.accept()
            return
        if event.button() == QtCore.Qt.LeftButton:
            pass

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MiddleButton:
            self._panning = False
            self.setCursor(QtCore.Qt.ArrowCursor)
            event.accept()
            return

    def mouseMoveEvent(self, event):
        if self._panning:
            x = (self.horizontalScrollBar().value() - (event.x() - self._pan_start_x)) * self._get_pan_value()
            y = (self.verticalScrollBar().value() - (event.y() - self._pan_start_y)) * self._get_pan_value()
            self._set_viewer_pan(x, y)
            self._pan_start_x = event.x()
            self._pan_start_y = event.y()
            return

    def scale(self, sx, sy, pos=None):
        scale = [sx, sx]
        center = pos or self.scene_range.center()
        x = center.x() - (center.x() - self.scene_range.left()) / scale[0]
        y = center.y() - (center.y() - self.scene_range.top()) / scale[1]
        w = self.scene_range.width() / scale[0]
        h = self.scene_range.height() / scale[1]
        self.scene_range.setRect(x, y, w, h)
        self._update_scene()

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            factor = 1.25
            self._ZOOM += 1
            if self.zoom > self.zoom_max:
                factor = 1.0
                self._ZOOM = self.zoom_max
        else:
            factor = 0.8
            self._ZOOM -= 1
            if self.zoom < self.zoom_min:
                factor = 1.0
                self._ZOOM = self.zoom_min

        self.scale(factor, factor, self.mapToScene(event.pos()))

    def add_node(self, node):
        self.scene().addItem(node)


class NodeScene(QtWidgets.QGraphicsScene):
    def __init__(self, parent=None):
        super(NodeScene, self).__init__(parent)

        self._GRID_SIZE = 50
        self._GRID_COLOR = "gray"
        self._BACKGROUND_COLOR = "dimgray"

        self.setBackgroundBrush(QtGui.QColor(self._BACKGROUND_COLOR))

    @property
    def grid_size(self):
        return self._GRID_SIZE

    @property
    def grid_color(self):
        return self._GRID_COLOR

    @property
    def background_color(self):
        return self._BACKGROUND_COLOR

    def viewer(self):
        return self.views()[0] if self.views() else None

    @staticmethod
    def _draw_grid(painter, rect, pen, grid_size):
        left = int(rect.left())
        right = int(rect.right())
        top = int(rect.top())
        bottom = int(rect.bottom())

        first_left = left - (left % grid_size)
        first_top = top - (top % grid_size)

        lines = []
        lines.extend([
            QtCore.QLineF(x, top, x, bottom)
            for x in range(first_left, right, grid_size)
        ])
        lines.extend([
            QtCore.QLineF(left, y, right, y)
            for y in range(first_top, bottom, grid_size)]
        )

        painter.setPen(pen)
        painter.drawLines(lines)

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)

        painter.save()
        painter.setRenderHint(QtGui.QPainter.Antialiasing, False)
        painter.setBrush(self.backgroundBrush())

        zoom = self.viewer().zoom
        if zoom > 0:
            pen = QtGui.QPen(QtGui.QColor(self.grid_color), 0.65)
            self._draw_grid(painter, rect, pen, self.grid_size)

        color = QtGui.QColor(self.background_color).darker(200)
        if zoom < 0:
            color = color.darker(100 - int(zoom * 110))
        pen = QtGui.QPen(color, 0.65)
        self._draw_grid(painter, rect, pen, self.grid_size * 8)

        painter.restore()

    def mousePressEvent(self, event):
        selected_nodes = self.selectedItems()
        print(event, selected_nodes)
        super(NodeScene, self).mousePressEvent(event)


class NodesList(QtWidgets.QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        for node in nodes.get_all_nodes():
            item = QtWidgets.QListWidgetItem(node)
            self.addItem(item)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    win = NodeGraphWindow()
    win.show()

    sys.exit(app.exec_())
