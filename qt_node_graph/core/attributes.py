from qt_node_graph.core.bases.base_attribute import _BaseAttribute
from qt_node_graph.core.signal import Signal
from qt_node_graph.utils import constants

import os
import pathlib
import re

class String(_BaseAttribute):
    """The string setting is a setting that only take a string as a value."""

    def __init__(self, name, value="", parent=None, locked=False, hidden=False, hint=None, pattern=None):
        self._SIGNAL_PATTERN_CHANGED = Signal(name=f"{name}.pattern_changed")

        pattern = pattern or '(?s).*'
        self._PATTERN = pattern

        if not isinstance(value, str):
            value = str(value)

        super().__init__(name, value, str, parent=parent, locked=locked, hidden=hidden, hint=hint)

        self.set_object_data("pattern", pattern)
        self.set_meta_data(constants.META_DATA.SETTING_WIDGET, constants.META_DATA.SETTING_WIDGET.STRING)

    def set(self, value, force=False):
        if not bool(re.compile(self.pattern).fullmatch(value)):
            raise Exception(f'[setting.{self.name}] Provided string does not match the pattern:' + self.pattern)
        if not isinstance(value, str):
            value = str(value)
        super().set(value, force=force)
        return self

    @property
    def pattern(self):
        return self._PATTERN

    @property
    def pattern_changed(self):
        """Emission: pattern_changed.emit(pattern)."""
        return self._SIGNAL_PATTERN_CHANGED

    def set_pattern(self, pattern):
        self._PATTERN = pattern
        self.set_object_data("pattern", pattern)
        self.pattern_changed.emit(pattern=pattern)
        return self.pattern


class Label(String):
    """The label setting is a setting that only takes a string as a value."""

    def __init__(self, name, value="", parent=None, locked=False, hidden=False, hint=None, pattern=None):
        super().__init__(name, value, parent, locked, hidden, hint, pattern)
        self.set_meta_data(constants.META_DATA.SETTING_WIDGET, constants.META_DATA.SETTING_WIDGET.LABEL)


class MultiLineString(String):
    """The multi line setting is a setting that only take a string as a value."""

    def __init__(self, name, value="", parent=None, locked=False, hidden=False, hint=None, pattern=None):
        super().__init__(name, value, parent, locked, hidden, hint, pattern)
        self.set_meta_data(constants.META_DATA.SETTING_WIDGET, constants.META_DATA.SETTING_WIDGET.MULTI_LINE_STRING)


class Path(String):
    """The path setting is a setting that only take a string as a value and contains it as a pathlib.Path."""

    def __init__(self, name, value="", parent=None, locked=False, hidden=False, hint=None, pattern=None):
        self._SIGNAL_SHORT_PATH_CHANGED = Signal(name=f"{name}.short_path_changed")
        super().__init__(name, value, parent, locked, hidden, hint, pattern)
        self._PATH = pathlib.Path(os.path.expandvars(os.path.expanduser(str(value))))
        self._SHORT_PATH = f"../{os.path.basename(self._PATH)}/.."

        self.set_meta_data(constants.META_DATA.SETTING_WIDGET, constants.META_DATA.SETTING_WIDGET.PATH)
        self.set_meta_data(constants.META_DATA.DEFAULT_DISPLAY_TYPE, constants.META_DATA.DEFAULT_DISPLAY_TYPE.LONG)
        self.set_meta_data(constants.META_DATA.FILE_MODE, constants.META_DATA.FILE_MODE.FILE)

    @property
    def path(self):
        return self._PATH

    @property
    def short_path(self):
        return self._SHORT_PATH

    @property
    def short_path_changed(self):
        """Emission: short_path_changed.emit(path)."""
        return self._SIGNAL_SHORT_PATH_CHANGED

    @property
    def extension(self):
        return self.path.suffix

    def set(self, value, force=False):
        super().set(value, force=force)
        self._PATH = pathlib.Path(os.path.expandvars(os.path.expanduser(str(value))))
        self.set_short_path(f"../{os.path.basename(self.path)}")
        return self

    def set_short_path(self, value):
        self._SHORT_PATH = value
        self._SIGNAL_SHORT_PATH_CHANGED.emit(path=value)
        return self


