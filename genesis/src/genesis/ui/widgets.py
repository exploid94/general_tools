import math
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from genesis.core.objects import nodes

class GraphicsScene(QGraphicsScene):
    def __init__(self, scene, parent=None):
        super().__init__(parent)

        self.scene = scene

        self._background_color = QColor("#393939")
        self._line_color_light = QColor("#2f2f2f")
        self._line_color_dark = QColor("#292929")

        self._pen_light = QPen(self._line_color_light)
        self._pen_light.setWidth(1)
        self._pen_dark = QPen(self._line_color_dark)
        self._pen_dark.setWidth(2)

        self.grid_size = 20
        self.grid_square = 5

        self.setBackgroundBrush(self._background_color)

    def setScene(self, width, height):
        self.setSceneRect(-width // 2, -height // 2, width, height)

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)

        left = int(math.floor(rect.left()))
        right = int(math.ceil(rect.right()))
        top = int(math.floor(rect.top()))
        bottom = int(math.ceil(rect.bottom()))

        first_left = left - (left % self.grid_size)
        first_top = top - (top % self.grid_size)

        lines_light, lines_dark = [], []
        for x in range(first_left, right, self.grid_size):
            if (x % (self.grid_size * self.grid_square) != 0):
                lines_light.append(QLine(x, top, x, bottom))
            else:
                lines_dark.append(QLine(x, top, x, bottom))

        for y in range(first_top, bottom, self.grid_size):
            if (y % (self.grid_size * self.grid_square) != 0):
                lines_light.append(QLine(left, y, right, y))
            else:
                lines_dark.append(QLine(left, y, right, y))

        if lines_light:
            painter.setPen(self._pen_light)
            painter.drawLines(*lines_light)
        if lines_dark:
            painter.setPen(self._pen_dark)
            painter.drawLines(*lines_dark)

