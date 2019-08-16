from aiohttp import web
from aiohttp_apispec import request_schema
from marshmallow import RAISE

from .models import insert_import, update_citizen_data, check_relatives, check_citizen
from .schemas import ImportsSchema, CitizenSchema


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


@request_schema(CitizenSchema(partial=True, unknown=RAISE))
async def update_citizen(request):
    schema = CitizenSchema()
    import_id = int(request.match_info.get('import_id'))
    citizen_id = int(request.match_info.get('citizen_id'))
    citizen = request['data']
    updating_relatives = set()

    del citizen['citizen_id']
    del citizen['import_id']

    async with request.app['db'].acquire() as conn:
        # TODO: Вынести в модельку проверку
        is_exist_citizen = await check_citizen(conn, import_id, citizen_id)
        if not is_exist_citizen:
            return web.json_response("Citizen Does not exist", status=400)

        if 'relatives' in citizen:
            updating_relatives.update(citizen['relatives'])
            del citizen['relatives']

            is_correct_relatives = await check_relatives(conn, import_id, updating_relatives)

            if not is_correct_relatives:
                return web.json_response("Incorect relatives", status=400)

        updated_citizen = await update_citizen_data(conn, import_id, citizen_id, citizen, updating_relatives)

    if not updated_citizen:
        return web.json_response("Error in updating", status=400)

    return web.json_response(schema.dump(updated_citizen), status=200)