# numeric settings
class _NumericSetting(_BaseAttribute):
    def __init__(self, name, value, data_type, parent=None, locked=False, hidden=False, hint=None, min=None, max=None):
        """Creates a numeric setting with min and max values if needed.

        Args:
            name (str): name to give the setting
            value (int or float): value to give the setting
            data_type (int or float): type of data to represent
            parent (object): the parent of this setting
            locked (bool): whether to lock the setting or not
            hidden (bool): whether to hide the setting or not
            hint (str): the hint to give the setting
            min (int or float): the min value to give the setting
            max (int or float): the max value to give the setting
        """
        self._MIN_VALUE = None
        self._MAX_VALUE = None
        self._DATA_TYPE = data_type
        self._SIGNAL_MIN_CHANGED = Signal(name=f"{name}.min_changed")
        self._SIGNAL_MAX_CHANGED = Signal(name=f"{name}.max_changed")

        if not isinstance(value, data_type):
            value = data_type(value)

        super().__init__(name, value, data_type, parent=parent, locked=locked, hidden=hidden, hint=hint)

        self.set_min(min)
        self.set_max(max)

    @property
    def min(self):
        return self._MIN_VALUE

    @property
    def max(self):
        return self._MAX_VALUE

    @property
    def min_changed(self):
        """Emission: min_changed.emit(min)."""
        return self._SIGNAL_MIN_CHANGED

    @property
    def max_changed(self):
        """Emission: max_changed.emit(max)."""
        return self._SIGNAL_MAX_CHANGED

    def set_min(self, min_value):
        """Sets the minimum value allowed for the setting.

        Args:
            min_value (self.data_type): The minimm value allowed for the setting.
        """
        if isinstance(min_value, self.data_type):
            if self.min != min_value:
                self._MIN_VALUE = min_value
                self.set_object_data("min", self.min)
                self.min_changed.emit(min=min_value)
        elif min_value == None:
            if self.min != min_value:
                self._MIN_VALUE = None
                self.set_object_data("min", self.min)
                self.min_changed.emit(min=min_value)
        return self

    def set_max(self, max_value):
        """Sets the maximum value allowed for the setting.

        Args:
            max_value (self.data_type): The maximum value allowed for the setting.
        """
        if isinstance(max_value, self.data_type):
            if self.max != max_value:
                self._MAX_VALUE = max_value
                self.set_object_data("max", self.max)
                self.max_changed.emit(max=max_value)
        elif max_value == None:
            if self.max != max_value:
                self._MAX_VALUE = None
                self.set_object_data("max", self.max)
                self.max_changed.emit(max=max_value)
        return self

    def set(self, value, force=False, clamp=False):
        """Sets the value with extra clamping functionality.

        Args:
            value (self.data_type): The value to give the setting.
            force (bool): If True, ignores the locked state.
            clamp (bool): If True, the value will be clamped to the min and max values of the setting.
        """
        if clamp:
            if isinstance(self.min, self.data_type) and (value < self.min):
                value = self.min

            if isinstance(self.max, self.data_type) and (value > self.max):
                value = self.max

        if not isinstance(value, self.data_type):
            value = self.data_type(value)

        super().set(value, force=force)
        return self


class Integer(_NumericSetting):
    """The integer setting is a setting that only takes an int as a value."""

    def __init__(self, name, value=0, parent=None, locked=False, hidden=False, hint=None, min=-10000, max=10000):
        super().__init__(name, value, int, parent=parent, locked=locked, hidden=hidden, hint=hint, min=min, max=max)
        self.set_meta_data(constants.META_DATA.SETTING_WIDGET, constants.META_DATA.SETTING_WIDGET.INTEGER)


class Float(_NumericSetting):
    """The float setting is a setting that only takes a float as a value."""

    def __init__(self, name, value=0.0, parent=None, locked=False, hidden=False, hint=None, min=-10000.0, max=10000.0):
        super().__init__(name, value, float, parent=parent, locked=locked, hidden=hidden, hint=hint, min=min, max=max)
        self.set_meta_data(constants.META_DATA.SETTING_WIDGET, constants.META_DATA.SETTING_WIDGET.FLOAT)


