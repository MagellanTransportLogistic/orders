import sqlalchemy as db

metadata = db.MetaData()
bot_users = db.Table('bot_users', metadata,
                     db.Column('user_id', db.BIGINT, primary_key=True, autoincrement=False, nullable=False,
                               unique=True),
                     db.Column('login', db.VARCHAR(256)),
                     db.Column('name', db.VARCHAR(256)),
                     db.Column('snils', db.VARCHAR(32), nullable=False, unique=True),
                     db.Column('role_id', db.Integer, nullable=False, default=1))


def sql_start(_database="demo", _server='localhost', _login='admin', _passwd='pass'):
    global engine
    database_url = f'mssql+pyodbc://{_login}:{_passwd}@{_server}/{_database}?driver=ODBC+Driver+17+for+SQL+Server'
    engine = db.create_engine(database_url)
    metadata.create_all(engine)


async def add_user_to_db(user_id, name, snils):
    try:
        q = db.insert(bot_users).values(user_id=user_id, login=name, name=name, snils=snils, role_id=1)
        with engine.connect() as connection:
            connection.execute(q)
            connection.commit()
        return True
    except Exception as E:
        print(f'add_user_to_db: {E}')
        return False


async def delete_user_from_db(user_id):
    try:
        q = db.delete(bot_users).where(bot_users.c.user_id == user_id)
        with engine.connect() as connection:
            connection.execute(q)
            connection.commit()
        return True
    except Exception as E:
        print(f'delete_user_from_db: {E}')
        return False


async def get_user_role(user_id):
    try:
        q = db.select(bot_users.c.role_id).where(bot_users.c.user_id == user_id)
        with engine.connect() as connection:
            data = connection.execute(q).fetchall()
        return data[0][0] if len(data) > 0 else 0
    except Exception as E:
        print(f'get_user_role: {E}')
        return 0


async def get_user_path(user_id):
    try:
        q = db.select(bot_users.c.name, bot_users.c.snils).where(bot_users.c.user_id == user_id)
        with engine.connect() as connection:
            data = connection.execute(q).fetchall()
        return f'{data[0][0]} [{data[0][1]}]' if len(data) > 0 else 0
    except Exception as E:
        print(f'get_user_role: {E}')
        return 'unknown'


async def change_user_role(user_id, new_role_id):
    try:
        q = db.update(bot_users).where(bot_users.c.user_id == user_id).values(role_id=new_role_id)
        with engine.connect() as connection:
            connection.execute(q)
            connection.commit()
        return True
    except Exception as E:
        print(f'change_user_role: {E}')
        return False


async def get_admin_count():
    try:
        q = db.select(bot_users).where(bot_users.c.role_id == 2)
        with engine.connect() as connection:
            return len(connection.execute(q).fetchall())
    except Exception as E:
        print(f'get_user_role: {E}')
        return -1
