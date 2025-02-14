import os
import pathlib
import re
from collections import defaultdict

from genesis.core.bases.base_attribute import BaseAttribute
from genesis.core import signal
from genesis.utils import logging
from genesis.utils import constants

logger = logging.get_logger(__name__, level="WARNING")


class String(BaseAttribute):
    """The string setting is a setting that only take a string as a value.

    Args:
        name (str): The name of this setting
        value (str, optional): The value to set on this setting98
        locked (bool, optional): If True, this setting can only be set using self.set(value, force=True)
        hidden (bool, optional): If True, this setting will be hidden in ui elements
        hint (str, optional): The hint/tooltip to give this setting
        pattern (str, optional): The pattern to give this setting. This uses the python re package
        """

    def __init__(self, name, value="", parent=None, locked=False, hidden=False, hint=None, pattern=None):
        self._SIGNAL_PATTERN_CHANGED = signal.Signal()

        pattern = pattern or '(?s).*'
        self._PATTERN = pattern

        if not isinstance(value, str):
            value = str(value)

        super().__init__(name, value, str, parent=parent, locked=locked, hidden=hidden, hint=hint)

        self.set_object_data("pattern", pattern)

    def set(self, value, force=False, emit=True):
        """Sets the value of this setting to the given value.

        Args:
            value (str): The value to set this setting to
            force (bool, optional): If True, this setting will set the value even if the setting is locked
        """
        if not bool(re.compile(self.pattern).fullmatch(value)):
            raise Exception(f'[setting.{self.name}] Provided string does not match the pattern:' + self.pattern)
        if not isinstance(value, str):
            value = str(value)
        super().set(value, force=force)
        return self

    @property
    def pattern(self):
        """str: The pattern of this setting. The pattern should be able to re.compile()"""
        return self._PATTERN

    @property
    def pattern_changed(self):
        """signal.Signal: pattern_changed.emit(pattern)."""
        return self._SIGNAL_PATTERN_CHANGED

    def set_pattern(self, pattern):
        """Sets the pattern of this setting

        Args:
            pattern (str): The pattern you want this string to use when using self.set()
        """
        self._PATTERN = pattern
        self.set_object_data("pattern", pattern)
        self.pattern_changed.emit(pattern=pattern)
        return self.pattern


class Label(String):
    """The label setting is a setting that only takes a string as a value.

    Args:
        name (str): The name of this setting
        value (str, optional): The value to set on this setting
        parent (Any, optional): The parent of this setting
        locked (bool, optional): If True, this setting can only be set using self.set(value, force=True)
        hidden (bool, optional): If True, this setting will be hidden in ui elements
        hint (str, optional): The hint/tooltip to give this setting
        pattern (str, optional): The pattern to give this setting. This uses the python re package
    """

    def __init__(self, name, value="", parent=None, locked=False, hidden=False, hint=None, pattern=None):
        super().__init__(name, value, parent, locked, hidden, hint, pattern)