class Bool(_BaseAttribute):
    """The bool setting is a setting that only takes a bool as a value."""

    def __init__(self, name, value=True, parent=None, locked=False, hidden=False, hint=None):
        if not isinstance(value, bool):
            value = self._convert(value)
        super().__init__(name, value, bool, parent=parent, locked=locked, hidden=hidden, hint=hint)
        self.set_meta_data(constants.META_DATA.SETTING_WIDGET, constants.META_DATA.SETTING_WIDGET.BOOL)

    def set(self, value, force=True):
        if not isinstance(value, bool):
            value = self._convert(value)
        super().set(value, force=force)
        return self

    def _convert(self, value):
        if isinstance(value, str):
            if value in ["true", "True", "1"]:
                value = True
            elif value in ["false", "False", "0"]:
                value = False
            elif float(value) >= 0.5:
                value = True
            else:
                value = False
        elif isinstance(value, int):
            if value > 0:
                value = True
            else:
                value = False
        elif isinstance(value, float):
            if value >= 0.5:
                value = True
            else:
                value = False
        else:
            value = False
        return value


# multi settings
class List(_BaseAttribute):
    """The list setting is a setting that only takes a list as a value."""

    def __init__(self, name, value=[], parent=None, locked=False, hidden=False, hint=None):
        super().__init__(name, value, list, parent=parent, locked=locked, hidden=hidden, hint=hint)
        self.set_meta_data(constants.META_DATA.SETTING_WIDGET, constants.META_DATA.SETTING_WIDGET.LIST)

    def append(self, obj):
        """Appends the object given to the list.

        Args:
            obj (object): The object to add to the list
        """
        if obj not in self.get():
            temp_list = self.get()
            temp_list.append(obj)
            self.set(temp_list)


class Compound(_BaseAttribute):
    """The compound setting allowsother settings to be added as children. This is useful for """

    def __init__(self, name, parent=None, locked=False, hidden=False, hint=None):
        self._SIGNAL_CHILDREN_CHANGED = Signal(name=f"{name}.children_changed")

        super().__init__(name, [], list, parent=parent, locked=locked, hidden=hidden, hint=hint, _set=False)
        self.set_meta_data(constants.META_DATA.SETTING_WIDGET, constants.META_DATA.SETTING_WIDGET.COMPOUND)

        self._VALUE = []
        self._CHILDREN = {}

    @property
    def children(self):
        return self._CHILDREN

    @property
    def children_changed(self):
        """Emission: children_changed.emit(children)."""
        return self._SIGNAL_CHILDREN_CHANGED

    def add_setting(self, setting):
        """Adds another setting to the children of this compound setting.

        Args:
            setting (_BaseAttribute): The setting to add. This can be any setting type.

        Returns:
            setting: The setting added.
        """
        if setting.name not in self.children:
            if isinstance(setting, _BaseAttribute):
                setting.set_parent(self)
                self.value.append(setting)
                self._CHILDREN[setting.name] = setting
                self.children_changed.emit(children=self.children)
                return setting

    def add_settings(self, settings):
        """Adds multiple settings to this compound setting."""
        changed = False
        for setting in settings:
            if setting.name not in self.children:
                if isinstance(setting, _BaseAttribute):
                    setting.set_parent(self)
                    self.value.append(setting)
                    self._CHILDREN[setting.name] = setting
                    changed = True
        if changed:
            self.children_changed.emit(children=self.children)

    def remove_setting(self, setting):
        """Removes the given setting from this compound setting.

        Args:
            setting (_BaseAttribute): The setting to remove from this compound setting.
        """
        if setting.name in self.children:
            setting.set_parent(None)
            del self._CHILDREN[setting.name]
            self.children_changed.emit(children=self.children)

    def set(self, value):
        raise NotImplementedError(
            "Compound.set() is not implemented, use Compound.add_setting() or Compound.remove_setting() instead")

    def get(self):
        raise NotImplementedError("Compound.get() is not implemented, use Compound.children property instead")