class GraphicsView(QGraphicsView):
    MODE_NONE = 0
    MODE_EDGE_DRAG = 1
    def __init__(self, graphics_scene, parent=None):
        super().__init__(parent)
        self.graphics_scene = graphics_scene

        self._init_ui()

        self.setScene(self.graphics_scene)

        self.zoom_factor = 1.25
        self.zoom_clamp = True
        self.zoom = 10
        self.zoom_step = 1
        self.zoom_range = [0, 20]

        self.mode = self.MODE_NONE

    def _init_ui(self):
        self.setRenderHints(QPainter.Antialiasing | QPainter.HighQualityAntialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)

        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

        self.setDragMode(QGraphicsView.RubberBandDrag)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.delete_selected()
        if event.key() == Qt.Key_Tab:
            NodeSearch(self.pos_x, self.pos_y, self.graphics_scene.scene, parent=self)
        else:
            super().keyPressEvent(event)

    def delete_selected(self):
        selected_edges = [i for i in self.graphics_scene.selectedItems() if isinstance(i, GraphicsEdge)]
        selected_nodes = [i for i in self.graphics_scene.selectedItems() if isinstance(i, GraphicsNode)]
        for item in (selected_edges + selected_nodes):
            if isinstance(item, GraphicsEdge):
                item.edge.remove()
            elif isinstance(item, GraphicsNode):
                item.node_widget.remove()

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonPress(event)
        elif event.button() == Qt.LeftButton:
            self.leftMouseButtonPress(event)
        elif event.button() == Qt.RightButton:
            self.rightMouseButtonPress(event)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonRelease(event)
        elif event.button() == Qt.LeftButton:
            self.leftMouseButtonRelease(event)
        elif event.button() == Qt.RightButton:
            self.rightMouseButtonRelease(event)
        else:
            super().mouseReleaseEvent(event)

    def middleMouseButtonPress(self, event):
        release_event = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(), Qt.LeftButton, Qt.NoButton, event.modifiers())
        super().mouseReleaseEvent(release_event)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        fake_event = QMouseEvent(event.type(), event.localPos(), event.screenPos(), Qt.LeftButton, event.buttons() | Qt.LeftButton, event.modifiers())
        super().mousePressEvent(fake_event)

    def middleMouseButtonRelease(self, event):
        fake_event = QMouseEvent(event.type(), event.localPos(), event.screenPos(), Qt.LeftButton, event.buttons() | Qt.LeftButton, event.modifiers())
        super().mouseReleaseEvent(fake_event)
        self.setDragMode(QGraphicsView.NoDrag)

    def leftMouseButtonPress(self, event):
        item = self.get_item_at_click(event)
        self.held_click_item = None
        self.temp_edge = None

        if type(item) is GraphicsSocket:
            if self.mode == self.MODE_NONE:
                self.mode = self.MODE_EDGE_DRAG
                self.held_click_item = item
                self.temp_edge = EdgeWidget(self.graphics_scene.scene, self.held_click_item.socket_widget, None, is_temp=True)
                return

        if self.mode == self.MODE_EDGE_DRAG:
            self.mode = self.MODE_NONE
            if type(item) is GraphicsSocket:
                return

        super().mousePressEvent(event)

    def leftMouseButtonRelease(self, event):
        item = self.get_item_at_click(event)

        if self.mode == self.MODE_EDGE_DRAG:
            self.mode = self.MODE_NONE
            if self.temp_edge:
                self.temp_edge.remove()
            if type(item) is GraphicsSocket:
                if self.held_click_item and (self.held_click_item != item):
                    # don't allow output to output or input to input
                    if (self.held_click_item.socket_widget in self.held_click_item.socket_widget.node_widget.inputs) and (item.socket_widget in item.socket_widget.node_widget.inputs):
                        return
                    elif (self.held_click_item.socket_widget in self.held_click_item.socket_widget.node_widget.outputs) and (item.socket_widget in item.socket_widget.node_widget.outputs):
                        return
                    else:
                        # only allow same socket types
                        if self.held_click_item.socket_widget.socket_color is item.socket_widget.socket_color:
                            EdgeWidget(self.graphics_scene.scene, self.held_click_item.socket_widget, item.socket_widget)
                        else:
                            return
                return
        self.held_click_item = None

        super().mouseReleaseEvent(event)

    def rightMouseButtonPress(self, event):
        item = self.get_item_at_click(event)
        if type(item) is GraphicsEdge:
            item.edge.remove()
        super().mousePressEvent(event)

    def rightMouseButtonRelease(self, event):
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        self.pos_x = event.pos().x()
        self.pos_y = event.pos().y()
        if self.mode == self.MODE_EDGE_DRAG:
            pos = self.mapToScene(event.pos())
            if self.temp_edge:
                self.temp_edge.graphics_edge.set_dest(pos.x(), pos.y())
                self.temp_edge.graphics_edge.update()
        super().mouseMoveEvent(event)

    def wheelEvent(self, event):
        zoom_out_factor = 1 / self.zoom_factor

        if event.angleDelta().y() > 0:
            zoom_factor = self.zoom_factor
            self.zoom += self.zoom_step
        else:
            zoom_factor = zoom_out_factor
            self.zoom -= self.zoom_step

        clamped = False
        if self.zoom < self.zoom_range[0]:
            self.zoom = self.zoom_range[0]
            clamped = True
        if self.zoom > self.zoom_range[1]:
            self.zoom = self.zoom_range[1]
            clamped = True

        if not clamped or self.zoom_clamp is False:
            self.scale(zoom_factor, zoom_factor)

    def get_item_at_click(self, event):
        pos = event.pos()
        obj = self.itemAt(pos)
        return obj

