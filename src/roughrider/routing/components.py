from typing import Type
from horseman.meta import Overhead, APINode
from roughrider.routing.route import Routes, Route


class RoutingRequest(Overhead):
    route: Route


class RoutingNode(APINode):
    routes: Routes
    request_factory: Type[RoutingRequest]

    __slots__ = ('routes', 'request_factory')

    def route(self, path: str, methods: list=None, **extras):
        return self.routes.register(path, methods, **extras)
