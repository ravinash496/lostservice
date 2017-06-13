import os
from werkzeug.wrappers import Request, Response
from lostservice.app import LostApplication
import lostservice.context as context
import lostservice.logging.auditlog as auditlog


class LostService(object):
    """
    The lost web service container.
    """
    def __init__(self):
        self._lostapp = LostApplication()
        self._auditor = auditlog.getauditor()
        self._auditor.register_listener(None)

    def dispatch_request(self, request):
        result = self._lostapp.execute_query(request.data)
        return result

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        result = self.dispatch_request(request)
        response = Response(result)
        response.headers['content-type'] = 'text/xml; charset=utf-8'

        # self._auditor.record_event(None)
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

    custom_ini_file = os.path.join(os.path.dirname(__file__), './lostservice.ini')
    os.environ[context._CONFIGFILE] = custom_ini_file

    app = create_app()
    run_simple('127.0.0.1', 5150, app, use_debugger=True, use_reloader=True)
