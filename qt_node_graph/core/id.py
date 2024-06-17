from hh_publishers.api.utils import constants
from qt_node_graph.core.signal import Signal
import uuid
import json
import importlib


class Id(object):
    def __init__(self):
        self._UUID = uuid.uuid4().hex
        self._OBJECT_DATA = {}
        self._META_DATA = {}
        self._TEMP_DATA = {}
        self._OBJECT_DATA_CHANGED = Signal(name=f"{self._UUID}.object_data_changed")
        self._META_DATA_CHANGED = Signal(name=f"{self._UUID}.meta_data_changed")
        self._TEMP_DATA_CHANGED = Signal(name=f"{self._UUID}.temp_data_changed")

        self.set_meta_data(constants.META_DATA.UUID, self.uuid)
        self.set_object_data(constants.OBJECT_DATA.META_DATA, self._META_DATA)

    def __del__(self):
        try:
            remove(self.uuid)
        except:
            pass

    @property
    def uuid(self):
        return self._UUID

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
    def object_data_changed(self):
        """Emission: object_data_changed.emit(key, value)."""
        return self._OBJECT_DATA_CHANGED

    @property
    def meta_data_changed(self):
        """Emission: meta_data_changed.emit(key, value)."""
        return self._META_DATA_CHANGED

    @property
    def temp_data_changed(self):
        """Emission: temp_data_changed.emit(key, value)."""
        return self._TEMP_DATA_CHANGED

    def serialize(self):
        return {key: value for key, value in self._OBJECT_DATA.items()}

    def set_object_data(self, key, value):
        """Assigns a key and value to the object data. Generally this is used to store the flags
        needed to initialize an object. For instance, creating an asset or setting requires a name flag.
        for those objects we run set_object_data("name", name_of_object). Object data contains the meta data.
        This is serialized

        Args:
            key (str): The name to give the key.
            value (Any): The value for the key.
        """
        try:
            json.dumps(value)
        except Exception:
            raise

        if not isinstance(key, str):
            raise Exception(f"Object data key must be a string! Got {type(key)}")

        self._OBJECT_DATA[key] = value
        self.object_data_changed.emit(key=key, value=value)

    def get_object_data(self, key):
        if key not in self._OBJECT_DATA.keys():
            return None
        return self._OBJECT_DATA[key]

    def set_meta_data(self, key, value):
        """Assigns a key and value to the meta data. Meta data differs from object data in that you
        can store any extra information thats not needed to rebuild the object. This is serialized.

        Args:
            key (str): The name to give the key.
            value (Any): The value for the key.
        """
        try:
            json.dumps(value)
        except Exception:
            raise

        if not isinstance(key, str):
            raise Exception(f"Metadata key must be a string! Got {type(key)}")

        self._META_DATA[key] = value
        self.meta_data_changed.emit(key=key, value=value)
        self.set_object_data(constants.OBJECT_DATA.META_DATA, self._META_DATA)

    def get_meta_data(self, key):
        if key not in self._META_DATA.keys():
            return None
        return self._META_DATA[key]

    def set_temp_data(self, key, value):
        """Assigns a key and value to the temp data. Temp data is not serialized so you can store
        whatever you need. keep in mind this data gets wiped since its temporary.

        Args:
            key (str): The name to give the key.
            value (Any): The value for the key.
        """
        self._TEMP_DATA[key] = value
        self.temp_data_changed.emit(key=key, value=value)

    def get_temp_data(self, key):
        if key not in self._TEMP_DATA.keys():
            return None
        return self._TEMP_DATA[key]

    def register(self):
        _register(self.uuid)


def deserialize(object_data):
    class_name = object_data[constants.OBJECT_DATA.META_DATA][constants.META_DATA.CLASS]
    module_dir = object_data[constants.OBJECT_DATA.META_DATA][constants.META_DATA.MODULE]

    object_data.pop(constants.OBJECT_DATA.META_DATA)

    module = importlib.import_module(module_dir)

    class_inst = getattr(module, class_name)
    if class_inst:
        return class_inst(**object_data)
    else:
        raise Exception(f"Could not find class {class_name} in globals")


OBJECTS = {}


def find(id):
    return OBJECTS.get(id, None)


def _register(obj):
    OBJECTS[obj.uuid] = obj


def remove(id):
    if id in OBJECTS:
        OBJECTS.pop(id)