from roughrider.routing.route import Routes, RouteDefinition


def test_iterable():
    router1 = Routes()
    assert list(router1) == []

    router1.add('/test')
    assert list(router1) == [
        RouteDefinition(
            path='/test', payload={})
    ]

    router1.add('/test2/{me}')
    assert list(router1) == [
        RouteDefinition(
            path='/test', payload={}),
        RouteDefinition(
            path='/test2/{me}', payload={}),
    ]

    router1.add('/foo', foo='bar')
    assert router1.match('/foo') == ({'foo': 'bar'}, {})
    assert list(router1) == [
        RouteDefinition(
            path='/test', payload={}),
        RouteDefinition(
            path='/test2/{me}', payload={}),
        RouteDefinition(
            path='/foo', payload={'foo': 'bar'}),
    ]

    router1.add('/foo', qux='test')
    assert router1.match('/foo') == ({'foo': 'bar', 'qux': 'test'}, {})
    assert list(router1) == [
        RouteDefinition(
            path='/test', payload={}),
        RouteDefinition(
            path='/test2/{me}', payload={}),
        RouteDefinition(
            path='/foo', payload={'foo': 'bar', 'qux': 'test'}),
    ]


def test_basic_add_operation():
    router1 = Routes()
    router2 = Routes()

    router1.add('/test')
    router2.add('/test2')
    router3 = router1 + router2
    assert list(router3) == [
        RouteDefinition(path='/test', payload={}),
        RouteDefinition(path='/test2', payload={}),
    ]


def test_override_add_operation():
    router1 = Routes()
    router2 = Routes()

    router1.add('/test')
    router1.add('/test2', test=1)
    router2.add('/test2', test=2)
    router3 = router1 + router2
    assert list(router3) == [
        RouteDefinition(path='/test', payload={}),
        RouteDefinition(path='/test2', payload={'test': 2}),
    ]

    router3 = router2 + router1
    assert list(router3) == [
        RouteDefinition(path='/test', payload={}),
        RouteDefinition(path='/test2', payload={'test': 1}),
    ]


def test_merge_add_operation():
    router1 = Routes()
    router2 = Routes()

    router1.add('/test')
    router1.add('/test2', test=1)
    router2.add('/test2', foo='bar')
    router3 = router1 + router2
    assert list(router3) == [
        RouteDefinition(
            path='/test', payload={}
        ),
        RouteDefinition(path='/test2', payload={
            'test': 1, 'foo': 'bar'
        }),
    ]

    assert list(router1 + router2) == list(router2 + router1)


def test_merge_method_registration_operation():
    router1 = Routes()
    router2 = Routes()

    @router1.register('/test')
    def my_get(request):
        pass

    @router2.register('/test', methods=['POST'])
    def my_post(request):
        pass

    assert list(router1) == [
        RouteDefinition(path='/test', payload={
            'GET': my_get, 'extras': {}
        })
    ]

    assert list(router2) == [
        RouteDefinition(path='/test', payload={
            'POST': my_post, 'extras': {},
        })
    ]

    router3 = router1 + router2
    assert list(router3) == [
        RouteDefinition(path='/test', payload={
            'GET': my_get, 'POST': my_post, 'extras': {}
        })
    ]


def test_override_method_registration_operation():
    router1 = Routes()
    router2 = Routes()

    @router1.register('/test')
    def my_get(request):
        pass

    @router2.register('/test', methods=['GET'])
    def my_other_get(request):
        pass

    assert list(router1) == [
        RouteDefinition(
            path='/test', payload={'GET': my_get, 'extras': {}})
    ]

    assert list(router2) == [
        RouteDefinition(
            path='/test', payload={'GET': my_other_get, 'extras': {}})
    ]

    router3 = router1 + router2
    assert list(router3) == [
        RouteDefinition(
            path='/test', payload={'GET': my_other_get, 'extras': {}})
    ]

    router3 = router2 + router1
    assert list(router3) == [
        RouteDefinition(
            path='/test', payload={'GET': my_get, 'extras': {}})
    ]