class Enum(_BaseAttribute):
    def __init__(self, name, value=0, options=[], parent=None, locked=False, hidden=False, hint=None):
        """An enum setting is a setting that contains a list of options that can be set to an individual option.

        Args:
            name (str): The name of the setting.
            value (int or str): The index or name of the option in the options list.
            options (list of str): The list of options to choose from. Options must be strings.
            parent (obj): The parent of the setting.
            locked (bool): The locked state of the setting.
            hidden (bool): The hidden state of the setting.
            hint (str): A description of the setting.
        """
        self._OPTIONS = []
        self._SIGNAL_OPTIONS_CHANGED = Signal(name=f"{name}.options_changed")

        # TODO turn set to false because this set is overridden
        # use custom set right after
        super().__init__(name, value, str, parent=parent, locked=locked, hidden=hidden, hint=hint, _set=False)
        if len(options) > 0:
            self.add_options(options)
            self.set(value, force=True)

        self.set_object_data("options", self.options)
        self.set_meta_data(constants.META_DATA.SETTING_WIDGET, constants.META_DATA.SETTING_WIDGET.ENUM)

    @property
    def options(self):
        return self._OPTIONS

    @property
    def current_index(self):
        return self.get_index_from_option(self.get())

    @property
    def options_changed(self):
        """Emission: options_changed.emit(options)."""
        return self._SIGNAL_OPTIONS_CHANGED

    def option_exists(self, option):
        """Checks whether or not the option exists.

        Args:
            option (str): The name of the option

        Returns:
            bool
        """
        if isinstance(option, str):
            if option in self.options:
                return True
            else:
                return False

    def add_option(self, option):
        """Adds the given option to the options list.

        Args:
            option (str): The name of the option to add.
        """
        if isinstance(option, str):
            if option not in self.options:
                self._OPTIONS.append(option)
                self.set_object_data("options", self.options)
                self.options_changed.emit(options=self.options)

    def add_options(self, options):
        """Adds multiple options to the options list.

        Args:
            options (list of str): The list of options to add
        """
        changed = False
        for option in options:
            if isinstance(option, str):
                if option not in self.options:
                    self._OPTIONS.append(option)
                    changed = True
        if changed:
            self.set_object_data("options", self.options)
            self.options_changed.emit(options=self.options)

    def remove_option(self, option):
        if option in self.options:
            self.options.remove(option)
            self.set_object_data("options", self.options)
            self.options_changed.emit(options=self.options)

    def clear_options(self):
        self._OPTIONS = []
        self.set_object_data("options", self.options)
        self.options_changed.emit(options=self.options)

    def get_index_from_option(self, option):
        """Gets the index of an option by the given option name.

        Args:
            option (str): The name of the option.

        Returns:
            int: Index of the option.
        """
        if self.option_exists(option):
            return self.options.index(option)

    def get_option_from_index(self, index):
        """Gets the option at the given index.

        Args:
            index (int): The index of the option.

        Returns:
            option (str): The name of the option."""
        return self.options[index]

    def set(self, value, force=False):
        try:
            if isinstance(value, str):
                if self.option_exists(value):
                    super().set(value, force=force)
            elif isinstance(value, int):
                super().set(self.get_option_from_index(value), force=force)
            elif value == None:
                super().set(None, force=force)
        except:
            pass
        return self


