from aiohttp import web
from aiohttp_apispec import validation_middleware, setup_aiohttp_apispec

from api.models import init_pg, close_pg
from api.routes import setup_routes
from api.schemas import my_error_handler
from api.settings import get_config


async def hello_world(request):
    return web.Response(text="Привет мир")


async def init_app(argv=None):
    app = web.Application()
    app.add_routes([web.get('/', hello_world)])
    app['config'] = get_config(argv)
    setup_aiohttp_apispec(app=app, error_callback=my_error_handler)
    app.middlewares.append(validation_middleware)
    app.on_startup.append(init_pg)
    app.on_cleanup.append(close_pg)
    setup_routes(app)
    return app
