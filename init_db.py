from sqlalchemy import create_engine, MetaData

from api.models import imports, relatives, citizens
from api.settings import BASE_DIR, get_config

DSN = "postgresql://{user}:{password}@{host}:{port}/{database}"

ADMIN__CONFIG_PATH = BASE_DIR / 'config' / 'api_admin.yaml'
ADMIN_CONFIG = get_config(['-c', ADMIN__CONFIG_PATH.as_posix()])
ADMIN_DB_URL = DSN.format(**ADMIN_CONFIG['postgres'])
admin_engine = create_engine(ADMIN_DB_URL, isolation_level='AUTOCOMMIT')

USER_CONFIG_PATH = BASE_DIR / 'config' / 'api.yaml'
USER_CONFIG = get_config(['-c', USER_CONFIG_PATH.as_posix()])
USER_DB_URL = DSN.format(**USER_CONFIG['postgres'])
user_engine = create_engine(USER_DB_URL)

TEST_CONFIG_PATH = BASE_DIR / 'config' / 'api_test.yaml'
TEST_CONFIG = get_config(['-c', TEST_CONFIG_PATH.as_posix()])
TEST_DB_URL = DSN.format(**TEST_CONFIG['postgres'])
test_engine = create_engine(TEST_DB_URL)


def setup_db(config):
    db_name = config['database']
    db_user = config['user']
    db_pass = config['password']

    conn = admin_engine.connect()
    conn.execute("DROP DATABASE IF EXISTS %s" % db_name)
    conn.execute("DROP ROLE IF EXISTS %s" % db_user)
    conn.execute("CREATE USER %s WITH PASSWORD '%s'" % (db_user, db_pass))
    conn.execute("CREATE DATABASE %s ENCODING 'UTF8'" % db_name)
    conn.execute("GRANT ALL PRIVILEGES ON DATABASE %s TO %s" %
                 (db_name, db_user))
    conn.close()


def teardown_db(config):
    db_name = config['database']
    db_user = config['user']

    conn = admin_engine.connect()
    conn.execute("""
      SELECT pg_terminate_backend(pg_stat_activity.pid)
      FROM pg_stat_activity
      WHERE pg_stat_activity.datname = '%s'
        AND pid <> pg_backend_pid();""" % db_name)
    conn.execute("DROP DATABASE IF EXISTS %s" % db_name)
    conn.execute("DROP ROLE IF EXISTS %s" % db_user)
    conn.close()


def create_tables(engine=test_engine):
    meta = MetaData()
    meta.create_all(bind=engine, tables=[imports, relatives, citizens])


def drop_tables(engine=test_engine):
    meta = MetaData()
    meta.drop_all(bind=engine, tables=[imports, relatives, citizens])


def sample_data(engine=test_engine):
    conn = engine.connect()
    conn.execute(imports.insert())
    conn.execute(citizens.insert(), [
        {
            "citizen_id": 1,
            "town": "Москва",
            "street": "Улица строителей",
            "building": "Дом 5",
            "apartment": 15,
            "name": "Вера Иванова",
            "birth_date": "5.01.2000",
            "gender": "female",
            "import_id": 1,
        }, {
            "citizen_id": 2,
            "town": "Москва",
            "street": "Улица Моцарта",
            "building": "дом 46",
            "apartment": 11,
            "name": "Надежда Иванова",
            "birth_date": "01.02.2000",
            "gender": "female",
            "import_id": 1,
        }, {
            "citizen_id": 3,
            "town": "Москва",
            "street": "Ленина",
            "building": "д.15/43",
            "apartment": 6,
            "name": "Любовь Степанова",
            "birth_date": "01.03.2000",
            "gender": "female",
            "import_id": 1,
        }, {
            "citizen_id": 4,
            "town": "Москва",
            "street": "Гончарова",
            "building": "16k7стр5",
            "apartment": 11,
            "name": "София Иванова",
            "birth_date": "01.04.2000",
            "gender": "female",
            "import_id": 1,
        }
    ])
    conn.execute(relatives.insert(), [
        {'citizen_id': 1, 'relative_id': 2},
        {'citizen_id': 1, 'relative_id': 3},
        {'citizen_id': 3, 'relative_id': 1},
        {'citizen_id': 2, 'relative_id': 1},
        {'citizen_id': 2, 'relative_id': 4},
        {'citizen_id': 4, 'relative_id': 2},
    ])
    conn.close()


if __name__ == '__main__':
    setup_db(USER_CONFIG['postgres'])
    create_tables(engine=user_engine)
    # drop_tables()
    # teardown_db(config)