# vector settings
class _Vector2(Compound):
    def __init__(self, name, data_type, x, y, parent=None, locked=False, hidden=False, hint=None):
        super().__init__(name, parent, locked, hidden, hint)
        if isinstance(data_type, float):
            self._X = self.add_setting(Float(name="x", value=x, locked=locked, hidden=hidden, hint=hint))
            self._Y = self.add_setting(Float(name="y", value=y, locked=locked, hidden=hidden, hint=hint))
        elif isinstance(data_type, int):
            self._X = self.add_setting(Integer(name="x", value=x, locked=locked, hidden=hidden, hint=hint))
            self._Y = self.add_setting(Integer(name="y", value=y, locked=locked, hidden=hidden, hint=hint))

    @property
    def x(self):
        return self._X

    @property
    def y(self):
        return self._Y

    def set_x(self, value, force=False):
        self.x.set(value, force=force)
        return self.x

    def set_y(self, value, force=False):
        self.y.set(value, force=force)
        return self.y

    def set(self, x, y, force=False):
        self.set_x(x, force=force)
        self.set_y(y, force=force)
        return self

    def lock(self):
        super().lock()
        self.x.lock()
        self.y.lock()
        return self

    def unlock(self):
        super().unlock()
        self.x.unlock()
        self.y.unlock()
        return self

    def hide(self):
        super().hide()
        self.x.hide()
        self.y.hide()
        return self

    def unhide(self):
        super().unhide()
        self.x.unhide()
        self.y.unhide()
        return self


class _Vector3(Compound):
    def __init__(self, name, data_type, x, y, z, parent=None, locked=False, hidden=False, hint=None):
        super().__init__(name, parent, locked, hidden, hint)
        if isinstance(data_type, float):
            self._X = self.add_setting(Float(name="x", value=x, locked=locked, hidden=hidden, hint=hint))
            self._Y = self.add_setting(Float(name="y", value=y, locked=locked, hidden=hidden, hint=hint))
            self._Z = self.add_setting(Float(name="z", value=z, locked=locked, hidden=hidden, hint=hint))
        elif isinstance(data_type, int):
            self._X = self.add_setting(Integer(name="x", value=x, locked=locked, hidden=hidden, hint=hint))
            self._Y = self.add_setting(Integer(name="y", value=y, locked=locked, hidden=hidden, hint=hint))
            self._Z = self.add_setting(Integer(name="z", value=z, locked=locked, hidden=hidden, hint=hint))

    @property
    def x(self):
        return self._X

    @property
    def y(self):
        return self._Y

    @property
    def z(self):
        return self._Z

    def set_x(self, value, force=False):
        self.x.set(value, force=force)
        return self.x

    def set_y(self, value, force=False):
        self.y.set(value, force=force)
        return self.y

    def set_z(self, value, force=False):
        self.z.set(value, force=force)
        return self.z

    def set(self, x, y, z, force=False):
        self.set_x(x, force=force)
        self.set_y(y, force=force)
        self.set_z(z, force=force)
        return self

    def lock(self):
        super().lock()
        self.x.lock()
        self.y.lock()
        self.z.lock()
        return self

    def unlock(self):
        super().unlock()
        self.x.unlock()
        self.y.unlock()
        self.z.unlock()
        return self

    def hide(self):
        super().hide()
        self.x.hide()
        self.y.hide()
        self.z.hide()
        return self

    def unhide(self):
        super().unhide()
        self.x.unhide()
        self.y.unhide()
        self.z.unhide()
        return self


