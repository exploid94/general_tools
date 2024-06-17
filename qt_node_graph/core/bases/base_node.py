from qt_node_graph.core.id import Id
from qt_node_graph.core.bases.base_attribute import _BaseAttribute
from qt_node_graph.core import attributes

class _BaseNode(Id):
    def __init__(self, name):
        super().__init__()
        self._ATTRIBUTES = {}
        self._NAME = attributes.String(name="name", value=name)
        self._TRANSFORM = attributes.FloatVector3(name="transform")

        self.add_attribute(self._NAME)
        self.add_attribute(self._TRANSFORM)

    @property
    def attributes(self):
        return self._ATTRIBUTES

    @property
    def name(self):
        return self._NAME

    def add_attribute(self, attribute):
        if isinstance(attribute, _BaseAttribute):
            if attribute.name not in self.attributes:
                self._ATTRIBUTES[attribute.name] = attribute
                return attribute
            else:
                ValueError(f"attribute {attribute.name} already exists on {self}")
        else:
            TypeError(f"attribute {attribute} is not of type {_BaseAttribute}")

    def remove_attribute(self, attribute):
        if isinstance(attribute, _BaseAttribute):
            if attribute.name not in self.attributes:
                del self.attributes[attribute.name]
                return
            else:
                ValueError(f"attribute {attribute.name} already exists on {self}")
        else:
            TypeError(f"attribute {attribute} is not of type {_BaseAttribute}")
