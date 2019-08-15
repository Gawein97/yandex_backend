from aiohttp import web
from aiohttp_apispec import request_schema

from .schemas import ImportsSchema


@request_schema(ImportsSchema())
def add_import(request):
    return web.Response(text="Привет мир")
