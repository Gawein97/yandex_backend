from aiohttp import web
from aiohttp_apispec import request_schema

from .models import insert_import
from .schemas import ImportsSchema


@request_schema(ImportsSchema())
async def add_import(request):
    relatives = {}
    citizens = request['data']['citizens']

    for citizen in citizens:
        relatives[citizen['citizen_id']] = citizen['relatives']
        del citizen['relatives']

    async with request.app['db'].acquire() as conn:
        import_id = await insert_import(conn, citizens, relatives)

        if import_id is None:
            return web.json_response("an errow was acquired", status=400)

        output_data = {"data": {"import_id": import_id}}
        return web.json_response(output_data, status=201)
