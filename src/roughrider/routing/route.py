import inspect
from horseman.meta import View, APIView


def subroute(func=None, path: str=None, methods: list=None):

    def subrouting(func):
        func.__subroute__ = (
            path is not None and path or func.__name__, methods)
        return func

    if func is not None:
        # Default
        func.__subroute__ = (None, methods)
        return func

    return subrouting


def route_payload(path: str, view, methods: list=None):
    if inspect.isclass(view):
        inst = view()
        members = view_methods(inst)
        if isinstance(inst, APIView):
            for name, func in members:
                yield path, name, func
        else:
            for name, func in members:
                subpath, submethods = getattr(
                    func, '__subroute__', (name, methods))
                for method in submethods or ['GET']:
                    if not subpath:
                        yield path, method or ['GET'], func
                    else:
                        yield f'{path}/{subpath}', method or ['GET'], func
    else:
        if methods is None:
            methods = ['GET']
        for method in methods:
            yield path, method, view


def add_route(router, path: str, methods: list=None, **extras: dict):

    def route_from_view_or_function(view):
        for fullpath, method, func in route_payload(path, view, methods):
            payload = {method: func, **extras}
            router.add(fullpath, **payload)
        return view

    return route_from_view_or_function
