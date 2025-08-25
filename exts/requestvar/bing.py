from contextvars import ContextVar


def bind_contextvar(contextvar):
    class ContextVarBind:
        __slots__ = ()

        def __getattr__(self, name):
            return getattr(contextvar.get(), name)

        def __setattr__(self, name, value):
            setattr(contextvar.get(), name, value)

        def __delattr__(self, name):
            delattr(contextvar.get(), name)

        def __getitem__(self, key):
            return contextvar.get()[key]

        def __setitem__(self, key, value):
            contextvar.get()[key] = value

        def __delitem__(self, key):
            del contextvar.get()[key]

    return ContextVarBind()