class GraphicsNode(QGraphicsItem):
    def __init__(self, node_widget, parent=None):
        super().__init__(parent)
        self.node_widget = node_widget
        self._title = node_widget.title
        self._title_color = Qt.white
        self._title_font = QFont("Ubuntu", 10)

        self.width = 180
        self.height = 240
        self.edge_size = 10.0
        self.title_height = 24.0
        self._padding = 4.0

        self._pen_default = QPen(QColor("#7f000000"))
        self._pen_selected = QPen(QColor("#FFFFA637"))

        self._brush_title = QBrush(QColor("#FF313131"))
        self._brush_background = QBrush(QColor("#E3212121"))

        self._init_title()
        self.set_title(node_widget.title)

        self._init_sockets()

        self._init_ui()

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        self.node_widget.update_connected_edges()


    @property
    def title(self):
        return self._title

    def set_title(self, title):
        self._title = title
        self.title_item.setPlainText(self._title)

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height).normalized()

    def _init_ui(self):
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)

    def _init_title(self):
        self.title_item = QGraphicsTextItem(self)
        self.title_item.setDefaultTextColor(self._title_color)
        self.title_item.setFont(self._title_font)
        self.title_item.setPos(self._padding, 0)
        self.title_item.setTextWidth(self.width - 2 * self._padding)

    def _init_sockets(self):
        pass

    def paint(self, painter, option, widget=None):
        # title
        path_title = QPainterPath()
        path_title.setFillRule(Qt.WindingFill)
        path_title.addRoundedRect(0, 0, self.width, self.title_height, self.edge_size, self.edge_size)
        path_title.addRect(0, self.title_height - self.edge_size, self.edge_size, self.edge_size)
        path_title.addRect(self.width - self.edge_size, self.title_height - self.edge_size, self.edge_size, self.edge_size)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._brush_title)
        painter.drawPath(path_title.simplified())

        # content
        path_content = QPainterPath()
        path_content.setFillRule(Qt.WindingFill)
        path_content.addRoundedRect(0, self.title_height, self.width, self.height - self.title_height, self.edge_size, self.edge_size)
        path_content.addRect(0, self.title_height, self.edge_size, self.edge_size)
        path_content.addRect(self.width - self.edge_size, self.title_height, self.edge_size, self.edge_size)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._brush_background)
        painter.drawPath(path_content.simplified())

        # outline
        path_outline = QPainterPath()
        path_outline.addRoundedRect(0, 0, self.width, self.height, self.edge_size, self.edge_size)
        painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path_outline.simplified())

class GraphicsSocket(QGraphicsItem):
    def __init__(self, socket_widget, color="#FFFF7700", parent=None):
        super().__init__(parent)
        self.socket_widget = socket_widget
        self.radius = 6
        self.outline_width = 1

        self._color_background = QColor(color)
        self._color_outline = QColor("#FF000000")

        self._pen = QPen(self._color_outline)
        self._pen.setWidthF(self.outline_width)
        self._brush = QBrush(self._color_background)

        self.text_item = QGraphicsTextItem(self.socket_widget.attribute.name, self)
        self.text_item.setDefaultTextColor(QColor("white"))
        if self.socket_widget.attribute in self.socket_widget.node_widget.node.inputs:
            self.text_item.setPos(self.pos().x() + self.radius * 2, self.pos().y() - self.radius * 2)
        else:
            # todo this is not perfect but it works for now. the x value gets further away the longer the word
            self.text_item.setPos(self.pos().x() - self.radius * (2 + len(self.socket_widget.attribute.name)), self.pos().y() - self.radius * 2)

    def paint(self, painter, option, widget=None):
        painter.setBrush(self._brush)
        painter.setPen(self._pen)
        painter.drawEllipse(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius)

    def boundingRect(self):
        return QRectF(-self.radius - self.outline_width,
                      -self.radius - self.outline_width,
                      2 * (self.radius + self.outline_width),
                      2 * (self.radius + self.outline_width))

