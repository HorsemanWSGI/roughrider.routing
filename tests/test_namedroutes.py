import pytest
from roughrider.routing.route import NamedRoutes, RouteDefinition


def test_naming():
    router = NamedRoutes()
    router.add('/test', name='test')
    assert list(router) == [
        RouteDefinition(path='/test', payload={'name': 'test'}),
    ]

    router.add('/test', name='test2')
    assert list(router) == [
        RouteDefinition(path='/test', payload={'name': 'test2'}),
    ]

    assert list(router.names_mapping) == [
        ('test', '/test'),
        ('test2', '/test')
    ]

    with pytest.raises(NameError) as exc:
        router.add('/test2', name='test2')
    assert str(exc.value) == "Route 'test2' already exists for path '/test'."


def test_basic_add_operation():
    router1 = NamedRoutes()
    router2 = NamedRoutes()

    router1.add('/test', name='test')
    router2.add('/test2')
    router3 = router1 + router2
    assert list(router3) == [
        RouteDefinition(path='/test', payload={'name': 'test'}),
        RouteDefinition(path='/test2', payload={}),
    ]
    assert list(router3.names_mapping) == [
        ('test', '/test'),
    ]


def test_conflict_add_operation():
    router1 = NamedRoutes()
    router2 = NamedRoutes()

    router1.add('/test', name='test')
    router2.add('/test2', name='test')

    with pytest.raises(NameError) as exc:
        router1 + router2
    assert str(exc.value) == "Route 'test' already exists for path '/test'."

def test_merge_add_operation():
    router1 = NamedRoutes()
    router2 = NamedRoutes()

    router1.add('/test', name='test')
    router2.add('/test', name='test2')
    router3 = router1 + router2

    assert list(router3.names_mapping) == [
        ('test', '/test'),
        ('test2', '/test'),
    ]


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
            'GET': obj_get,
            'POST': obj_post,
            'name': 'post_obj',
            'extras': {}
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
                'name': 'my_view',
                'GET': hamcrest.has_property(
                    '__func__', hamcrest.is_(View.GET)),
                'POST': hamcrest.has_property(
                '__func__', hamcrest.is_(View.POST)),
            })
        }),
        hamcrest.has_properties({
            'path': '/object_view/{oid}',
            'payload': hamcrest.has_entries({
                'name': 'object_view',
                'GET': hamcrest.has_property(
                    '__func__', hamcrest.is_(View.GET)),
                'POST': hamcrest.has_property(
                    '__func__', hamcrest.is_(View.POST)),
            })
        })
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

    @router2.register('/item/{id}')
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
    ]

    hamcrest.assert_that(list(router3), hamcrest.contains_exactly(
        hamcrest.has_properties({
            'path': '/item/{id}',
            'payload': hamcrest.has_entries({
                'name': 'item',
                'GET': hamcrest.has_property(
                    '__func__', hamcrest.is_(Browser.GET)),
                'POST': hamcrest.has_property(
                '__func__', hamcrest.is_(Browser.POST)),
                'PUT': hamcrest.has_property(
                    '__func__', hamcrest.is_(REST.PUT)),
                'PATCH': hamcrest.has_property(
                '__func__', hamcrest.is_(REST.PATCH)),
                'DELETE': hamcrest.has_property(
                    '__func__', hamcrest.is_(REST.DELETE)),
            })
        })
    ))