class Path(String):
    """The path setting is a setting that only take a string as a value and contains it as a pathlib.Path.

    Args:
        name (str): The name of this setting
        value (str, optional): The value to set on this setting
        parent (Any, optional): The parent of this setting
        locked (bool, optional): If True, this setting can only be set using self.set(value, force=True)
        hidden (bool, optional): If True, this setting will be hidden in ui elements
        hint (str, optional): The hint/tooltip to give this setting
        pattern (str, optional): The pattern to give this setting. This uses the python re package
    """

    def __init__(self, name, value="", parent=None, locked=False, hidden=False, hint=None, pattern=None):
        self._SIGNAL_SHORT_PATH_CHANGED = signal.Signal()
        self._SIGNAL_TEMPLATE_CHANGED = signal.Signal()
        super().__init__(name, value, parent, locked, hidden, hint, pattern)
        self._TEMPLATE = ""
        self._PATH = pathlib.Path(os.path.expandvars(os.path.expanduser(str(value))))
        self._SHORT_PATH = f"../{os.path.basename(self._PATH)}"

        self.set_meta_data(constants.META_DATA.DEFAULT_DISPLAY_TYPE, constants.META_DATA.DEFAULT_DISPLAY_TYPE.LONG)
        self.set_meta_data(constants.META_DATA.FILE_MODE, constants.META_DATA.FILE_MODE.FILE)

    @property
    def template(self):
        """str: The format of the path you want to use. The format responds to examples like '{folder_name}_{file_name}.{extension}'"""
        return self._TEMPLATE

    @property
    def path(self):
        """pathlib.Path: The path object of the value of this setting"""
        return self._PATH

    @property
    def short_path(self):
        """str: The shortened path of the value of this setting"""
        return self._SHORT_PATH

    @property
    def template_changed(self):
        """signal.Signal: template_changed.emit(template)."""
        return self._SIGNAL_TEMPLATE_CHANGED

    @property
    def short_path_changed(self):
        """signal.Signal: short_path_changed.emit(path)."""
        return self._SIGNAL_SHORT_PATH_CHANGED

    @property
    def extension(self):
        """str: The extension of this setting"""
        return self.path.suffix

    def set(self, value, force=False, emit=True):
        """Sets the value of this setting to the given value.

        Args:
            value (str): The value to set this setting to
            force (bool, optional): If True, this setting will set the value even if the setting is locked
        """
        if isinstance(value, pathlib.Path):
            super().set(str(value), force=force)
            self._PATH = value
        else:
            super().set(value, force=force)
            self._PATH = pathlib.Path(os.path.expandvars(os.path.expanduser(str(value))))

        # try to automatically assign meta data
        try:
            if self.path.is_file():
                self.set_meta_data(constants.META_DATA.FILE_MODE, constants.META_DATA.FILE_MODE.FILE)
            elif self.path.is_dir():
                self.set_meta_data(constants.META_DATA.FILE_MODE, constants.META_DATA.FILE_MODE.DIRECTORY)
        except:
            raise

        self.set_short_path(f"../{os.path.basename(self.path)}")
        return self

    def set_short_path(self, value):
        """Sets the short path of this setting to the value give. Short path is mostly for easier to read long paths.

        Args:
            value (str): The short path you want to set on this setting
        """
        self._SHORT_PATH = value
        self._SIGNAL_SHORT_PATH_CHANGED.emit(path=value)
        return self

    def set_template(self, template):
        """Sets the template for this setting which can be used with self.format_path()

        Args:
            template (str): The template to use for formatting the value of this setting
        """
        self._TEMPLATE = template
        self.template_changed.emit(template=template)

    def format_path(self, **kwargs):
        """Formats the value of this setting to self.format using given kwargs. For example if you have the format as
        '{folder_name}/{file_name}.{ext}', you should use self.format_path(folder_name='folder', file_name='file', ext='.test')

        Args:
            **kwargs (Any): The arguments you want to pass and use for formating.
            """
        return self.template.format_map(defaultdict(str, **kwargs))

    def exists(self):
        """Returns True if the path exists on disk or not"""
        if self.value:
            return self.path.exists()
        else:
            return False


class Button(BaseAttribute):
    """The button setting is a setting that simulates a button for extended use with a publisher.

    Args:
        name (str): The name of this setting
        value (str, optional): The value to set on this setting
        parent (Any, optional): The parent of this setting
        locked (bool, optional): If True, this setting can only be set using self.set(value, force=True)
        hidden (bool, optional): If True, this setting will be hidden in ui elements
        hint (str, optional): The hint/tooltip to give this setting
    """

    def __init__(self, name, value="", parent=None, locked=False, hidden=False, hint=None):
        self._SIGNAL_CLICKED = signal.Signal()
        self._CLICK_FUNCTION = None

        super().__init__(name, value, str, parent=parent, locked=locked, hidden=hidden, hint=hint)


    @property
    def clicked(self):
        """signal.Signal: clicked.emit()."""
        return self._SIGNAL_CLICKED

    @property
    def click_function(self):
        """func: The function assigned to this setting"""
        return self._CLICK_FUNCTION

    def click(self, **kwargs):
        """Simulates a clicked action like a button does, with the given kwargs

        Args:
            **kwargs: The arguments you want to pass the click_function
        """
        self.click_function(**kwargs)

    def set_click_function(self, function):
        """Sets the func given to be the self.click_function, which is ran when this button is clicked.

        Args:
            function (def): The function you want to assign when this button is clicked
        """
        self._CLICK_FUNCTION = function


