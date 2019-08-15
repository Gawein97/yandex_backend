import json

mock_data = {
    "citizens": [{
        "citizen_id": 1,
        "town": "Москва",
        "street": "Улица строителей",
        "building": "Дом 5",
        "apartment": 15,
        "name": "Вера Иванова",
        "birth_date": "5.01.2000",
        "gender": "female",
        "relatives": [2, 3]
    }, {
        "citizen_id": 2,
        "town": "Москва",
        "street": "Улица Моцарта",
        "building": "дом 46",
        "apartment": 11,
        "name": "Надежда Иванова",
        "birth_date": "01.02.2000",
        "gender": "female",
        "relatives": [1, 4]
    }, {
        "citizen_id": 3,
        "town": "Москва",
        "street": "Ленина",
        "building": "д.15/43",
        "apartment": 6,
        "name": "Любовь Степанова",
        "birth_date": "01.03.2000",
        "gender": "female",
        "relatives": [1]
    }, {
        "citizen_id": 4,
        "town": "Москва",
        "street": "Гончарова",
        "building": "16k7стр5",
        "apartment": 11,
        "name": "София Иванова",
        "birth_date": "01.04.2000",
        "gender": "female",
        "relatives": [2]
    }]
}
mock_headers = {"Content-Type": "application/json"}


async def test_correct_import(cli, tables_and_data):
    """Тестируем вставку данных в таблицу"""
    post_data = mock_data.copy()
    response = await cli.post('/imports', data=json.dumps(post_data), headers=mock_headers)

    assert response.status == 200
    assert 'Привет мир' in await response.text()


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


async def test_unknown_field_in_citizen(cli, tables_and_data):
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
