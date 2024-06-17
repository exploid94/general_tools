Z_VALUE_GROUP_BOX = -2
Z_VALUE_PIPE = -1
Z_VALUE_NODE = 1
Z_VALUE_PORT = 2


class _LookupStr(str):
    def __init__(self, *args):
        self._ITEMS = []
        self._ITEMS.extend([v for k,v in self.__class__.__dict__.items() if k.upper() == k and not k.startswith("__")])

    @property
    def items(self):
        return self._ITEMS

    def has_item(self, item):
        return item in self.items

# object data keys for publishId's
class _ObjectData(_LookupStr):
    META_DATA = "__meta_data__"
    NAME = "name"
    VALUE = "value"
    LOCKED = "locked"
    HIDDEN = "hidden"
    HINT = "hint"
    ENABLED = "enabled"
OBJECT_DATA = _ObjectData("__object_data__")

# meta data keys for publishId's
class META_DATA(_LookupStr):
    UUID = "__uuid__"
    CLASS = "__class__"
    MODULE = "__module__"
META_DATA = META_DATA(OBJECT_DATA.META_DATA)

# temp data keys for publishId's
class _TempData(_LookupStr):
    PREVIOUS_VALUE = "previous_value"
TEMP_DATA = _TempData("__temp_data__")