# numeric settings
class _NumericSetting(BaseAttribute):
    """Creates a numeric setting with min and max values if needed.

    Args:
        name (str): The name of this setting
        value (int or float, optional): The value to set on this setting
        parent (Any, optional): The parent of this setting
        locked (bool, optional): If True, this setting can only be set using self.set(value, force=True)
        hidden (bool, optional): If True, this setting will be hidden in ui elements
        hint (str, optional): The hint/tooltip to give this setting
        min (int or float, optional): the min value to give the setting
        max (int or float, optional): the max value to give the setting
    """

    def __init__(self, name, value, data_type, parent=None, locked=False, hidden=False, hint=None, min=None, max=None):
        self._MIN_VALUE = None
        self._MAX_VALUE = None
        self._DATA_TYPE = data_type
        self._SIGNAL_MIN_CHANGED = signal.Signal()
        self._SIGNAL_MAX_CHANGED = signal.Signal()

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
        """signal.Signal: min_changed.emit(min)."""
        return self._SIGNAL_MIN_CHANGED

    @property
    def max_changed(self):
        """signal.Signal: max_changed.emit(max)."""
        return self._SIGNAL_MAX_CHANGED

    def set_min(self, min_value):
        """Sets the minimum value allowed for the setting.

        Args:
            min_value (int or float): The minimum value allowed for the setting.
        """
        if isinstance(min_value, self.data_type):
            if self.min != min_value:
                self._MIN_VALUE = min_value
                self.set_object_data("min", self.min)
                self.min_changed.emit(min=min_value)
        elif min_value is None:
            if self.min != min_value:
                self._MIN_VALUE = None
                self.set_object_data("min", self.min)
                self.min_changed.emit(min=min_value)
        else:
            logger.error(f"{min_value} is not of type {self.data_type}")
        return self

    def set_max(self, max_value):
        """Sets the maximum value allowed for the setting.

        Args:
            max_value (int or float): The maximum value allowed for the setting.
        """
        if isinstance(max_value, self.data_type):
            if self.max != max_value:
                self._MAX_VALUE = max_value
                self.set_object_data("max", self.max)
                self.max_changed.emit(max=max_value)
        elif max_value is None:
            if self.max != max_value:
                self._MAX_VALUE = None
                self.set_object_data("max", self.max)
                self.max_changed.emit(max=max_value)
        else:
            logger.error(f"{max_value} is not of type {self.data_type}")
        return self

    def set(self, value, force=False, clamp=False, emit=True):
        """Sets the value with extra clamping functionality.

        Args:
            value (int or float): The value to give the setting.
            force (bool, optional): If True, ignores the locked state.
            clamp (bool, optional): If True, the value will be clamped to the min and max values of the setting.
        """
        if clamp:
            if isinstance(self.min, self.data_type) and (value < self.min):
                value = self.min

            if isinstance(self.max, self.data_type) and (value > self.max):
                value = self.max
        else:
            if isinstance(self.min, self.data_type) and (value < self.min):
                logger.error(f'Value {value} is less than min value {self.min}!')

            if isinstance(self.max, self.data_type) and (value > self.max):
                logger.error(f'Value {value} is more than max value {self.max}!')

        if not isinstance(value, self.data_type):
            logger.warning(f"setting {self.name} got passed a non {self.data_type} type. Attempting to convert it.")
            value = self.data_type(value)

        super().set(value, force=force, emit=emit)
        return self


class Integer(_NumericSetting):
    """The integer setting is a setting that only takes an int as a value.

    Args:
        name (str): The name of this setting
        value (int, optional): The value to set on this setting
        parent (Any, optional): The parent of this setting
        locked (bool, optional): If True, this setting can only be set using self.set(value, force=True)
        hidden (bool, optional): If True, this setting will be hidden in ui elements
        hint (str, optional): The hint/tooltip to give this setting
        min (int or float, optional): the min value to give the setting
        max (int or float, optional): the max value to give the setting
    """

    def __init__(self, name, value=0, parent=None, locked=False, hidden=False, hint=None, min=-99999999, max=99999999):
        super().__init__(name, value, int, parent=parent, locked=locked, hidden=hidden, hint=hint, min=min, max=max)


class Float(_NumericSetting):
    """The float setting is a setting that only takes a float as a value.

    Args:
        name (str): The name of this setting
        value (float, optional): The value to set on this setting
        parent (Any, optional): The parent of this setting
        locked (bool, optional): If True, this setting can only be set using self.set(value, force=True)
        hidden (bool, optional): If True, this setting will be hidden in ui elements
        hint (str, optional): The hint/tooltip to give this setting
        min (int or float, optional): the min value to give the setting
        max (int or float, optional): the max value to give the setting
    """

    def __init__(self, name, value=0.0, parent=None, locked=False, hidden=False, hint=None, min=-99999999.9,
                 max=99999999.9):
        super().__init__(name, value, float, parent=parent, locked=locked, hidden=hidden, hint=hint, min=min, max=max)


