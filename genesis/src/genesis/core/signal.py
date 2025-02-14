
class Signal:
    def __init__(self):
        self._functions = {}
    
    @property
    def functions(self):
        return self._functions

    def _add_callback(self, func):
        s_id = hex(id(func))
        self._functions[s_id] = func
        return s_id

    def _remove_callback(self, s_id):
        if s_id in self._functions:
            return self._functions.pop(s_id)

    def connect(self, func):
        if isinstance(func, (list, tuple)):
            return [self._add_callback(f) for f in func]
        return self._add_callback(func)

    def disconnect(self, id_):
        if isinstance(id_, (list, tuple)):
            return {id_: self._remove_callback(s_id) for s_id in id_}
        return self._remove_callback(id_)
    
    def clear(self):
        self._functions = {}

    def emit(self, **kwargs):
        for func in list(self._functions.values()):
            try:
                func(*kwargs.values())
            except Exception as e:
                func()
