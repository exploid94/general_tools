from genesis.core.bases import base_object
from genesis.core import signal
from genesis.utils import constants, logging

logger = logging.get_logger(__name__, level=constants.WARNING)

class BaseAttribute(base_object.BaseObject):
    """Base class for all attributes. This base class takes care of all general functionality.
    This is a sub class of a BaseObject.

    Args:
        name (str): The name of the attribute.
        value (data_type): The value to give the attribute.
        data_type (Any): The data type to give the attribute. This is default python data types.
        parent (object): The parent of the attribute.
        locked (bool): If True, the attribute cannot be set, unless you use force=True.
        hidden (bool): The attribute hidden state.
        hint (str) (optional): A description of the attribute.
        _set (bool) (optional): If False, the value won't be set during initialization.

    """

    def __init__(self, name, value, data_type=any, parent=None, locked=False, hidden=False, hint=None, _set=True):
        self._NAME = name
        self._NICE_NAME = name.replace("_", " ").title()
        self._VALUE = None
        self._DEFAULT_VALUE = None
        self._IS_OVERRIDDEN = None
        self._DATA_TYPE = data_type
        self._PARENT = parent
        self._LOCKED = locked
        self._HIDDEN = hidden
        self._HINT = hint
        self._CONNECTED_SIGNAL = None
        self._CONNECTED_ATTRIBUTE = None

        self._SIGNAL_NAME_CHANGED = signal.Signal()
        self._SIGNAL_VALUE_CHANGED = signal.Signal()
        self._SIGNAL_PARENT_CHANGED = signal.Signal()
        self._SIGNAL_HIDDEN_CHANGED = signal.Signal()
        self._SIGNAL_LOCKED_CHANGED = signal.Signal()
        self._SIGNAL_HINT_CHANGED = signal.Signal()
        self._SIGNAL_IS_OVERRIDDEN_CHANGED = signal.Signal()
        self._SIGNAL_DEFAULT_VALUE_CHANGED = signal.Signal()

        super().__init__()

        self.set_object_data(constants.NAME, self.name)
        self.set_object_data(constants.VALUE, self.value)
        self.set_object_data(constants.LOCKED, self.locked)
        self.set_object_data(constants.HIDDEN, self.hidden)
        self.set_object_data(constants.HINT, self.hint)
        self.set_temp_data(constants.PREVIOUS_VALUE, self.value)

        if _set:
            self.set_default_value(value, force=True)
            self.set(value, force=True)

    @property
    def name(self):
        """str: The name of this attribute"""
        return self._NAME

    @property
    def nice_name(self):
        """str: The nice name of this attribute"""
        return self._NICE_NAME

    @property
    def value(self):
        """self.data_type: The current value that this attribute is set to."""
        return self._VALUE

    @property
    def previous_value(self):
        """self.data_type: The previous value that this attribute was set to."""
        return self.temp_data[constants.PREVIOUS_VALUE]

    @property
    def is_overridden(self):
        """bool: Returns whether or not self.value differs from self.default_value."""
        return self._IS_OVERRIDDEN

    @property
    def default_value(self):
        """self.data_type: The default value of this attribute. Allows users to always go to a default value if they wish."""
        return self._DEFAULT_VALUE

    @property
    def data_type(self):
        """Any: The data type of this attribute. This is specified when creating a specific data type attribute light Float or Int"""
        return self._DATA_TYPE

    @property
    def parent(self):
        """Any: The parent of this attribute."""
        return self._PARENT

    @property
    def locked(self):
        """bool: The locked state of this attribute. If True, disables ui elements"""
        return self._LOCKED

    @property
    def hidden(self):
        """bool: The hidden state of this attribute. If True hides UI elements"""
        return self._HIDDEN

    @property
    def hint(self):
        """str: The tooltip hint to apply to this attribute for other users to have useful info when hovering over ui elements."""
        return self._HINT

    @property
    def name_changed(self):
        """signal.PublishSignal: name_changed.emit(name)."""
        return self._SIGNAL_NAME_CHANGED

    @property
    def value_changed(self):
        """signal.PublishSignal: value_changed.emit(value)."""
        return self._SIGNAL_VALUE_CHANGED

    @property
    def parent_changed(self):
        """signal.PublishSignal: parent_changed.emit(parent)."""
        return self._SIGNAL_PARENT_CHANGED

    @property
    def hidden_changed(self):
        """signal.PublishSignal: hidden_changed.emit(hidden)."""
        return self._SIGNAL_HIDDEN_CHANGED

    @property
    def locked_changed(self):
        """signal.PublishSignal: locked_changed.emit(locked)."""
        return self._SIGNAL_LOCKED_CHANGED

    @property
    def hint_changed(self):
        """signal.PublishSignal: hint_changed.emit(hint)."""
        return self._SIGNAL_HINT_CHANGED

    @property
    def is_overridden_changed(self):
        """signal.PublishSignal: is_overridden_changed.emit(is_overridden)."""
        return self._SIGNAL_IS_OVERRIDDEN_CHANGED

    @property
    def default_value_changed(self):
        """signal.PublishSignal: default_value_changed.emit(value)."""
        return self._SIGNAL_DEFAULT_VALUE_CHANGED

    @property
    def connected_signal(self):
        return self._CONNECTED_SIGNAL

    @property
    def connected_attribute(self):
        return self._CONNECTED_ATTRIBUTE

    def rename(self, name):
        """Renames the attribute to the name given.

        Args:
            name (str): The name to give the attribute.

        Returns:
            attribute: The attribute
        """
        if isinstance(name, str):
            if self.name != name:
                self._NAME = name
                self._NICE_NAME = name.replace("_", " ").title()
                self.set_object_data("name", self.name)
                self.name_changed.emit(name=name)
            return self
        else:
            logger.error("name {name} is not of type str")

    def get(self):
        """Returns the current value of the attribute."""
        return self.value

    def set(self, value, force=False, emit=True):
        """Sets the value of the attribute. Force=True can override locked=True.

        Args:
            value (self.data_type): The value to give the attribute.
            force (bool): If True, sets the value even if its locked.

        Returns:
            attribute: The attribute
        """
        if self.locked and not force:
            logger.exception(f'[attribute.{self.name}] Cannot edit locked attribute!')

        if (self.data_type is any) or isinstance(value, self.data_type):
            # set the previous value
            self.set_temp_data(constants.PREVIOUS_VALUE, self.value)
            # set the value if it is not the current value
            if value != self.value:
                self._VALUE = value
                self.set_object_data(constants.VALUE, value)
                if emit:
                    self.value_changed.emit(value=value)
                self._set_is_overridden()
            return self
        else:
            logger.warning(
                f"value {value} from attribute '{self.parent}.{self.name}' is not a {self.data_type}. Will attempt to convert it.")

    def lock(self):
        """Locks the attribute so the value cannot normally be set.

        Returns:
            attribute: The attribute
        """
        if self.locked is not True:
            self._LOCKED = True
            self.set_object_data(constants.LOCKED, True)
            self.locked_changed.emit(locked=True)
        return self

    def unlock(self):
        """Unlocks the attribute so the attribute can normally be set.

        Returns:
            attribute: The attribute
        """
        if self.locked is not False:
            self._LOCKED = False
            self.set_object_data(constants.LOCKED, False)
            self.locked_changed.emit(locked=False)
        return self

    def hide(self):
        """Sets the attribute's hidden state to True.

        Returns:
            attribute: The attribute
        """
        if self.hidden is not True:
            self._HIDDEN = True
            self.set_object_data(constants.HIDDEN, True)
            self.hidden_changed.emit(hidden=True)
        return self

    def unhide(self):
        """Sets the attribute's hidden state to False.

        Returns:
            attribute: The attribute
        """
        if self.hidden is not False:
            self._HIDDEN = False
            self.set_object_data(constants.HIDDEN, False)
            self.hidden_changed.emit(hidden=False)
        return self

    def set_hint(self, hint):
        """Sets the hint of the attribute to the given string.

        Args:
            hint (str): A description of the attribute.

        Returns:
            attribute: The attribute
        """
        if isinstance(hint, str):
            if self.hint != hint:
                self._HINT = hint
                self.set_object_data(constants.HINT, hint)
                self.hint_changed.emit(hint=hint)
            return self
        else:
            logger.error("hint must be a string")

    def set_parent(self, parent):
        """Sets the parent of the attribute.

        Args:
            parent (object): The parent to give the attribute.

        Returns:
            attribute: The attribute
        """
        if self.parent != parent:
            self._PARENT = parent
            self.parent_changed.emit(parent=parent)
        return self

    def set_default_value(self, value, force=False):
        """Sets the default value of the attribute. Default value can be used along with value overrides.

        Args:
            value (self.data_type): The default value to give the attribute.
            force (bool) (optional): If True, set() will ignore locked state.

        Returns:
            attribute: The attribute
        """
        if self.locked and not force:
            logger.exception(f'[attribute.{self.name}] Cannot edit locked attribute!')

        if (self.data_type is any) or isinstance(value, self.data_type):
            if value != self.default_value:
                self._DEFAULT_VALUE = value
                self.default_value_changed.emit(value=value)
                self._set_is_overridden()
            return self
        else:
            logger.error(f"default_value {value} from attribute '{self.parent}.{self.name}' is not a {self.data_type}")

    def copy(self, name=None):
        pass

    def _set_is_overridden(self):
        """Checks and sets if the value differs from the default value."""
        # set the override state if it's not the default value
        if self.value == self.default_value:
            self._IS_OVERRIDDEN = False
        else:
            self._IS_OVERRIDDEN = True
        self.is_overridden_changed.emit(is_overridden=self.is_overridden)

    def connect(self, attribute):
        """Connects another attribute to this attributes value"""
        self.disconnect()
        self.set(attribute.value, force=True)
        self._CONNECTED_SIGNAL = attribute.value_changed.connect(lambda: self.set(attribute.value, force=True))
        self._CONNECTED_ATTRIBUTE = attribute
        self.lock()

    def disconnect(self):
        """Connects another attribute to this attributes value"""
        if self.connected_signal:
            self.connected_attribute.value_changed.disconnect(self.connected_signal)
            self._CONNECTED_ATTRIBUTE = None
            self._CONNECTED_SIGNAL = None
            self.unlock()