class Bool(BaseAttribute):
    """The bool setting is a setting that only takes a bool as a value.

    Args:
        name (str): The name of this setting
        value (bool, optional): The value to set on this setting
        parent (Any, optional): The parent of this setting
        locked (bool, optional): If True, this setting can only be set using self.set(value, force=True)
        hidden (bool, optional): If True, this setting will be hidden in ui elements
        hint (str, optional): The hint/tooltip to give this setting
    """

    def __init__(self, name, value=True, parent=None, locked=False, hidden=False, hint=None):
        if not isinstance(value, bool):
            value = self._convert(value)
        super().__init__(name, value, bool, parent=parent, locked=locked, hidden=hidden, hint=hint)

    def set(self, value, force=True, emit=True):
        """Sets the value of this setting to the given value.

        Args:
            value (bool): The value to set this setting to
            force (bool, optional): If True, this setting will set the value even if the setting is locked
        """
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
class List(BaseAttribute):
    """The list setting is a setting that only takes a list as a value.

    Args:
        name (str): The name of this setting
        value (list, optional): The value to set on this setting
        parent (Any, optional): The parent of this setting
        locked (bool, optional): If True, this setting can only be set using self.set(value, force=True)
        hidden (bool, optional): If True, this setting will be hidden in ui elements
        hint (str, optional): The hint/tooltip to give this setting
    """

    def __init__(self, name, value=[], parent=None, locked=False, hidden=False, hint=None):
        if not isinstance(value, list):
            value = self._convert(value)
        super().__init__(name, value, list, parent=parent, locked=locked, hidden=hidden, hint=hint)

    def append(self, obj, force=False):
        """Appends the object given to the list.

        Args:
            obj (Any): The object to add to the list
        """
        if obj not in self.get():
            temp_list = self.get()
            temp_list.append(obj)
            self.set(temp_list, force=force)
        else:
            logger.exception(f"Object {obj} is already in {self}")

    def set(self, value, force=False, emit=True):
        if not isinstance(value, list):
            value = self._convert(value)
        super().set(value, force=force)
        return self

    def _convert(self, value):
        return [value]


class Compound(BaseAttribute):
    """The compound setting allows other settings to be added as children. This is useful for
    settings such as vectors or rgb colors etc. Don't use the set or get functions in this class,
    instead you can use self.children to get child settings, then you can use the child set/get.
    Must subclass this class so the children settings get serialized and de-serialized properly.

    Args:
        name (str): The name of this setting
        parent (Any, optional): The parent of this setting
        locked (bool, optional): If True, this setting can only be set using self.set(value, force=True)
        hidden (bool, optional): If True, this setting will be hidden in ui elements
        hint (str, optional): The hint/tooltip to give this setting
    """

    def __init__(self, name, value=None, parent=None, locked=False, hidden=False, hint=None, force=False):
        self._SIGNAL_SETTINGS_CHANGED = signal.Signal()
        self._VALUE = value

        super().__init__(name, [], list, parent=parent, locked=locked, hidden=hidden, hint=hint, _set=False)

    def set(self, value, force=False, emit=True):
        """Not implemented, use the child settings set()
        We are only using this for serializing and deserializing the class."""
        if force:
            self._VALUE = value
            # for setting in value:
            #    self.settings[setting].set(value[setting])
        else:
            raise NotImplementedError(
                "Compound.set() is not implemented, use Compound.add_attribute() or Compound.remove_setting() instead")

    def get(self):
        """Not implemented, use the child settings get()"""
        return self._VALUE


