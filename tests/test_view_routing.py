import hamcrest
import pytest
from horseman.meta import APIView
from roughrider.routing.route import get_routables


def view_func(request):
    pass


class SomeCallable:

    def __call__(self, request):
        pass


class View(APIView):

    def GET(request):
        pass

    def HEAD(request):
        pass

    def POST(request):
        pass

    def something_else(self):
        pass


def test_simple_class_payload():
    payload = list(get_routables(SomeCallable))
    hamcrest.assert_that(
        payload, hamcrest.contains_exactly(
            hamcrest.contains_exactly(
                'GET', hamcrest.has_property(
                    '__func__', hamcrest.is_(SomeCallable.__call__))
            ),
        )
    )

    payload = list(get_routables(SomeCallable, methods=['POST']))
    hamcrest.assert_that(
        payload, hamcrest.contains_exactly(
            hamcrest.contains_exactly(
                'POST', hamcrest.has_property(
                    '__func__', hamcrest.is_(SomeCallable.__call__))
            ),
        )
    )

    payload = list(get_routables(SomeCallable, methods=['DELETE', 'POST']))
    hamcrest.assert_that(
        payload, hamcrest.contains_exactly(
            hamcrest.contains_exactly(
                'DELETE', hamcrest.has_property(
                    '__func__', hamcrest.is_(SomeCallable.__call__))
            ),
            hamcrest.contains_exactly(
                'POST', hamcrest.has_property(
                    '__func__', hamcrest.is_(SomeCallable.__call__))
            ),
        )
    )


def test_simple_instance_payload():
    inst = SomeCallable()

    with pytest.raises(ValueError) as exc:
        list(get_routables(inst))

    assert str(exc.value) == (
        f'Unknown type of route: {inst}.')


def test_view_class_payload():
    payload = list(get_routables(View))
    hamcrest.assert_that(
        payload, hamcrest.contains_exactly(
            hamcrest.contains_exactly(
                'GET', hamcrest.has_property(
                    '__func__', hamcrest.is_(View.GET))
            ),
            hamcrest.contains_exactly(
                'HEAD', hamcrest.has_property(
                    '__func__', hamcrest.is_(View.HEAD))
            ),
            hamcrest.contains_exactly(
                'POST', hamcrest.has_property(
                    '__func__', hamcrest.is_(View.POST))
            ),
        )
    )

    with pytest.raises(AttributeError) as exc:
        list(get_routables(View, methods=['POST']))

    assert str(exc.value) == (
        'Registration of APIView does not accept methods.')


def test_view_instance_payload():
    inst = View()
    payload = list(get_routables(inst))
    hamcrest.assert_that(
        payload, hamcrest.contains_exactly(
            ('GET', inst.GET),
            ('HEAD', inst.HEAD),
            ('POST', inst.POST)
        )
    )

    with pytest.raises(AttributeError) as exc:
        list(get_routables(inst, methods=['POST']))

    assert str(exc.value) == (
        'Registration of APIView does not accept methods.')
