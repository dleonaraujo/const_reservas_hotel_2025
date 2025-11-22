from app import app
from werkzeug.wsgi import DispatcherMiddleware
from werkzeug.serving import run_wsgi_app

def handler(request, response):
    # Convierte el request serverless en WSGI
    return run_wsgi_app(app, environ=request.environ, start_response=response)
