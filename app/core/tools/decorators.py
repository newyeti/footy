def singleton(cls):
    _instance = {}

    def get_instance(*args, **kwargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kwargs)
        return _instance[cls]

    return get_instance

def singleton_with_initializer(initializer_func):
    _instances = {}

    def decorator(cls):
        def get_instance(name, *args, **kwargs):
            if name not in _instances:
                instance = cls(name, *args, **kwargs)
                _instances[name] = instance
                initializer_func(instance, *args, **kwargs)
            return _instances[name]
        return get_instance
    return decorator

def qualifier(instance_name):
    def decorator(cls):
        class WrappedClass(cls):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.instance_name = instance_name

        return WrappedClass

    return decorator