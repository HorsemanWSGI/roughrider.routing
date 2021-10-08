import pytest
from horseman.meta import Overhead, Node
from roughrider.routing.components import Routes


class MockOverhead(Overhead):

    def __init__(self, node, environ, route):
        self.node = node
        self.environ = environ
        self.route = route
        self._data = {}

    def extract(self):
        pass


class MockRoutingNode(Node):

    def __init__(self):
        self.routes = Routes()

    def resolve(self, path: str, environ: dict):
        route = self.routes.match_method(path, environ['REQUEST_METHOD'])
        if route is not None:
            request = MockOverhead(self, environ, route)
            return route.endpoint(request, **route.params)


@pytest.fixture
def node():
    return MockRoutingNode()
