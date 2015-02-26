#! ../env/bin/python
import os

from flask import Flask
from webassets.loaders import PythonLoader as PythonAssetsLoader

from memex import assets
from memex.models import db

from memex.extensions import (
    cache,
    assets_env,
    debug_toolbar,
    login_manager
)


class ReverseProxied(object):
    '''Wrap the application in this middleware and configure the 
    front-end server to add these headers, to let you quietly bind 
    this to a URL other than / and to an HTTP scheme that is 
    different than what is used locally.

    In nginx:
    location /myprefix {
        proxy_pass http://192.168.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Script-Name /myprefix;
        }

    :param app: the WSGI application
    '''
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)


def create_app(object_name, env="prod"):
    """
    An flask application factory, as explained here:
    http://flask.pocoo.org/docs/patterns/appfactories/

    Arguments:
        object_name: the python path of the config object,
                     e.g. memex.settings.ProdConfig

        env: The name of the current environment, e.g. prod or dev
    """

    app = Flask(__name__)

    app.wsgi_app = ReverseProxied(app.wsgi_app)

    app.config.from_object(object_name)
    app.config['ENV'] = env

    #init the cache
    cache.init_app(app)

    debug_toolbar.init_app(app)

    #init SQLAlchemy
    db.init_app(app)

    login_manager.init_app(app)

    # Import and register the different asset bundles
    assets_env.init_app(app)
    assets_loader = PythonAssetsLoader(assets)
    for name, bundle in assets_loader.load_bundles().iteritems():
        assets_env.register(name, bundle)

    # register our blueprints
    from controllers.main import main
    app.register_blueprint(main)

    return app

if __name__ == '__main__':
    # Import the config for the proper environment using the
    # shell var MEMEX_ENV
    env = os.environ.get('MEMEX_ENV', 'prod')
    app = create_app('memex.settings.%sConfig' % env.capitalize(), env=env)

    app.run()
