import typing as t
from horseman.meta import Overhead
from horseman.types import WSGICallable, HTTPMethod


Endpoint = t.Callable[[Overhead], WSGICallable]
HTTPMethods = t.Iterable[HTTPMethod]


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
