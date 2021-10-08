roughrider.routing
******************

Routing capabilities for ``horseman`` nodes.

This package introduces a 'Routes' component that allows registration of
endpoints on one or several HTTP Methods. Routes can be looked up by URL
or by name.


Example
=======

Below is an example of a barebone API, handling a GET request on '/'
and returning a JSON response.

.. code-block:: python

  import logging
  from bjoern import run
  from horseman.meta import SentryNode, Overhead, APIView
  from horseman.response import Response
  from roughrider.routing import Routes


  class Request(Overhead):

      data = None

      def __init__(self, environ):
          self.environ = environ

      def extract(self):
          self.data = 'somedata'


  class RootNode(SentryNode):

      def __init__(self):
          self.routes = Routes()

      def resolve(self, path: str, environ: dict):
          route = self.routes.match_method(path, environ['REQUEST_METHOD'])
          if route is not None:
              request = Request(environ)
              return route.endpoint(request, **route.params)

      def handle_exception(self, exc_info, environ):
          logging.error(exc_info)


  app = RootNode()

  @app.routes.register('/')
  class View(APIView):

      def GET(self, overhead):
          return Response.to_json(200, {"Result": "OK"})

  run(
      host="0.0.0.0",
      port=8080,
      reuse_port=True,
      wsgi_app=app,
  )