class GraphicsEdge(QGraphicsPathItem):
    DIRECT = 0
    BEZIER = 1
    def __init__(self, edge, parent=None, edge_type=BEZIER):
        super().__init__(parent)
        self.edge = edge
        self.edge_type = edge_type

        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setZValue(-1)

        self._color = QColor("#001000")
        self._color_selected = QColor("#00ff00")

        self._pen = QPen(self._color)
        self._pen.setWidthF(2.0)
        self._pen_selected = QPen(self._color_selected)
        self._pen_selected.setWidthF(2.0)
        self._pen_drag = QPen(self._color)
        self._pen_drag.setWidthF(2.0)
        self._pen_drag.setStyle(Qt.DashLine)

        self._brush = QBrush(self._color)

        self.source_position = [0, 0]
        self.dest_position = [200, 100]

    def set_source(self, x, y):
        self.source_position = [x, y]

    def set_dest(self, x, y):
        self.dest_position = [x, y]

    def paint(self, painter, option, widget=None):
        self.update_path()

        if self.edge.end_socket is None:
            painter.setPen(self._pen_drag)
        else:
            painter.setPen(self._pen if not self.isSelected() else self._pen_selected)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(self.path())

    def update_path(self):
        if self.edge_type is self.DIRECT:
            path = QPainterPath(QPointF(self.source_position[0], self.source_position[1]))
            path.lineTo(self.dest_position[0], self.dest_position[1])
            self.setPath(path)
        elif self.edge_type is self.BEZIER:
            s = self.source_position
            d = self.dest_position
            dist = (d[0] - s[0]) * 0.5
            if s[0] > d[0]:
                dist *= -1

            path = QPainterPath(QPointF(self.source_position[0], self.source_position[1]))
            path.cubicTo(s[0] + dist, s[1], d[0] - dist, d[1], self.dest_position[0], self.dest_position[1])
            self.setPath(path)



class NodeSearch(QWidget):
    def __init__(self, x, y, scene, w=200, h=150, parent=None):
        super().__init__(parent)
        self.scene = scene

        self.setFixedWidth(w)
        self.setFixedHeight(h)
        self.setGeometry(x, y, w, h)

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.search_bar = SearchBar(self)
        self.list_widget = QListWidget(self)
        self.list_widget.addItems(nodes.get_nodes().keys())

        self.main_layout.addWidget(self.search_bar)
        self.main_layout.addWidget(self.list_widget)

        self.list_widget.itemDoubleClicked.connect(self.create_node)
        self.search_bar.textChanged.connect(self.filter_nodes)

        self.list_widget.setFocusProxy(self)
        self.setFocusProxy(self.search_bar)
        self.search_bar.setFocus(True)

        self.show()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        if not self.hasFocus():
            self.deleteLater()

    def create_node(self, item):
        node = nodes.create_node(item.text())
        NodeWidget(node, self.scene)
        self.deleteLater()

    def filter_nodes(self):
        text = self.search_bar.text()
        for x in range(self.list_widget.count()):
            item = self.list_widget.item(x)
            if text in item.text():
                item.setHidden(False)
            else:
                item.setHidden(True)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            self.list_widget.setCurrentRow(max(self.list_widget.currentRow() - 1, 0))
        if event.key() == Qt.Key_Down:
            self.list_widget.setCurrentRow(min(self.list_widget.currentRow() + 1, self.list_widget.count()))
        if event.key() == Qt.Key_Return:
            self.create_node(self.list_widget.item(self.list_widget.currentRow()))
        if event.key() == Qt.Key_Tab:
            self.list_widget.setCurrentRow(min(self.list_widget.currentRow() + 1, self.list_widget.count()))
        if event.key() == Qt.Key_Escape:
            self.deleteLater()


class SearchBar(QLineEdit):
    def focusOutEvent(self, widget):
        super().focusOutEvent(widget)
        self.parent().deleteLater()


