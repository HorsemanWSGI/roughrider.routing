import pytest
from roughrider.routing.route import (
    NamedRoutes, RouteDefinition, RouteEndpoint)


def test_merge_add_operation_decorator():
    router1 = NamedRoutes()
    router2 = NamedRoutes()

    @router1.register('/test', name="obj")
    def obj_get(request):
        pass

    @router2.register('/test', methods=['POST'], name="obj")
    def obj_post(request):
        pass

    router3 = router1 + router2
    assert list(router3.names_mapping) == [
        ('obj', '/test')
    ]


def test_merge_add_operation_decorator_diff_names():
    router1 = NamedRoutes()
    router2 = NamedRoutes()

    @router1.register('/test', methods=['GET'], name="get_obj")
    def obj_get(request):
        pass

    @router2.register('/test', methods=['POST'], name="post_obj")
    def obj_post(request):
        pass

    router3 = router1 + router2
    assert list(router3.names_mapping) == [
        ('get_obj', '/test'),
        ('post_obj', '/test')
    ]

    # WARNING : the route payload will be updated to the LAST name.
    assert list(router3) == [
        RouteDefinition(path='/test', payload={
            'GET': RouteEndpoint(
                method='GET',
                endpoint=obj_get,
                metadata={"name": "get_obj"}
            ),
            'POST': RouteEndpoint(
                method='POST',
                endpoint=obj_post,
                metadata={"name": "post_obj"}
            )
        }),
    ]


def test_add_operation_decorator_view_class():
    import hamcrest
    from horseman.meta import APIView

    router1 = NamedRoutes()
    router2 = NamedRoutes()

    @router1.register('/view/{id}', name='my_view')
    @router2.register('/object_view/{oid}', name='object_view')
    class View(APIView):

        def GET(request):
            pass

        def POST(request):
            pass

        def something_else(self):
            pass

    router3 = router1 + router2
    assert list(router3.names_mapping) == [
        ('my_view', '/view/{id}'),
        ('object_view', '/object_view/{oid}')
    ]

    hamcrest.assert_that(list(router3), hamcrest.contains_exactly(
        hamcrest.has_properties({
            'path': '/view/{id}',
            'payload': hamcrest.has_entries({
                'GET': hamcrest.contains_exactly(
                    'GET',
                    hamcrest.has_property(
                        '__func__', hamcrest.is_(View.GET)
                    ),
                    {"name": "my_view"}
                ),
                'POST': hamcrest.contains_exactly(
                    'POST',
                    hamcrest.has_property(
                        '__func__', hamcrest.is_(View.POST)
                    ),
                    {"name": "my_view"}
                ),
            })
        }),
        hamcrest.has_properties({
            'path': '/object_view/{oid}',
            'payload': hamcrest.has_entries({
                'GET': hamcrest.contains_exactly(
                    'GET',
                    hamcrest.has_property(
                        '__func__', hamcrest.is_(View.GET)
                    ),
                    {"name": "object_view"}
                ),
                'POST': hamcrest.contains_exactly(
                    'POST',
                    hamcrest.has_property(
                        '__func__', hamcrest.is_(View.POST)
                    ),
                    {"name": "object_view"}
                ),
            })
        }),
    ))


def test_merge_add_operation_decorator_view_class():
    import hamcrest
    from horseman.meta import APIView

    router1 = NamedRoutes()
    router2 = NamedRoutes()

    @router1.register('/item/{id}', name='item')
    class Browser(APIView):

        def GET(request):
            pass

        def POST(request):
            pass

    @router2.register('/item/{id}', name="crud")
    class REST(APIView):

        def PUT(request):
            pass

        def PATCH(request):
            pass

        def DELETE(request):
            pass

    router3 = router1 + router2
    assert list(router3.names_mapping) == [
        ('item', '/item/{id}'),
        ('crud', '/item/{id}'),
    ]

    hamcrest.assert_that(list(router3), hamcrest.contains_exactly(
        hamcrest.has_properties({
            'path': '/item/{id}',
            'payload': hamcrest.has_entries({
                'GET': hamcrest.contains_exactly(
                    'GET',
                    hamcrest.has_property(
                        '__func__', hamcrest.is_(Browser.GET)
                    ),
                    {"name": "item"}
                ),
                'POST': hamcrest.contains_exactly(
                    'POST',
                    hamcrest.has_property(
                        '__func__', hamcrest.is_(Browser.POST)
                    ),
                    {"name": "item"}
                ),
                'PUT': hamcrest.contains_exactly(
                    'PUT',
                    hamcrest.has_property(
                        '__func__', hamcrest.is_(REST.PUT)
                    ),
                    {"name": "crud"}
                ),
                'PATCH': hamcrest.contains_exactly(
                    'PATCH',
                    hamcrest.has_property(
                        '__func__', hamcrest.is_(REST.PATCH)
                    ),
                    {"name": "crud"}
                ),
                'DELETE': hamcrest.contains_exactly(
                    'DELETE',
                    hamcrest.has_property(
                        '__func__', hamcrest.is_(REST.DELETE)
                    ),
                    {"name": "crud"}
                )
            })
        })
    ))
