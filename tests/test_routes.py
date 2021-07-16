from roughrider.routing.route import Routes, RouteDefinition, RouteEndpoint


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
            'GET': RouteEndpoint(
                method='GET',
                endpoint=my_get
            )
        })
    ]

    assert list(router2) == [
        RouteDefinition(path='/test', payload={
            'POST': RouteEndpoint(
                method='POST',
                endpoint=my_post
            )
        })
    ]

    router3 = router1 + router2
    assert list(router3) == [
        RouteDefinition(path='/test', payload={
            'GET': RouteEndpoint(
                method='GET',
                endpoint=my_get
            ),
            'POST': RouteEndpoint(
                method='POST',
                endpoint=my_post
            )
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
            path='/test',
            payload={
                'GET': RouteEndpoint(
                    method='GET',
                    endpoint=my_get
                )
            }
        )
    ]

    assert list(router2) == [
        RouteDefinition(
            path='/test',
            payload={
                'GET': RouteEndpoint(
                    method='GET',
                    endpoint=my_other_get
                )
            }
        )
    ]

    router3 = router1 + router2
    assert list(router3) == [
        RouteDefinition(
            path='/test',
            payload={
                'GET': RouteEndpoint(
                    method='GET',
                    endpoint=my_other_get
                )
            }
        )
    ]

    router3 = router2 + router1
    assert list(router3) == [
        RouteDefinition(
            path='/test',
            payload={
                'GET': RouteEndpoint(
                    method='GET',
                    endpoint=my_get
                )
            }
        )
    ]
