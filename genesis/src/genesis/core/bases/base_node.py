from genesis.core.bases import base_object
from genesis.core.objects import attributes

import importlib
importlib.reload(attributes)

class Node(base_object.BaseObject):
    def __init__(self, name, parent=None, update=True):
        self._INPUTS = []
        self._OUTPUTS = []
        super().__init__(parent=parent)

        self._NAME = attributes.String(name="name", value=name)
        self.add_attribute(self._NAME)

        self._UPDATE = attributes.Bool(name="update", value=update)
        self.add_attribute(self._UPDATE)

    @property
    def name(self):
        return self._NAME

    @property
    def update(self):
        return self._UPDATE

    @property
    def inputs(self):
        return self._INPUTS

    @property
    def outputs(self):
        return self._OUTPUTS

    def add_input(self, attr):
        self._INPUTS.append(attr)
        self.add_attribute(attr)

    def add_output(self, attr):
        self._OUTPUTS.append(attr)
        self.add_attribute(attr)

    def compute(self):
        pass