class _Vector4(Compound):
    def __init__(self, name, data_type, x, y, z, w, parent=None, locked=False, hidden=False, hint=None):
        super().__init__(name, parent, locked, hidden, hint)
        if isinstance(data_type, float):
            self._X = self.add_setting(Float(name="x", value=x, locked=locked, hidden=hidden, hint=hint))
            self._Y = self.add_setting(Float(name="y", value=y, locked=locked, hidden=hidden, hint=hint))
            self._Z = self.add_setting(Float(name="z", value=z, locked=locked, hidden=hidden, hint=hint))
            self._W = self.add_setting(Float(name="w", value=w, locked=locked, hidden=hidden, hint=hint))
        elif isinstance(data_type, int):
            self._X = self.add_setting(Integer(name="x", value=x, locked=locked, hidden=hidden, hint=hint))
            self._Y = self.add_setting(Integer(name="y", value=y, locked=locked, hidden=hidden, hint=hint))
            self._Z = self.add_setting(Integer(name="z", value=z, locked=locked, hidden=hidden, hint=hint))
            self._W = self.add_setting(Integer(name="w", value=w, locked=locked, hidden=hidden, hint=hint))

    @property
    def x(self):
        return self._X

    @property
    def y(self):
        return self._Y

    @property
    def z(self):
        return self._Z

    @property
    def w(self):
        return self._W

    def set_x(self, value, force=False):
        self.x.set(value, force=force)
        return self.x

    def set_y(self, value, force=False):
        self.y.set(value, force=force)
        return self.y

    def set_z(self, value, force=False):
        self.z.set(value, force=force)
        return self.z

    def set_w(self, value, force=False):
        self.w.set(value, force=force)
        return self.w

    def set(self, x, y, z, w, force=False):
        self.set_x(x, force=force)
        self.set_y(y, force=force)
        self.set_z(z, force=force)
        self.set_z(w, force=force)
        return self

    def lock(self):
        super().lock()
        self.x.lock()
        self.y.lock()
        self.z.lock()
        self.w.lock()
        return self

    def unlock(self):
        super().unlock()
        self.x.unlock()
        self.y.unlock()
        self.z.unlock()
        self.w.unlock()
        return self

    def hide(self):
        super().hide()
        self.x.hide()
        self.y.hide()
        self.z.hide()
        self.w.hide()
        return self

    def unhide(self):
        super().unhide()
        self.x.unhide()
        self.y.unhide()
        self.z.unhide()
        self.w.unhide()
        return self


class IntVector2(_Vector2):
    def __init__(self, name, x=0, y=0, parent=None, locked=False, hidden=False, hint=None):
        super().__init__(name, int(), x, y, parent, locked, hidden, hint)


class IntVector3(_Vector3):
    def __init__(self, name, x=0, y=0, z=0, parent=None, locked=False, hidden=False, hint=None):
        super().__init__(name, int(), x, y, z, parent, locked, hidden, hint)


class IntVector4(_Vector4):
    def __init__(self, name, x=0, y=0, z=0, w=0, parent=None, locked=False, hidden=False, hint=None):
        super().__init__(name, int(), x, y, z, w, parent, locked, hidden, hint)


class FloatVector2(_Vector2):
    def __init__(self, name, x=0.0, y=0.0, parent=None, locked=False, hidden=False, hint=None):
        super().__init__(name, float(), x, y, parent, locked, hidden, hint)


class FloatVector3(_Vector3):
    def __init__(self, name, x=0.0, y=0.0, z=0.0, parent=None, locked=False, hidden=False, hint=None):
        super().__init__(name, float(), x, y, z, parent, locked, hidden, hint)


class FloatVector4(_Vector4):
    def __init__(self, name, x=0.0, y=0.0, z=0.0, w=0.0, parent=None, locked=False, hidden=False, hint=None):
        super().__init__(name, float(), x, y, z, parent, locked, hidden, hint)


# color settings
class _RGB(Compound):
    def __init__(self, name, data_type, r, g, b, parent=None, locked=False, hidden=False, hint=None):
        super().__init__(name, parent, locked, hidden, hint)
        if isinstance(data_type, float):
            self._R = self.add_setting(Float(name="r", value=r, locked=locked, hidden=hidden, hint=hint))
            self._G = self.add_setting(Float(name="g", value=g, locked=locked, hidden=hidden, hint=hint))
            self._B = self.add_setting(Float(name="b", value=b, locked=locked, hidden=hidden, hint=hint))
        elif isinstance(data_type, int):
            self._R = self.add_setting(Integer(name="r", value=r, locked=locked, hidden=hidden, hint=hint))
            self._G = self.add_setting(Integer(name="g", value=g, locked=locked, hidden=hidden, hint=hint))
            self._B = self.add_setting(Integer(name="b", value=b, locked=locked, hidden=hidden, hint=hint))

    @property
    def r(self):
        return self._R

    @property
    def g(self):
        return self._G

    @property
    def b(self):
        return self._B

    def set_r(self, value, force=False):
        self.r.set(value, force=force)
        return self.r

    def set_g(self, value, force=False):
        self.g.set(value, force=force)
        return self.g

    def set_b(self, value, force=False):
        self.b.set(value, force=force)
        return self.b

    def set(self, r, g, b, force=False):
        self.set_r(r, force=force)
        self.set_g(g, force=force)
        self.set_b(b, force=force)
        return self

    def lock(self):
        super().lock()
        self.r.lock()
        self.g.lock()
        self.b.lock()
        return self

    def unlock(self):
        super().unlock()
        self.r.unlock()
        self.g.unlock()
        self.b.unlock()
        return self

    def hide(self):
        super().hide()
        self.r.hide()
        self.g.hide()
        self.b.hide()
        return self

    def unhide(self):
        super().unhide()
        self.r.unhide()
        self.g.unhide()
        self.b.unhide()
        return self


