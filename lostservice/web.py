#!/usr/bin/env python
# -*- coding: utf-8 -*-


from werkzeug.wrappers import Request, Response
from lostservice.app import LostApplication, WebRequestContext


class LostService(object):
    """
    The lost web service container.
    """
    def __init__(self):
        self._lostapp = LostApplication()

    def dispatch_request(self, request):
        context = {}
        web_ctx = WebRequestContext()
        web_ctx.client_ip = request.access_route[0]
        context['web_ctx'] = web_ctx
        result = self._lostapp.execute_query(request.data, context)
        return result

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        result = self.dispatch_request(request)
        response = Response(result)
        response.headers['content-type'] = 'application/xml; charset=utf-8'

        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)


def create_app():
    """
    Create an instance of the lost web service.

    :return: :py:class:`lostservice.web.LostService`
    """
    app = LostService()
    return app

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    app = create_app()
    run_simple('127.0.0.1', 8080, app, use_debugger=True, use_reloader=True)
