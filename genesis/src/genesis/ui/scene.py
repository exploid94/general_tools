from genesis.ui import widgets

import importlib
importlib.reload(widgets)

class Scene:
    def __init__(self):
        self.nodes = []
        self.edges = []

        self.width = 32000
        self.height = 32000

        self._init_ui()

    def _init_ui(self):
        self.graphics_scene = widgets.GraphicsScene(self)
        self.graphics_scene.setScene(self.width, self.height)

    def add_node(self, node):
        self.nodes.append(node)

    def remove_node(self, node):
        self.nodes.remove(node)

    def add_edge(self, edge):
        self.edges.append(edge)

    def remove_edge(self, edge):
        self.edges.remove(edge)