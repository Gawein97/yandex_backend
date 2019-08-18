import json

from . import mock_data, mock_headers, mock_update


async def test_correct_import(cli, tables_and_data):
    """Тестируем вставку данных в таблицу"""
    post_data = mock_data.copy()
    response = await cli.post('/imports', data=json.dumps(post_data), headers=mock_headers)

    assert response.status == 201


async def test_import_validate(cli, tables_and_data, param_test_insert_and_update):
    """Тестируем вставку неправильных данны"""
    post_data = mock_data.copy()

    for value in param_test_insert_and_update[1]:
        post_data['citizens'][0][param_test_insert_and_update[0]] = value
        response = await cli.post('/imports', data=json.dumps(post_data), headers=mock_headers)

        assert response.status == 400


async def test_unknown_field(cli, tables_and_data):
    """Добавляем несуществующее поле"""
    post_data = mock_data.copy()
    post_data['aliens'] = "All your base are belong to us"

    response = await cli.post('/imports', data=json.dumps(post_data), headers=mock_headers)

    assert response.status == 400


async def test_invalid_date(cli, tables_and_data):
    """Пытаемся вставить дату в неправильном формате"""
    post_data = mock_data.copy()
    post_data['citizens'][0]['birth_date'] = '31.22.2015'

    response = await cli.post('/imports', data=json.dumps(post_data), headers=mock_headers)

    assert response.status == 400


async def test_correct_update(cli, tables_and_data):
    """Тестируем вставку данных в таблицу"""
    post_data = mock_update.copy()
    response = await cli.patch('/imports/1/citizens/1', data=json.dumps(post_data), headers=mock_headers)

    assert response.status == 200


async def test_update_validate(cli, tables_and_data, param_test_insert_and_update):
    """Тестируем вставку неправильных данны в обновлении"""
    post_data = mock_update.copy()

    for value in param_test_insert_and_update[1]:
        post_data[param_test_insert_and_update[0]] = value
        response = await cli.post('/imports', data=json.dumps(post_data), headers=mock_headers)

        assert response.status == 400


async def test_add_fake_import(cli, tables_and_data):
    """Добавляем Пытаемся обновить фейковый импорт"""
    post_data = mock_update.copy()
    response = await cli.patch('/imports/5000/citizens/1', data=json.dumps(post_data), headers=mock_headers)

    assert response.status == 404


async def test_add_fake_citizen(cli, tables_and_data):
    """Добавляем Пытаемся обновить фейкового пользователя"""
    post_data = mock_update.copy()
    response = await cli.patch('/imports/1/citizens/5000', data=json.dumps(post_data), headers=mock_headers)

    assert response.status == 404


async def test_add_fake_citizen_and_import(cli, tables_and_data):
    """Добавляем Пытаемся обновить фейкового пользователя и импорт"""
    post_data = mock_update.copy()
    response = await cli.patch('/imports/5000/citizens/5000', data=json.dumps(post_data), headers=mock_headers)

    assert response.status == 404


async def test_get_fake_import(cli, tables_and_data):
    """Пытаемся обратиться к несущетвующему импорту"""
    response = await cli.get('/imports/5000/citizens')

    assert response.status == 404

async def test_get_fake_birthdays(cli, tables_and_data):
    """Пытаемся обратиться к несущетвующему импорту"""
    response = await cli.get('/imports/166/citizens/birthdays')

    assert response.status == 404

async def test_get_fake_percentiles(cli, tables_and_data):
    """Пытаемся обратиться к несущетвующему импорту"""
    response = await cli.get('/imports/166/towns/stat/percentile/age')

    assert response.status == 404