class Enum(BaseAttribute):
    """An enum setting is a setting that contains a list of options that can be set to an individual option.

    Args:
        name (str): The name of the setting.
        value (int or str, optional): The index or name of the option in the options list.
        options (list of str, optional): The list of options to choose from. Options must be strings.
        option_data (dict, optional): The data that is assigned to each option. Format is {option_name: options_data}.
        parent (obj, optional): The parent of the setting.
        locked (bool, optional): The locked state of the setting.
        hidden (bool, optional): The hidden state of the setting.
        hint (str, optional): A description of the setting.
    """

    def __init__(self, name, value=0, options=[], option_data={}, parent=None, locked=False, hidden=False, hint=None):
        self._OPTIONS = []
        self._OPTION_DATA = option_data
        self._SIGNAL_OPTIONS_CHANGED = signal.Signal()
        self._SIGNAL_OPTION_DATA_CHANGED = signal.Signal()

        # TODO turn set to false because this set is overridden
        # use custom set right after
        super().__init__(name, value, str, parent=parent, locked=locked, hidden=hidden, hint=hint, _set=False)
        if len(options) > 0:
            self.add_options(options)
            self.set(value, force=True)
        else:
            logger.debug(f"no options specified for setting {name}")

        self.set_object_data("options", self.options)
        self.set_object_data("option_data", self.option_data)

    @property
    def options(self):
        """list: The options available on this setting. You can only set() using one of these options"""
        return self._OPTIONS

    @property
    def option_data(self):
        """dict: The data associated to all of the options"""
        return self._OPTION_DATA

    @property
    def current_index(self):
        """int: The index of the current selected value"""
        return self.get_index_from_option(self.get())

    @property
    def options_changed(self):
        """signal.Signal: options_changed.emit(options)."""
        return self._SIGNAL_OPTIONS_CHANGED

    @property
    def option_data_changed(self):
        """signal.Signal: options_changed.emit(data)."""
        return self._SIGNAL_OPTION_DATA_CHANGED

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
        else:
            logger.error(f"Option {option} is not a string")

    def add_option(self, option, option_data=None):
        """Adds the given option to the options list.

        Args:
            option (str): The name of the option to add.
        """
        if isinstance(option, str):
            if option not in self.options:
                self._OPTIONS.append(option)
                self.set_option_data(option, option_data)
                self.set_object_data("options", self.options)
                self.options_changed.emit(options=self.options)
            else:
                logger.exception(f"Option {option} is already an allowed option")
        else:
            logger.error(f"Option {option} is not a string")

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
                else:
                    logger.exception(f"Option {option} is already an allowed option")
            else:
                logger.error(f"Option {option} is not a string")
        if changed:
            self.set_object_data("options", self.options)
            self.options_changed.emit(options=self.options)

    def remove_option(self, option):
        """Removes the given option of self.options

        Args:
            option (str): The name of the option you want removed
        """
        if option in self.options:
            self.options.remove(option)
            if option in self.option_data:
                self.option_data.pop(option)
            self.set_object_data("options", self.options)
            self.options_changed.emit(options=self.options)

    def clear_options(self):
        """Removes all options from this setting"""
        self._OPTIONS = []
        self._OPTION_DATA = {}
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
        else:
            logger.error(f"Option {option} does not exist")

    def get_option_from_index(self, index):
        """Gets the option at the given index.

        Args:
            index (int): The index of the option.

        Returns:
            option (str): The name of the option."""
        return self.options[index]

    def set(self, value, force=False, emit=True):
        """Sets the value with extra clamping functionality.

        Args:
            value (int or float): The value to give the setting.
            force (bool, optional): If True, ignores the locked state.
        """
        try:
            if isinstance(value, str):
                if self.option_exists(value):
                    super().set(value, force=force)
                else:
                    logger.error(f"value {value} is not in options {self.options}")
            elif isinstance(value, int):
                super().set(self.get_option_from_index(value), force=force)
            elif value is None:
                super().set(None, force=force)
            else:
                logger.error(f"{self.name} - Enum.set(value) requires a string (option) or int (index)")
        except:
            pass
        return self

    def set_option_data(self, option, option_data=None):
        """Sets the option data for the given option. This is similar to having meta data for each option that
        you want access to at any point.

        Args:
            option (str): The option you want to assign the meta data to
            option_data (Any, optional): The meta data you want to assign
        """
        if self.option_exists(option):
            self._OPTION_DATA[option] = option_data
            self.option_data_changed.emit(data=self.option_data)
            self.set_object_data("option_data", self.option_data)
        else:
            logger.error(f"Option {option} does not exist on setting {self.name}")


class Matrix(Compound):
    def __init__(self, name, parent=None, locked=False, hidden=False, hint=None):
        super().__init__(name, parent, locked, hidden, hint)
        self._TRANSLATE = FloatVector3(name="translate")
        self._ROTATE = FloatVector3(name="rotate")
        self._SCALE = FloatVector3(name="scale")

    @property
    def translate(self):
        return self._TRANSLATE

    @property
    def rotate(self):
        return self._ROTATE

    @property
    def scale(self):
        return self._SCALE

    def _update_value(self):
        self._VALUE = [self.translate.get(), self.rotate.get(), self.scale.get()]
        self.value_changed.emit(value=self.value)

    def set(self, translate, rotate, scale, force=False):
        self.translate.set(translate[0], translate[1], translate[2], force=force)
        self.rotate.set(rotate[0], rotate[1], rotate[2], force=force)
        self.scale.set(scale[0], scale[1], scale[2], force=force)
        self._update_value()
        return self

