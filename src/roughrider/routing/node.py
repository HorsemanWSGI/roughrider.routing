from autoroutes import Routes
from http import HTTPStatus
from horseman.meta import Overhead, APINode
from horseman.http import HTTPError
from horseman.util import view_methods
from horseman.prototyping import Environ, WSGICallable
from roughrider.routing.route import add_route


class RoutingNode(APINode):

    routes: Routes
    request_factory: Overhead

    __slots__ = ('routes', 'request_factory')

    def route(self, path: str, methods: list=None, **extras):
        return add_route(self.routes, path, methods, **extras)

    def resolve(self, path_info: str, environ: Environ) -> WSGICallable:
        methods, params = self.routes.match(path_info)
        if methods is None:
            return None
        endpoint = methods.get(environ['REQUEST_METHOD'])
        if endpoint is None:
            raise HTTPError(HTTPStatus.METHOD_NOT_ALLOWED)

        request = self.request_factory(self, environ, **params)
        return endpoint(request)
