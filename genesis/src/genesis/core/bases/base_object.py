import uuid
import json

from genesis.utils import constants
from genesis.core import signal

import importlib
importlib.reload(constants)

class BaseObject(object):
    def __init__(self, parent=None, register=True):
        self._UUID = uuid.uuid4().hex
        self._PARENT = None
        self._CHILDREN = []
        self._ATTRIBUTES = []
        self._OBJECT_DATA = {}
        self._META_DATA = {}
        self._TEMP_DATA = {}

        self._PARENT_CHANGED = signal.Signal()
        self._CHILD_ADDED = signal.Signal()
        self._CHILD_REMOVED = signal.Signal()
        self._SETTING_ADDED = signal.Signal()
        self._OBJECT_DATA_CHANGED = signal.Signal()
        self._META_DATA_CHANGED = signal.Signal()
        self._TEMP_DATA_CHANGED = signal.Signal()

        if parent:
            self.set_parent(parent)

        if register:
            register_object(self)

        self.set_object_data(constants.UUID, self.uuid)
        self.set_object_data(constants.MODULE, self.__module__)
        self.set_object_data(constants.CLASS, self.__class__.__name__)

    @property
    def uuid(self):
        return self._UUID

    @property
    def parent(self):
        return self._PARENT

    @property
    def children(self):
        return self._CHILDREN

    @property
    def attributes(self):
        return self._ATTRIBUTES

    @property
    def object_data(self):
        return self._OBJECT_DATA

    @property
    def meta_data(self):
        return self._META_DATA

    @property
    def temp_data(self):
        return self._TEMP_DATA
    
    @property
    def parent_changed(self):
        return self._PARENT_CHANGED

    @property
    def child_added(self):
        return self._CHILD_ADDED

    @property
    def child_removed(self):
        return self._CHILD_REMOVED

    @property
    def attribute_added(self):
        return self._SETTING_ADDED

    @property
    def object_data_changed(self):
        return self._OBJECT_DATA_CHANGED

    @property
    def meta_data_changed(self):
        return self._META_DATA_CHANGED

    @property
    def temp_data_changed(self):
        return self._TEMP_DATA_CHANGED

    def add_child(self, child):
        if not child in self.children:
            self._CHILDREN.append(child)
            self.child_added.emit(child=child)
    
    def remove_child(self, child):
        if child in self.children:
            self._CHILDREN.pop(child)
            self.child_removed(child=child)

    def set_parent(self, parent):
        previous_parent = self.parent
        # remove from previous parent first
        if previous_parent:
            previous_parent.remove_child(self)

        # now set parent and add it a child of said parent
        self._PARENT = parent
        if self.parent != previous_parent:
            self.parent_changed.emit(parent=parent)
        parent.add_child(self)

    def add_attribute(self, attribute):
        if attribute not in self._ATTRIBUTES:
            self._ATTRIBUTES.append(attribute)
            attribute.set_parent(self)
            self.attribute_added.emit(attribute=attribute)
        return attribute

    def set_object_data(self, key, value):
        try:
            json.dumps(key)
            json.dumps(value)
        except Exception:
            raise

        if not isinstance(key, str):
            raise Exception(f"Object data key must be a string! Got {type(key)}")
        
        previous_data = self.object_data.get(key)
        self._OBJECT_DATA[key] = value
        if value != previous_data:
            self.object_data_changed.emit(key=key, value=value)

    def set_meta_data(self, key, value):
        try:
            json.dumps(key)
            json.dumps(value)
        except Exception:
            raise

        if not isinstance(key, str):
            raise Exception(f"Metadata key must be a string! Got {type(key)}")

        previous_data = self.meta_data.get(key)
        self._META_DATA[key] = value
        if value != previous_data:
            self.meta_data_changed.emit(key=key, value=value)
    
    def set_temp_data(self, key, value):
        previous_data = self.temp_data.get(key)
        self._TEMP_DATA[key] = value
        if value != previous_data:
            self.temp_data_changed.emit(key=key, value=value)

    def serialize(self):
        children = []
        for child in self.children:
            children.append(child.serialize())
        self.set_object_data(constants.CHILDREN, children)

        attributes = []
        for attribute in self.attributes:
            attributes.append(attribute.serialize())
        self.set_object_data(constants.ATTRIBUTES, attributes)

        return self._OBJECT_DATA


def deserialize(object_data):
    # get the object_id data
    object_uuid = object_data[constants.UUID]
    module_dir = object_data[constants.MODULE]
    class_name = object_data[constants.CLASS]
    children = object_data[constants.CHILDREN]
    attributes = object_data[constants.ATTRIBUTES]

    # remove the object_id data
    object_data.pop(constants.UUID)
    object_data.pop(constants.MODULE)
    object_data.pop(constants.CLASS)
    object_data.pop(constants.CHILDREN)
    object_data.pop(constants.ATTRIBUTES)

    # import the module and new class instance object
    module = importlib.import_module(module_dir)
    class_instance = getattr(module, class_name)
    if class_instance:
        new_object = class_instance(**object_data)
        # set the original uuid as meta data for debugging
        new_object.set_meta_data(constants.FROM_UUID, object_uuid)

        # deserialize children
        for child in children:
            deserialized_child = deserialize(child)
            deserialized_child.set_parent(new_object)

        # deserialize attributes
        for attribute in attributes:
            deserialized_attribute = deserialize(attribute)
            new_object.add_attribute(deserialized_attribute)
        return new_object

_OBJECTS = {}

def register_object(obj: BaseObject):
    _OBJECTS[obj.uuid] = obj

def deregister_object(obj: BaseObject):
    _OBJECTS.pop(obj.uuid)

def get_objects():
    return _OBJECTS

def find_object(uuid: uuid):
    return _OBJECTS.get(uuid, None)

def flush():
    _OBJECTS.clear()
