from aiohttp import web


async def hello_world(request):
    return web.Response(text="Привет Мир")


async def init_app():
    app = web.Application()
    app.add_routes([web.get('/', hello_world)])
    return app