# vector settings
class _Vector2(Compound):
    def __init__(self, name, data_type, x, y, parent=None, locked=False, hidden=False, hint=None):
        super().__init__(name, parent, locked, hidden, hint)
        if isinstance(data_type, float):
            self._X = self.add_attribute(Float(name="x", value=x, locked=locked, hidden=hidden, hint=hint))
            self._Y = self.add_attribute(Float(name="y", value=y, locked=locked, hidden=hidden, hint=hint))
        elif isinstance(data_type, int):
            self._X = self.add_attribute(Integer(name="x", value=x, locked=locked, hidden=hidden, hint=hint))
            self._Y = self.add_attribute(Integer(name="y", value=y, locked=locked, hidden=hidden, hint=hint))

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
            self._X = self.add_attribute(Float(name="x", value=x, locked=locked, hidden=hidden, hint=hint))
            self._Y = self.add_attribute(Float(name="y", value=y, locked=locked, hidden=hidden, hint=hint))
            self._Z = self.add_attribute(Float(name="z", value=z, locked=locked, hidden=hidden, hint=hint))
        elif isinstance(data_type, int):
            self._X = self.add_attribute(Integer(name="x", value=x, locked=locked, hidden=hidden, hint=hint))
            self._Y = self.add_attribute(Integer(name="y", value=y, locked=locked, hidden=hidden, hint=hint))
            self._Z = self.add_attribute(Integer(name="z", value=z, locked=locked, hidden=hidden, hint=hint))

        self.x.value_changed.connect(self._update_value)
        self.y.value_changed.connect(self._update_value)
        self.z.value_changed.connect(self._update_value)

    @property
    def x(self):
        return self._X

    @property
    def y(self):
        return self._Y

    @property
    def z(self):
        return self._Z

    def _update_value(self):
        self._VALUE = [self.x.get(), self.y.get(), self.z.get()]
        self.value_changed.emit(value=self.value)

    def set_x(self, value, force=False, emit=True):
        self.x.set(value, force=force, emit=emit)
        return self.x

    def set_y(self, value, force=False, emit=True):
        self.y.set(value, force=force, emit=emit)
        return self.y

    def set_z(self, value, force=False, emit=True):
        self.z.set(value, force=force, emit=emit)
        return self.z

    def set(self, x, y, z, force=False):
        self.set_x(x, force=force, emit=False)
        self.set_y(y, force=force, emit=False)
        self.set_z(z, force=force, emit=False)
        self._update_value()
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
            self._X = self.add_attribute(Float(name="x", value=x, locked=locked, hidden=hidden, hint=hint))
            self._Y = self.add_attribute(Float(name="y", value=y, locked=locked, hidden=hidden, hint=hint))
            self._Z = self.add_attribute(Float(name="z", value=z, locked=locked, hidden=hidden, hint=hint))
            self._W = self.add_attribute(Float(name="w", value=w, locked=locked, hidden=hidden, hint=hint))
        elif isinstance(data_type, int):
            self._X = self.add_attribute(Integer(name="x", value=x, locked=locked, hidden=hidden, hint=hint))
            self._Y = self.add_attribute(Integer(name="y", value=y, locked=locked, hidden=hidden, hint=hint))
            self._Z = self.add_attribute(Integer(name="z", value=z, locked=locked, hidden=hidden, hint=hint))
            self._W = self.add_attribute(Integer(name="w", value=w, locked=locked, hidden=hidden, hint=hint))

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
    """This is a Compound setting that has 2 Int settings as children.

    Args:
        name (str): The name of this setting
        x (int, optional): The value of the first setting with the name of 'x'
        y (int, optional): The value of the first setting with the name of 'y'
        parent (Any, optional): The parent of this setting
        locked (bool, optional): If True, this setting can only be set using self.set(value, force=True)
        hidden (bool, optional): If True, this setting will be hidden in ui elements
        hint (str, optional): The hint/tooltip to give this setting
    """

    def __init__(self, name, x=0, y=0, parent=None, locked=False, hidden=False, hint=None):
        super().__init__(name, int(), x, y, parent, locked, hidden, hint)