LEFT_TOP = 1
LEFT_BOTTOM = 2
RIGHT_TOP = 3
RIGHT_BOTTOM = 4
class NodeWidget:
    def __init__(self, node, scene):
        self.scene = scene
        self.node = node
        self.title = node.name.get()
        self.node.widget = self

        self.graphics_node = GraphicsNode(self)

        self.scene.add_node(self)
        self.scene.graphics_scene.addItem(self.graphics_node)

        self.socket_spacing = 22

        self.inputs = []
        self.outputs = []

        for x, attr in enumerate(self.node.inputs):
            self.inputs.append(SocketWidget(self, attr, index=x, position=LEFT_TOP))

        for x, attr in enumerate(self.node.outputs):
            self.outputs.append(SocketWidget(self, attr, index=x, position=RIGHT_TOP))

    @property
    def position(self):
        return self.graphics_node.pos()

    def set_position(self, x, y):
        self.graphics_node.setPos(x, y)

    def get_socket_position(self, index, position):
        x = 0 if (position in (LEFT_TOP, LEFT_BOTTOM)) else self.graphics_node.width

        if position in (LEFT_BOTTOM, RIGHT_BOTTOM):
            y = self.graphics_node.height - self.graphics_node.edge_size - self.graphics_node._padding -  index * self.socket_spacing
        else:
            y = self.graphics_node.title_height + self.graphics_node._padding + self.graphics_node.edge_size + index * 20
        return [x, y]

    def update_connected_edges(self):
        for socket in self.inputs + self.outputs:
            if socket.has_edge():
                socket.edge.update_positions()

    def remove(self):
        for socket in (self.inputs + self.outputs):
            if socket.has_edge():
                socket.edge.remove()
        self.scene.graphics_scene.removeItem(self.graphics_node)
        self.graphics_node = None
        self.scene.remove_node(self)

class SocketWidget:
    def __init__(self, node_widget, attr, index=0, position=LEFT_TOP):
        self.node_widget = node_widget
        self.attribute = attr
        self.index = index
        self.position = position
        self.socket_type = self.attribute.data_type

        self._init_socket_type()

        self.graphics_socket = GraphicsSocket(self, color=self.socket_color, parent=self.node_widget.graphics_node)
        self.graphics_socket.setPos(*self.node_widget.get_socket_position(index, position))

        self.edge = None

    def _init_socket_type(self):
        if self.attribute.data_type is str:
            self.socket_color = "green"
        elif self.attribute.data_type is bool:
            self.socket_color = "darkOrange"
        elif self.attribute.data_type is int:
            self.socket_color = "blue"
        elif self.attribute.data_type is float:
            self.socket_color = "cyan"
        else:
            self.socket_color = "black"

    def get_socket_position(self):
        return self.node_widget.get_socket_position(self.index, self.position)

    def set_connected_edge(self, edge=None):
        self.edge = edge

    def has_edge(self):
        return True if self.edge else False

class EdgeWidget:
    def __init__(self, scene, start_socket, end_socket, is_temp=False):
        self.scene = scene
        self.start_socket = start_socket
        self.end_socket = end_socket
        self.is_temp = is_temp

        self.start_socket.set_connected_edge(self)
        if self.end_socket:
            self.end_socket.set_connected_edge(self)

        self.graphics_edge = GraphicsEdge(self)
        self.update_positions()

        self.scene.graphics_scene.addItem(self.graphics_edge)

        self.scene.add_edge(self)

        if not self.is_temp:
            self.end_socket.attribute.connect(self.start_socket.attribute)

    def update_positions(self):
        source_pos = self.start_socket.get_socket_position()
        source_pos[0] += self.start_socket.node_widget.graphics_node.pos().x()
        source_pos[1] += self.start_socket.node_widget.graphics_node.pos().y()
        self.graphics_edge.set_source(*source_pos)
        if self.end_socket is not None:
            end_pos = self.end_socket.get_socket_position()
            end_pos[0] += self.end_socket.node_widget.graphics_node.pos().x()
            end_pos[1] += self.end_socket.node_widget.graphics_node.pos().y()
            self.graphics_edge.set_dest(*end_pos)
        else:
            self.graphics_edge.set_dest(*source_pos)
        self.graphics_edge.update()

    def remove_from_socket(self):
        if self.start_socket is not None:
            self.start_socket.edge = None
        if self.end_socket is not None:
            self.end_socket.edge = None
        self.start_socket = None
        self.end_socket = None

    def remove(self):
        if not self.is_temp:
            self.end_socket.attribute.disconnect()
        self.remove_from_socket()
        self.scene.graphics_scene.removeItem(self.graphics_edge)
        self.graphics_edge = None
        self.scene.remove_edge(self)
