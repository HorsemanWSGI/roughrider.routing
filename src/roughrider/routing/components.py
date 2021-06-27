from typing import Type
from horseman.meta import Overhead, Node
from roughrider.routing.route import Routes, Route


class RoutingRequest(Overhead):
    route: Route


class RoutingNode(Node):
    routes: Routes
    request_factory: Type[RoutingRequest]

    def route(self, path: str, methods: list = None, **extras):
        return self.routes.register(path, methods, **extras)