class _RGBA(Compound):
    def __init__(self, name, data_type, r, g, b, a, parent=None, locked=False, hidden=False, hint=None):
        super().__init__(name, parent, locked, hidden, hint)
        if isinstance(data_type, float):
            self._R = self.add_setting(Float(name="r", value=r, locked=locked, hidden=hidden, hint=hint))
            self._G = self.add_setting(Float(name="g", value=g, locked=locked, hidden=hidden, hint=hint))
            self._B = self.add_setting(Float(name="b", value=b, locked=locked, hidden=hidden, hint=hint))
            self._A = self.add_setting(Float(name="a", value=a, locked=locked, hidden=hidden, hint=hint))
        elif isinstance(data_type, int):
            self._R = self.add_setting(Integer(name="r", value=r, locked=locked, hidden=hidden, hint=hint))
            self._G = self.add_setting(Integer(name="g", value=g, locked=locked, hidden=hidden, hint=hint))
            self._B = self.add_setting(Integer(name="b", value=b, locked=locked, hidden=hidden, hint=hint))
            self._A = self.add_setting(Integer(name="a", value=a, locked=locked, hidden=hidden, hint=hint))

    @property
    def r(self):
        return self._R

    @property
    def g(self):
        return self._G

    @property
    def b(self):
        return self._B

    @property
    def a(self):
        return self._A

    def set_r(self, value, force=False):
        self.r.set(value, force=force)
        return self.r

    def set_g(self, value, force=False):
        self.g.set(value, force=force)
        return self.g

    def set_b(self, value, force=False):
        self.b.set(value, force=force)
        return self.b

    def set_a(self, value, force=False):
        self.a.set(value, force=force)
        return self.a

    def set(self, r, g, b, a, force=False):
        self.set_r(r, force=force)
        self.set_g(g, force=force)
        self.set_b(b, force=force)
        self.set_a(a, force=force)
        return self

    def lock(self):
        super().lock()
        self.r.lock()
        self.g.lock()
        self.b.lock()
        self.a.lock()
        return self

    def unlock(self):
        super().unlock()
        self.r.unlock()
        self.g.unlock()
        self.b.unlock()
        self.a.unlock()
        return self

    def hide(self):
        super().hide()
        self.r.hide()
        self.g.hide()
        self.b.hide()
        self.a.hide()
        return self

    def unhide(self):
        super().unhide()
        self.r.unhide()
        self.g.unhide()
        self.b.unhide()
        self.a.unhide()
        return self


class IntRGB(_RGB):
    def __init__(self, name, r=0, g=0, b=0, parent=None, locked=False, hidden=False, hint=None):
        super().__init__(name, int(), r, g, b, parent, locked, hidden, hint)


class FloatRGB(_RGB):
    def __init__(self, name, r=0, g=0, b=0, parent=None, locked=False, hidden=False, hint=None):
        super().__init__(name, float(), r, g, b, parent, locked, hidden, hint)


class IntRGBA(_RGBA):
    def __init__(self, name, r=0, g=0, b=0, a=0, parent=None, locked=False, hidden=False, hint=None):
        super().__init__(name, int(), r, g, b, a, parent, locked, hidden, hint)


class FloatRGBA(_RGBA):
    def __init__(self, name, r=0, g=0, b=0, a=0, parent=None, locked=False, hidden=False, hint=None):
        super().__init__(name, float(), r, g, b, a, parent, locked, hidden, hint)

