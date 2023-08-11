def singleton(cls):
    _instance = {}

    def get_instance(*args, **kwargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kwargs)
        return _instance[cls]

    return get_instance

def singleton_with_initializer(initializer_func):
    instances = {}

    def decorator(cls):
        def get_instance(*args, **kwargs):
            if cls not in instances:
                instance = cls(*args, **kwargs)
                initializer_func(instance, *args, **kwargs)
                instances[cls] = instance
            return instances[cls]
        return get_instance
    return decorator