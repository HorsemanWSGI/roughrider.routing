import pytest
import roughrider.routing.components
import roughrider.routing.route


class MockOverhead(roughrider.routing.components.RoutingRequest):

    def __init__(self, node, environ, route):
        self.node = node
        self.environ = environ
        self.route = route
        self._data = {}

    def extract(self):
        pass


class MockRoutingNode(roughrider.routing.components.RoutingNode):

    request_factory = MockOverhead

    def __init__(self):
        self.routes = roughrider.routing.route.Routes()

    def resolve(self, path: str, environ: dict):
        route = self.routes.match_method(path, environ['REQUEST_METHOD'])
        if route is not None:
            request = self.request_factory(self, environ, route)
            return route.endpoint(request, **route.params)


@pytest.fixture
def node():
    return MockRoutingNode()
