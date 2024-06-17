from qt_node_graph.core.signal import Signal
from qt_node_graph.core.id import Id
from qt_node_graph.utils import constants


class _BaseAttribute(Id):
    """Base class for all attributes. This base class takes care of all general functionality.
    This is a sub class of an id."""
    def __init__(self, name, value, data_type, parent=None, locked=False, hidden=False, inherit=False, hint=None, _set=True):
        """Initilizes the attribute.

        Args:
            name (str): The name of the attribute.
            value (data_type): The value to give the attribute.
            data_type (Any): The data type to give the attribute. This is default python data types.
            parent (object): The parent of the attribute.
            locked (bool): If True, the attribute cannot be set, unless you use force=True.
            hidden (bool): The attribute hidden state.
            inherit (bool): If True, the value will inherit it's parent value.
            hint (str) (optional): A description of the attribute.
            _set (bool) (optional): If False, the value won't be set during initialization.
        """
        super().__init__()

        self._NAME = name
        self._VALUE = None
        self._DEFAULT_VALUE = None
        self._IS_OVERRIDDEN = None
        self._DATA_TYPE = data_type
        self._PARENT = parent
        self._LOCKED = locked
        self._HIDDEN = hidden
        self._HINT = hint
        self._INHERITED = inherit
        self._LINK = None
        self._WIDGET = None

        self.set_object_data(constants.OBJECT_DATA.NAME, self.name)
        self.set_object_data(constants.OBJECT_DATA.VALUE, self.value)
        self.set_object_data(constants.OBJECT_DATA.LOCKED, self.locked)
        self.set_object_data(constants.OBJECT_DATA.HIDDEN, self.hidden)
        self.set_object_data(constants.OBJECT_DATA.HINT, self.hint)
        self.set_meta_data(constants.META_DATA.CLASS, self.__class__.__name__)
        self.set_meta_data(constants.META_DATA.MODULE, self.__module__)
        self.set_temp_data(constants.TEMP_DATA.PREVIOUS_VALUE, self.value)

        self._SIGNAL_NAME_CHANGED = Signal(name=f"{name}.name_changed")
        self._SIGNAL_VALUE_CHANGED = Signal(name=f"{name}.value_changed")
        self._SIGNAL_PARENT_CHANGED = Signal(name=f"{name}.parent_changed")
        self._SIGNAL_HIDDEN_CHANGED = Signal(name=f"{name}.hidden_changed")
        self._SIGNAL_LOCKED_CHANGED = Signal(name=f"{name}.locked_changed")
        self._SIGNAL_HINT_CHANGED = Signal(name=f"{name}.hint_changed")
        self._SIGNAL_IS_OVERRIDDEN_CHANGED = Signal(name=f"{name}.is_overridden_changed")
        self._SIGNAL_DEFAULT_VALUE_CHANGED = Signal(name=f"{name}.default_value_changed")
        self._SIGNAL_INHERITED_CHANGED = Signal(name=f"{name}.inherited_changed")
        self._SIGNAL_LINK_CHANGED = Signal(name=f"{name}.link_changed")

        if _set:
            self.set_default_value(value, force=True)
            self.set(value, force=True)

    @property
    def name(self):
        return self._NAME

    @property
    def value(self):
        return self._VALUE

    @property
    def previous_value(self):
        return self.get_temp_data(constants.TEMP_DATA.PREVIOUS_VALUE)

    @property
    def is_overridden(self):
        return self._IS_OVERRIDDEN

    @property
    def default_value(self):
        return self._DEFAULT_VALUE

    @property
    def data_type(self):
        return self._DATA_TYPE

    @property
    def parent(self):
        return self._PARENT

    @property
    def locked(self):
        return self._LOCKED

    @property
    def hidden(self):
        return self._HIDDEN

    @property
    def inherited(self):
        return self._INHERITED

    @property
    def link(self):
        return self._LINK

    @property
    def widget(self):
        return self._WIDGET

    @property
    def hint(self):
        return self._HINT

    @property
    def name_changed(self):
        """Emission: name_changed.emit(name)."""
        return self._SIGNAL_NAME_CHANGED

    @property
    def value_changed(self):
        """Emission: value_changed.emit(value)."""
        return self._SIGNAL_VALUE_CHANGED

    @property
    def parent_changed(self):
        """Emission: parent_changed.emit(parent)."""
        return self._SIGNAL_PARENT_CHANGED

    @property
    def hidden_changed(self):
        """Emission: hidden_changed.emit(hidden)."""
        return self._SIGNAL_HIDDEN_CHANGED

    @property
    def inherited_changed(self):
        """Emission: inherited_changed.emit(inherited)."""
        return self._SIGNAL_INHERITED_CHANGED

    @property
    def locked_changed(self):
        """Emission: locked_changed.emit(locked)."""
        return self._SIGNAL_LOCKED_CHANGED

    @property
    def hint_changed(self):
        """Emission: hint_changed.emit(hint)."""
        return self._SIGNAL_HINT_CHANGED

    @property
    def is_overridden_changed(self):
        """Emission: is_overridden_changed.emit(is_overridden)."""
        return self._SIGNAL_IS_OVERRIDDEN_CHANGED

    @property
    def default_value_changed(self):
        """Emission: default_value_changed.emit(value)."""
        return self._SIGNAL_DEFAULT_VALUE_CHANGED

    @property
    def link_changed(self):
        """Emission: link_changed.emit(link)."""
        return self._SIGNAL_LINK_CHANGED

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
                self.set_object_data(constants.OBJECT_DATA.NAME, self.name)
                self.name_changed.emit(name=name)
            return self

    def get(self):
        """Gets the current value of the attribute."""
        return self.value

    def set(self, value, force=False):
        """Sets the value of the attribute. Force=True can override locked=True.

        Args:
            value (self.data_type): The value to give the attribute.

        Returns:
            attribute: The attribute
        """
        if isinstance(value, self.data_type):
            # set the previous value
            self.set_temp_data(constants.TEMP_DATA.PREVIOUS_VALUE, self.value)
            # set the value if it is not the current value
            if value != self.value:
                self._VALUE = value
                self.set_object_data(constants.OBJECT_DATA.VALUE, value)
                self.value_changed.emit(value=value)
                self._set_is_overridden()
            return self

    def lock(self):
        """Locks the attribute so the value cannot normally be set.

        Returns:
            attribute: The attribute
        """
        if self.locked != True:
            self._LOCKED = True
            self.set_object_data(constants.OBJECT_DATA.LOCKED, True)
            self.locked_changed.emit(locked=True)
        return self

    def unlock(self):
        """Unlocks the attribute so the attribute can normally be set..

        Returns:
            attribute: The attribute
        """
        if self.locked != False:
            self._LOCKED = False
            self.set_object_data(constants.OBJECT_DATA.LOCKED, False)
            self.locked_changed.emit(locked=False)
        return self

    def hide(self):
        """Sets the attribute's hidden state to True.

        Returns:
            attribute: The attribute
        """
        if self.hidden != True:
            self._HIDDEN = True
            self.set_object_data(constants.OBJECT_DATA.HIDDEN, True)
            self.hidden_changed.emit(hidden=True)
        return self

    def unhide(self):
        """Sets the attribute's hidden state to False.

        Returns:
            attribute: The attribute
        """
        if self.hidden != False:
            self._HIDDEN = False
            self.set_object_data(constants.OBJECT_DATA.HIDDEN, False)
            self.hidden_changed.emit(hidden=False)
        return self

    def set_link(self, attribute):
        if self._LINK != attribute:
            self._LINK = attribute
            self.link_changed.emit(link=attribute)

    def set_inherited(self, inherited):
        """Sets the attribute's inherited state.

        Returns:
            attribute: The attribute
        """
        self._INHERITED = inherited
        self._SIGNAL_INHERITED_CHANGED.emit(inherited=inherited)
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
                self.set_object_data(constants.OBJECT_DATA.HINT, hint)
                self.hint_changed.emit(hint=hint)
            return self

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
        if isinstance(value, self.data_type):
            if value != self.default_value:
                self._DEFAULT_VALUE = value
                self.default_value_changed.emit(value=value)
                self._set_is_overridden()
            return self

    def copy(self, name=None):
        kwargs = {key: value for key, value in self.get_meta_data() if not key.startswith("__")}
        kwargs["name"] = name or kwargs["name"]
        copy_instance = self.__class__(**kwargs)
        return copy_instance

    def _set_is_overridden(self):
        """Checks and sets if the value differs from the default value."""
        # set the override state if it's not the default value
        if self.value == self.default_value:
            if self.is_overridden:
                self.is_overridden_changed.emit(is_overridden=self.is_overridden)
        else:
            if not self.is_overridden:
                self.is_overridden_changed.emit(is_overridden=self.is_overridden)