class IntVector3(_Vector3):
    """This is a Compound setting that has 3 Int settings as children.
    Args:
        name (str): The name of this setting
        x (int, optional): The value of the first setting with the name of 'x'
        y (int, optional): The value of the first setting with the name of 'y'
        z (int, optional): The value of the first setting with the name of 'z'
        parent (Any, optional): The parent of this setting
        locked (bool, optional): If True, this setting can only be set using self.set(value, force=True)
        hidden (bool, optional): If True, this setting will be hidden in ui elements
        hint (str, optional): The hint/tooltip to give this setting
    """

    def __init__(self, name, x=0, y=0, z=0, parent=None, locked=False, hidden=False, hint=None):
        super().__init__(name, int(), x, y, z, parent, locked, hidden, hint)


class IntVector4(_Vector4):
    """This is a Compound setting that has 4 Int settings as children.

    Args:
        name (str): The name of this setting
        x (int, optional): The value of the first setting with the name of 'x'
        y (int, optional): The value of the first setting with the name of 'y'
        z (int, optional): The value of the first setting with the name of 'z'
        w (int, optional): The value of the first setting with the name of 'w'
        parent (Any, optional): The parent of this setting
        locked (bool, optional): If True, this setting can only be set using self.set(value, force=True)
        hidden (bool, optional): If True, this setting will be hidden in ui elements
        hint (str, optional): The hint/tooltip to give this setting
    """

    def __init__(self, name, x=0, y=0, z=0, w=0, parent=None, locked=False, hidden=False, hint=None):
        super().__init__(name, int(), x, y, z, w, parent, locked, hidden, hint)


class FloatVector2(_Vector2):
    """This is a Compound setting that has 2 Float settings as children.

    Args:
        name (str): The name of this setting
        x (float, optional): The value of the first setting with the name of 'x'
        y (float, optional): The value of the first setting with the name of 'y'
        parent (Any, optional): The parent of this setting
        locked (bool, optional): If True, this setting can only be set using self.set(value, force=True)
        hidden (bool, optional): If True, this setting will be hidden in ui elements
        hint (str, optional): The hint/tooltip to give this setting
    """

    def __init__(self, name, x=0.0, y=0.0, parent=None, locked=False, hidden=False, hint=None):
        super().__init__(name, float(), x, y, parent, locked, hidden, hint)


class FloatVector3(_Vector3):
    """This is a Compound setting that has 3 Float settings as children.

    Args:
        name (str): The name of this setting
        x (float, optional): The value of the first setting with the name of 'x'
        y (float, optional): The value of the first setting with the name of 'y'
        z (float, optional): The value of the first setting with the name of 'z'
        parent (Any, optional): The parent of this setting
        locked (bool, optional): If True, this setting can only be set using self.set(value, force=True)
        hidden (bool, optional): If True, this setting will be hidden in ui elements
        hint (str, optional): The hint/tooltip to give this setting
    """

    def __init__(self, name, x=0.0, y=0.0, z=0.0, parent=None, locked=False, hidden=False, hint=None):
        super().__init__(name, float(), x, y, z, parent, locked, hidden, hint)


class FloatVector4(_Vector4):
    """This is a Compound setting that has 4 Float settings as children.

    Args:
        name (str): The name of this setting
        x (float, optional): The value of the first setting with the name of 'x'
        y (float, optional): The value of the first setting with the name of 'y'
        z (float, optional): The value of the first setting with the name of 'z'
        w (float, optional): The value of the first setting with the name of 'w'
        parent (Any, optional): The parent of this setting
        locked (bool, optional): If True, this setting can only be set using self.set(value, force=True)
        hidden (bool, optional): If True, this setting will be hidden in ui elements
        hint (str, optional): The hint/tooltip to give this setting
    """

    def __init__(self, name, x=0.0, y=0.0, z=0.0, w=0.0, parent=None, locked=False, hidden=False, hint=None):
        super().__init__(name, float(), x, y, z, w, parent, locked, hidden, hint)


