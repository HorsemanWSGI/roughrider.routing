import http
import autoroutes
import webtest
import pytest
import horseman.meta
import horseman.http
import horseman.response


def fake_route(request):
    return horseman.response.Response.create(200, body=b'OK !')


def failing_route(request):
    raise RuntimeError('Oh, I failed !')


class TestRoutingNode:

    def test_resolve(self, node):
        node.route('/getter', methods=['GET'])(fake_route)

        environ = {'REQUEST_METHOD': 'GET'}
        result = node.resolve('/getter', environ)
        assert isinstance(result, horseman.response.Response)

        with pytest.raises(horseman.http.HTTPError) as exc:
            node.resolve('/getter', {'REQUEST_METHOD': 'POST'})

        # METHOD UNALLOWED.
        assert exc.value.status == http.HTTPStatus(405)

    def test_wsgi_roundtrip(self, node):
        node.route('/getter', methods=['GET'])(fake_route)
        app = webtest.TestApp(node)

        response = app.get('/', status=404)
        assert response.body == b'Nothing matches the given URI'

        response = app.get('/getter')
        assert response.body == b'OK !'

        response = app.post('/getter', status=405)
        assert response.body == (
            b'Specified method is invalid for this resource')
