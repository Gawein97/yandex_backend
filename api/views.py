from collections import Counter

from aiohttp import web
from aiohttp_apispec import request_schema

from .models import insert_import, update_citizen_data, check_relatives, check_citizen, get_import, \
    get_citizens_birthdays
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


@request_schema(CitizenSchema(partial=True, only=(
        'town', 'street', 'building', 'apartment', 'name', 'birth_date', 'gender', 'relatives')))
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
    output_data = {"data": schema.dump(updated_citizen)}
    return web.json_response(output_data, status=200)


async def get_citizens(request):
    """Выводим всех горожан из импорта"""
    schema = CitizenSchema(many=True)
    import_id = int(request.match_info.get('import_id'))

    async with request.app['db'].acquire() as conn:
        import_data = await get_import(conn, import_id)
    output_data = {"data": schema.dump(import_data)}

    return web.json_response(output_data, status=200)


async def get_birthdays(request):
    """Выводим дни рождения"""
    import_id = int(request.match_info.get('import_id'))
    out_data = {'data': {i: [] for i in range(1, 13)}}

    async with request.app['db'].acquire() as conn:
        birthdays = await get_citizens_birthdays(conn, import_id)
    for citizen in birthdays:
        presents = list(filter(None, citizen[1]))
        presents_counter = Counter(presents)
        for month, presents_count in presents_counter.items():
            out_data['data'][int(month)].append({'citizen_id': citizen[0], 'presents': presents_count})

    return web.json_response(out_data, status=200)
