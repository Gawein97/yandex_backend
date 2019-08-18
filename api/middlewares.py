from aiohttp import web

from .models import check_import, check_citizen, check_relatives
from .schemas import CitizenSchema


@web.middleware
async def import_exist(request, handler):
    """Проверяет существование импорта"""
    import_id = request.match_info.get('import_id')

    async with request.app['db'].acquire() as conn:
        is_import_exist = await check_import(conn, import_id)

        if not is_import_exist:
            return web.json_response("Import does not exist", status=404)

    resp = await handler(request)
    return resp


@web.middleware
async def update_citizen_validation(request, handler):
    """Дополнительная валидация для пользователя"""
    data = await request.json()
    appropriate_fields = {'town', 'street', 'building', 'apartment', 'building', 'name', 'birth_date',
                          'gender', 'relatives'}
    data_fields = {key for key in data.keys()}
    other_fields = data_fields - appropriate_fields

    if len(other_fields) > 0 or len(data_fields) == 0:
        return web.json_response("Other fields aren't supported", status=400)

    schema = CitizenSchema(partial=True)
    citizen = schema.validate(data)

    if citizen:
        return web.json_response(citizen, status=400)

    updating_relatives = set()

    if 'relatives' in data:
        updating_relatives.update(data['relatives'])
        del data['relatives']

    request['citizen'] = data
    request['relatives'] = updating_relatives
    resp = await handler(request)

    return resp


@web.middleware
async def validate_citizen(request, handler):
    """Проверяет существование импорта, пользователя и родственников"""
    import_id = int(request.match_info.get('import_id'))
    citizen_id = int(request.match_info.get('citizen_id'))
    relatives = request['relatives']

    async with request.app['db'].acquire() as conn:
        is_exist_citizen = await check_citizen(conn, import_id, citizen_id)

        if not is_exist_citizen:
            return web.json_response("Citizen does not exist", status=404)

        if relatives:
            is_correct_relatives = await check_relatives(conn, import_id, relatives)

            if not is_correct_relatives or citizen_id in relatives:
                return web.json_response("Invalid relatives", status=400)

    resp = await handler(request)

    return resp
