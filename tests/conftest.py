import pytest

from api.app import init_app
from api.settings import BASE_DIR, get_config
from init_db import (
    setup_db,
    teardown_db,
    create_tables,
    drop_tables,
    sample_data
)

TEST_CONFIG_PATH = BASE_DIR / 'config' / 'api_test.yaml'


@pytest.fixture
async def cli(loop, aiohttp_client, db):
    app = await init_app(['-c', TEST_CONFIG_PATH.as_posix()])
    return await aiohttp_client(app)


@pytest.fixture(scope='module')
def db():
    test_config = get_config(['-c', TEST_CONFIG_PATH.as_posix()])

    setup_db(test_config['postgres'])
    yield
    teardown_db(test_config['postgres'])


@pytest.fixture
def tables_and_data():
    create_tables()
    sample_data()
    yield
    drop_tables()


@pytest.fixture(params=[
    ("citizen_id", [-1, None, 'test']),
    ("apartment", [-1, None, 'test']),
    ("town", ["", 1, None]),
    ("street", ["", 1, None]),
    ('aliens', ["All your base are belong to us"]),
    ('birth_date', '31.22.2015'),
    ("building", ["", 1, None]),
    ("gender", ["Трансформер"]),
    ("relatives", [[2, 3, 1]],),
    ("relatives", [[3]]),
    ("relatives", [[2, 3, 500]]),
    ("relatives", [[]]),
])
async def param_test_insert_and_update(request):
    """Тестовый набор данных для вставки пользователей"""
    return request.param
