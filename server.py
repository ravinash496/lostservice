#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lostservice.web import create_app


if __name__ == '__main__':
    from werkzeug.serving import run_simple
    app = create_app()
    run_simple('0.0.0.0', 8080, app, threaded=True, use_debugger=False, use_reloader=False)
