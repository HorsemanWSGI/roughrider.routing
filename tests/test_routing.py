import http
import webtest
import pytest
import horseman.http
import horseman.response


def test_resolve(node):

    @node.route('/getter', methods=['GET'])
    def fake_route(request):
        return horseman.response.Response(200, body=b'OK !')

    environ = {'REQUEST_METHOD': 'GET'}
    result = node.resolve('/getter', environ)
    assert isinstance(result, horseman.response.Response)

    with pytest.raises(horseman.http.HTTPError) as exc:
        node.resolve('/getter', {'REQUEST_METHOD': 'POST'})

    # METHOD UNALLOWED.
    assert exc.value.status == http.HTTPStatus(405)


def test_wsgi_roundtrip(node):

    app = webtest.TestApp(node)
    response = app.get('/getter', status=404)
    assert response.body == b'Nothing matches the given URI'

    @node.route('/getter', methods=['GET'])
    def fake_route(request):
        return horseman.response.Response(200, body=b'OK !')

    response = app.get('/getter')
    assert response.body == b'OK !'

    response = app.post('/getter', status=405)
    assert response.body == (
        b'Specified method is invalid for this resource')
