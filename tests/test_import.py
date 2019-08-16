import json

from . import mock_data, mock_headers, mock_update


async def test_correct_import(cli, tables_and_data):
    """Тестируем вставку данных в таблицу"""
    post_data = mock_data.copy()
    response = await cli.post('/imports', data=json.dumps(post_data), headers=mock_headers)

    assert response.status == 201


async def test_circular_relative(cli, tables_and_data):
    """Добавляем жителю ссылку на самого себя"""
    post_data = mock_data.copy()
    post_data['citizens'][0]['relatives'].append(1)

    response = await cli.post('/imports', data=json.dumps(post_data), headers=mock_headers)

    assert response.status == 400


async def test_unknown_field(cli, tables_and_data):
    """Добавляем несуществующее поле"""
    post_data = mock_data.copy()
    post_data['aliens'] = "All your base are belong to us"

    response = await cli.post('/imports', data=json.dumps(post_data), headers=mock_headers)

    assert response.status == 400


async def test_unknown_field_in_citizen(cli):
    """Добавляем несуществующее поле в объект пользователя"""
    post_data = mock_data.copy()
    post_data['citizens'][0]['aliens'] = "All your base are belong to us"

    response = await cli.post('/imports', data=json.dumps(post_data), headers=mock_headers)

    assert response.status == 400


async def test_unreal_relative(cli, tables_and_data):
    """Добавляем жителю ссылку на не существующего пользователя"""
    post_data = mock_data.copy()
    post_data['citizens'][0]['relatives'].append(23)

    response = await cli.post('/imports', data=json.dumps(post_data), headers=mock_headers)

    assert response.status == 400


async def test_broken_relative(cli, tables_and_data):
    """Убираем у жителя свзять в одностороеннем порядке (1 ссылается на 2, но 2 не ссылаетя на 1)"""
    post_data = mock_data.copy()
    post_data['citizens'][0]['relatives'].remove(2)

    response = await cli.post('/imports', data=json.dumps(post_data), headers=mock_headers)

    assert response.status == 400


async def test_invalid_date(cli, tables_and_data):
    """Пытаемся вставить дату в неправильном формате"""
    post_data = mock_data.copy()
    post_data['citizens'][0]['birth_date'] = '31.22.2015'

    response = await cli.post('/imports', data=json.dumps(post_data), headers=mock_headers)

    assert response.status == 400


async def test_invalid_intagers(cli, tables_and_data):
    """Пытаемся вставить citizen_id и apartment меньше нуля"""
    fields = ["citizen_id", "apartment", ]
    values = [-1, None, 'test']
    for field in fields:
        for value in values:
            post_data = mock_data.copy()
            post_data['citizens'][0][field] = value
            response = await cli.post('/imports', data=json.dumps(post_data), headers=mock_headers)
            assert response.status == 400


async def test_invalid_text_fields(cli, tables_and_data):
    """Пытаемся вставить текстовые поля в неправильном формате"""
    fields = ["town", "street", "building"]
    values = ["", 1, None]
    for field in fields:
        for value in values:
            post_data = mock_data.copy()
            post_data['citizens'][0][field] = value
            response = await cli.post('/imports', data=json.dumps(post_data), headers=mock_headers)
            assert response.status == 400


async def test_invalid_gender(cli, tables_and_data):
    """У нас в приложении только 2 гендера"""
    post_data = mock_data.copy()
    post_data['citizens'][0]['gender'] = "Трансформер"

    response = await cli.post('/imports', data=json.dumps(post_data), headers=mock_headers)

    assert response.status == 400


async def test_correct_update(cli, tables_and_data):
    """Тестируем вставку данных в таблицу"""
    post_data = mock_update.copy()
    response = await cli.patch('/imports/1/citizens/1', data=json.dumps(post_data), headers=mock_headers)

    assert response.status == 200


async def test_add_unreal_relatives(cli, tables_and_data):
    """Добавляем поле relatives с ссылкой на не сущесвтующего пользователя"""
    post_data = mock_update.copy()
    post_data['relatives'] = [2, 500]
    response = await cli.patch('/imports/1/citizens/1', data=json.dumps(post_data), headers=mock_headers)

    assert response.status == 400


async def test_add_self_relatives(cli, tables_and_data):
    """Добавляем поле relatives с ссылкой на самого себя"""
    post_data = mock_update.copy()
    post_data['relatives'] = [1]
    response = await cli.patch('/imports/1/citizens/1', data=json.dumps(post_data), headers=mock_headers)

    assert response.status == 400

async def test_add_fake_import(cli, tables_and_data):
    """Добавляем Обновляем пользователя из несуществующего импорта"""
    post_data = mock_update.copy()
    post_data['relatives'] = [1]
    response = await cli.patch('/imports/5000/citizens/1', data=json.dumps(post_data), headers=mock_headers)

    assert response.status == 400


async def test_add_fake_citizen_id(cli, tables_and_data):
    """Добавляем Обновляем пользователя c не существующим citizen_id"""
    post_data = mock_update.copy()
    post_data['relatives'] = [1]
    response = await cli.patch('/imports/1/citizens/5000', data=json.dumps(post_data), headers=mock_headers)

    assert response.status == 400