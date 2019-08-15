from aiohttp import web

from api.settings import get_config


async def hello_world(request):
    return web.Response(text="Привет мир")


async def init_app():
    app = web.Application()
    app.add_routes([web.get('/', hello_world)])
    app['config'] = get_config()
    return app
