from aiopg import sa
from sqlalchemy import (
    MetaData, Table, Column, ForeignKey,
    Integer, String, Date
)
from sqlalchemy.dialects.postgresql import insert

metadata = MetaData()

imports = Table('imports', metadata,
                Column('id', Integer, primary_key=True, autoincrement=True))

relatives = Table('relatives', metadata,
                  Column('id', Integer, primary_key=True, autoincrement=True),
                  Column('citizen_id', Integer, ForeignKey('citizens.id'), nullable=False),
                  Column('relative_id', Integer, ForeignKey('citizens.id'), nullable=False)
                  )

citizens = Table('citizens', metadata,
                 Column('id', Integer, primary_key=True, autoincrement=True),
                 Column('citizen_id', Integer, nullable=False),
                 Column('town', String(255), nullable=False),
                 Column('street', String(255), nullable=False),
                 Column('building', String(255), nullable=False),
                 Column('apartment', Integer, nullable=False),
                 Column('building', String(255), nullable=False),
                 Column('name', String(255), nullable=False),
                 Column('birth_date', Date, nullable=False),
                 Column('gender', String(6), nullable=False),
                 Column('import_id', Integer, ForeignKey('imports.id'), nullable=False),
                 )


async def init_pg(app):
    conf = app['config']['postgres']
    engine = await sa.create_engine(
        database=conf['database'],
        user=conf['user'],
        password=conf['password'],
        host=conf['host'],
        port=conf['port'],
        minsize=conf['minsize'],
        maxsize=conf['maxsize'],
    )
    app['db'] = engine


async def close_pg(app):
    app['db'].close()
    await app['db'].wait_closed()


async def insert_import(conn, new_citizens, new_relatives):
    """Вставка импорта"""
    import_id = None
    async with conn.begin():
        # Cначала вставляем запись в таблицу imports и получаем id
        result = await conn.execute(imports.insert().values().returning(imports.c.id))
        import_id = await result.scalar()

        for new_citizen in new_citizens:
            new_citizen['import_id'] = import_id

        # Всталяем всех горожан за один множественный инсерт
        result = await conn.execute(
            insert(citizens).returning(citizens.c.id, citizens.c.citizen_id).values(
                new_citizens).on_conflict_do_nothing())  # Фишка постгреса returning в insert

        inserted_citizens = await result.fetchall()
        citizen_mapper = {item[1]: item[0] for item in inserted_citizens}
        values = []
        for new_citizen in new_citizens:
            for relative in new_relatives[new_citizen['citizen_id']]:
                values.append({
                    'citizen_id': citizen_mapper[new_citizen['citizen_id']],
                    'relative_id': citizen_mapper[relative]})

        await conn.execute(insert(relatives).returning(relatives.c.id).values(values).on_conflict_do_nothing())
    return import_id
