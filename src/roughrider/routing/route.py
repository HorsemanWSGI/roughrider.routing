import inspect
import typing as t
from http import HTTPStatus

import autoroutes
from horseman.types import WSGICallable, HTTPMethod
from horseman.meta import Overhead, APIView
from horseman.http import HTTPError


Endpoint = t.Callable[[Overhead], WSGICallable]
HTTPMethods = t.List[HTTPMethod]
METHODS = frozenset(t.get_args(HTTPMethod))


def get_routables(view, methods: HTTPMethods = None) \
      -> t.Generator[t.Tuple[HTTPMethod, Endpoint], None, None]:

    def instance_members(inst):
        if methods is not None:
            raise AttributeError(
                'Registration of APIView does not accept methods.')
        members = inspect.getmembers(
            inst, predicate=(lambda x: inspect.ismethod(x)
                             and x.__name__ in METHODS))
        for name, func in members:
            yield name, func

    if inspect.isclass(view):
        inst = view()
        if isinstance(inst, APIView):
            yield from instance_members(inst)
        else:
            if methods is None:
                methods = ['GET']
            for method in methods:
                if method not in METHODS:
                    raise ValueError(
                        f"'{method}' is not a known HTTP method.")
                yield method, inst.__call__
    elif isinstance(view, APIView):
        yield from instance_members(view)
    elif inspect.isfunction(view):
        if methods is None:
            methods = ['GET']
        for method in methods:
            if method not in METHODS:
                raise ValueError(
                    f"'{method}' is not a known HTTP method.")
            yield method, view
    else:
        raise ValueError(f'Unknown type of route: {view}.')


class RouteEndpoint(t.NamedTuple):
    method: HTTPMethod
    endpoint: Endpoint
    metadata: t.Optional[t.Dict[t.Any, t.Any]] = None

    def __call__(self, *args, **kwargs):
        return self.endpoint(*args, **kwargs)


class RouteDefinition(t.NamedTuple):
    path: str
    payload: t.Dict[HTTPMethod, RouteEndpoint]


class Route(t.NamedTuple):
    path: str
    endpoint: RouteEndpoint
    params: dict


class Routes(autoroutes.Routes):

    __slots__ = ('extractor')

    def __init__(self, extractor=get_routables):
        self.extractor = extractor

    def add(self, path: str, payload: t.Dict[HTTPMethod, RouteEndpoint]):
        super().add(path, **payload)

    def register(self, path: str, methods: HTTPMethods = None, **metadata):
        def routing(view):
            self.add(path, {
                method: RouteEndpoint(
                    endpoint=endpoint,
                    method=method,
                    metadata=metadata or None
                ) for method, endpoint in self.extractor(view, methods)
            })
            return view
        return routing

    def match_method(self, path_info: str, method: HTTPMethod) -> Route:
        found, params = self.match(path_info)
        if found is None:
            return None
        endpoint = found.get(method)
        if endpoint is None:
            raise HTTPError(HTTPStatus.METHOD_NOT_ALLOWED)

        return Route(
            path=path_info,
            params=params,
            endpoint=endpoint,
        )

    def __iter__(self):
        def route_iterator(edges):
            if edges:
                for edge in edges:
                    if edge.child.path:
                        yield RouteDefinition(
                            path=edge.child.path,
                            payload=edge.child.payload)
                    yield from route_iterator(edge.child.edges)
        yield from route_iterator(self.root.edges)

    def __add__(self, router: 'Routes'):
        if not isinstance(router, Routes):
            raise TypeError(
                "unsupported operand type(s) for +: '{self.__class__}'"
                "and '{router.__class__}'")
        routes = self.__class__()
        for routedef in self:
            routes.add(routedef.path, routedef.payload)
        for routedef in router:
            routes.add(routedef.path, routedef.payload)
        return routes


class NamedRoutes(Routes):

    __slots__ = ('_names')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._names = {}

    @property
    def names_mapping(self):
        return self._names.items()

    def has_route(self, name: str):
        return name in self._names

    def url_for(self, name: str, **params):
        path = self._names.get(name)
        if path is None:
            raise LookupError(f'Unknown route `{name}`.')
        try:
            # Raises a KeyError too if some param misses
            return path.format(**params)
        except KeyError:
            raise ValueError(
                f"No route found with name {name} and params {params}.")

    def add(self, path: str, payload: t.Dict[HTTPMethod, RouteEndpoint]):
        for verb, endpoint in payload.items():
            if not endpoint.metadata or not 'name' in endpoint.metadata:
                continue
            if found := self._names.get(endpoint.metadata['name']):
                if path != found:
                    raise NameError(
                        f"Route {name!r} already exists for path {found!r}.")
            self._names[endpoint.metadata['name']] = path
        return super().add(path, payload)
