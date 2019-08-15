async def test_results(cli):
    response = await cli.get('/')
    assert response.status == 200
    assert 'Привет Мир' in await response.text()