# color settings
class _RGB(Compound):
    def __init__(self, name, data_type, r, g, b, parent=None, locked=False, hidden=False, hint=None):
        super().__init__(name, parent, locked, hidden, hint)
        if isinstance(data_type, float):
            self._R = self.add_attribute(Float(name="r", value=r, locked=locked, hidden=hidden, hint=hint))
            self._G = self.add_attribute(Float(name="g", value=g, locked=locked, hidden=hidden, hint=hint))
            self._B = self.add_attribute(Float(name="b", value=b, locked=locked, hidden=hidden, hint=hint))
        elif isinstance(data_type, int):
            self._R = self.add_attribute(Integer(name="r", value=r, locked=locked, hidden=hidden, hint=hint))
            self._G = self.add_attribute(Integer(name="g", value=g, locked=locked, hidden=hidden, hint=hint))
            self._B = self.add_attribute(Integer(name="b", value=b, locked=locked, hidden=hidden, hint=hint))

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
            self._R = self.add_attribute(Float(name="r", value=r, locked=locked, hidden=hidden, hint=hint))
            self._G = self.add_attribute(Float(name="g", value=g, locked=locked, hidden=hidden, hint=hint))
            self._B = self.add_attribute(Float(name="b", value=b, locked=locked, hidden=hidden, hint=hint))
            self._A = self.add_attribute(Float(name="a", value=a, locked=locked, hidden=hidden, hint=hint))
        elif isinstance(data_type, int):
            self._R = self.add_attribute(Integer(name="r", value=r, locked=locked, hidden=hidden, hint=hint))
            self._G = self.add_attribute(Integer(name="g", value=g, locked=locked, hidden=hidden, hint=hint))
            self._B = self.add_attribute(Integer(name="b", value=b, locked=locked, hidden=hidden, hint=hint))
            self._A = self.add_attribute(Integer(name="a", value=a, locked=locked, hidden=hidden, hint=hint))

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
    """This is a Compound setting that has 3 Int settings as children.

    Args:
        name (str): The name of this setting
        r (int, optional): The value of the first setting with the name of 'r'
        g (int, optional): The value of the first setting with the name of 'g'
        b (int, optional): The value of the first setting with the name of 'b'
        parent (Any, optional): The parent of this setting
        locked (bool, optional): If True, this setting can only be set using self.set(value, force=True)
        hidden (bool, optional): If True, this setting will be hidden in ui elements
        hint (str, optional): The hint/tooltip to give this setting
    """

    def __init__(self, name, r=0, g=0, b=0, parent=None, locked=False, hidden=False, hint=None):
        super().__init__(name, int(), r, g, b, parent, locked, hidden, hint)


class FloatRGB(_RGB):
    """This is a Compound setting that has 3 Float settings as children.

    Args:
        name (str): The name of this setting
        r (float, optional): The value of the first setting with the name of 'r'
        g (float, optional): The value of the first setting with the name of 'g'
        b (float, optional): The value of the first setting with the name of 'b'
        parent (Any, optional): The parent of this setting
        locked (bool, optional): If True, this setting can only be set using self.set(value, force=True)
        hidden (bool, optional): If True, this setting will be hidden in ui elements
        hint (str, optional): The hint/tooltip to give this setting
    """

    def __init__(self, name, r=0, g=0, b=0, parent=None, locked=False, hidden=False, hint=None):
        super().__init__(name, float(), r, g, b, parent, locked, hidden, hint)


class IntRGBA(_RGBA):
    """This is a Compound setting that has 4 Int settings as children.

    Args:
        name (str): The name of this setting
        r (int, optional): The value of the first setting with the name of 'r'
        g (int, optional): The value of the first setting with the name of 'g'
        b (int, optional): The value of the first setting with the name of 'b'
        a (int, optional): The value of the first setting with the name of 'a'
        parent (Any, optional): The parent of this setting
        locked (bool, optional): If True, this setting can only be set using self.set(value, force=True)
        hidden (bool, optional): If True, this setting will be hidden in ui elements
        hint (str, optional): The hint/tooltip to give this setting
    """

    def __init__(self, name, r=0, g=0, b=0, a=0, parent=None, locked=False, hidden=False, hint=None):
        super().__init__(name, int(), r, g, b, a, parent, locked, hidden, hint)


class FloatRGBA(_RGBA):
    """This is a Compound setting that has 4 Float settings as children.

    Args:
        name (str): The name of this setting
        r (float, optional): The value of the first setting with the name of 'r'
        g (float, optional): The value of the first setting with the name of 'g'
        b (float, optional): The value of the first setting with the name of 'b'
        a (float, optional): The value of the first setting with the name of 'a'
        parent (Any, optional): The parent of this setting
        locked (bool, optional): If True, this setting can only be set using self.set(value, force=True)
        hidden (bool, optional): If True, this setting will be hidden in ui elements
        hint (str, optional): The hint/tooltip to give this setting
    """

    def __init__(self, name, r=0, g=0, b=0, a=1, parent=None, locked=False, hidden=False, hint=None):
        super().__init__(name, float(), r, g, b, a, parent, locked, hidden, hint)
