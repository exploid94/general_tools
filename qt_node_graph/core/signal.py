class Signal:
    def __init__(self, name=None, *args):
        self._functions = {}
        if not name:
            name = self
        self._NAME = name

    @property
    def functions(self):
        return self._functions

    @property
    def name(self):
        return self._NAME

    def _add_callback(self, func):
        s_id = hex(id(func))
        self._functions[s_id] = func
        return s_id

    def _remove_callback(self, s_id):
        if s_id in self._functions:
            return self._functions.pop(s_id)

    def connect(self, func):
        """Connect a function to this signal"""
        if isinstance(func, (list, tuple)):
            return [self._add_callback(f) for f in func]
        return self._add_callback(func)

    def disconnect(self, id_):
        """Disconnect a func from this signal through its id"""
        if isinstance(id_, (list, tuple)):
            return {id_: self._remove_callback(s_id) for s_id in id_}
        return self._remove_callback(id_)

    def clear(self):
        """Removes all the functions connected to this signal"""
        self._functions = {}

    def emit(self, **kwargs):
        """Emit this signal with the given kwargs and run any functions connected to this"""
        for func in list(self._functions.values()):
            try:
                func(*kwargs.values())
            except:
                try:
                    func()
                except Exception as e:
                    raise e
