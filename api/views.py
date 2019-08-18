from collections import Counter

import numpy as np
from aiohttp import web
from aiohttp_apispec import request_schema

from .models import insert_import, update_citizen_data, get_import, \
    get_citizens_birthdays, get_percentiles
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


async def update_citizen(request):
    """Обновляем горожанина"""
    schema = CitizenSchema()
    citizen = request['citizen']
    import_id = int(request.match_info.get('import_id'))
    citizen_id = int(request.match_info.get('citizen_id'))
    updating_relatives = set(request['relatives'])

    async with request.app['db'].acquire() as conn:
        updated_citizen = await update_citizen_data(conn, import_id, citizen_id, citizen, updating_relatives)

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


async def get_percentile(request):
    """Считаем перентили (Я на постгресе смог посчитать, нно там не совпадает с numpy)"""

    import_id = int(request.match_info.get('import_id'))
    out_data = {'data': []}

    async with request.app['db'].acquire() as conn:
        percentiles = await get_percentiles(conn, import_id)

    for item in percentiles:
        np_ages = np.array(item['birthdays'])
        out_data['data'].append({
            "town": item['town'],
            "p50": round(np.percentile(np_ages, 50, interpolation='linear'), 2),
            "p75": round(np.percentile(np_ages, 75, interpolation='linear'), 2),
            "p90": round(np.percentile(np_ages, 90, interpolation='linear'), 2)
        })

    return web.json_response(out_data, status=200)
