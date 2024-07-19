import json
import logging
import time

import sqlalchemy as db
from sqlalchemy import text

metadata = db.MetaData()

bot_users = db.Table('bot_users', metadata,
                     db.Column('user_id', db.BIGINT, primary_key=True, autoincrement=False, nullable=False,
                               unique=True),
                     db.Column('login', db.VARCHAR(256)),
                     db.Column('name', db.VARCHAR(256)),
                     db.Column('snils', db.VARCHAR(32), nullable=False, unique=True),
                     db.Column('role_id', db.Integer, nullable=False, default=1))

bot_group_messages = db.Table('bot_group_messages', metadata,
                              db.Column('group_id', db.BIGINT, autoincrement=False, nullable=False, ),
                              db.Column('message_text', db.NVARCHAR(), nullable=False, ),
                              db.Column('uuid', db.Uuid, primary_key=True, nullable=False,
                                        server_default=text('newid()')), )


def sql_start(_database="demo", _server='localhost', _login='admin', _passwd='pass', options='{}'):
    global engine
    _options = json.loads(options)
    _str_options = f'?driver={str(_options["driver"]).replace(" ", "+")}'
    for k in _options:
        if k != 'driver':
            _str_options += f'&{k}={_options[k]}'
    database_url = f'mssql+pyodbc://{_login}:{_passwd}@{_server}/{_database}{_str_options}'

    i = 10000
    while i > 0:
        engine = db.create_engine(database_url)
        try:
            engine.connect()
            logging.log(msg='Database connected.', level=logging.INFO)
            break
        except Exception as Err:
            logging.log(msg=str(Err), level=logging.ERROR)
        time.sleep(10)
        i -= 1
    metadata.create_all(engine)


async def add_user_to_db(user_id, name, snils):
    try:
        q = db.insert(bot_users).values(user_id=user_id, login=name, name=name, snils=snils, role_id=1)
        with engine.connect() as connection:
            connection.execute(q)
            connection.commit()
        return True
    except Exception as E:
        logging.log(msg=str(f'add_user_to_db: {E}'), level=logging.ERROR)
        return False


async def delete_user_from_db(user_id):
    try:
        q = db.delete(bot_users).where(bot_users.c.user_id == user_id)
        with engine.connect() as connection:
            connection.execute(q)
            connection.commit()
        return True
    except Exception as E:
        logging.log(msg=str(f'delete_user_from_db: {E}'), level=logging.ERROR)
        return False


async def get_user_role(user_id):
    try:
        q = db.select(bot_users.c.role_id).where(bot_users.c.user_id == user_id)
        with engine.connect() as connection:
            data = connection.execute(q).fetchall()
        return data[0][0] if len(data) > 0 else 0
    except Exception as E:
        logging.log(msg=str(f'get_user_role: {E}'), level=logging.ERROR)
        return 0


async def get_user_path(user_id):
    try:
        q = db.select(bot_users.c.name, bot_users.c.snils).where(bot_users.c.user_id == user_id)
        with engine.connect() as connection:
            data = connection.execute(q).fetchall()
        return f'{data[0][0]} [{data[0][1]}]' if len(data) > 0 else 0
    except Exception as E:
        logging.log(msg=str(f'get_user_path: {E}'), level=logging.ERROR)
        return 'unknown'


async def change_user_role(user_id, new_role_id):
    try:
        q = db.update(bot_users).where(bot_users.c.user_id == user_id).values(role_id=new_role_id)
        with engine.connect() as connection:
            connection.execute(q)
            connection.commit()
        return True
    except Exception as E:
        logging.log(msg=str(f'change_user_role: {E}'), level=logging.ERROR)
        return False


async def get_admin_count():
    try:
        q = db.select(bot_users).where(bot_users.c.role_id == 2)
        with engine.connect() as connection:
            return len(connection.execute(q).fetchall())
    except Exception as E:
        logging.log(msg=str(f'get_admin_count: {E}'), level=logging.ERROR)
        return -1


def get_group_messages():
    try:
        q = db.select(bot_group_messages)
        with engine.connect() as connection:
            return connection.execute(q).fetchall()
    except Exception as E:
        logging.log(msg=str(f'get_group_messages: {E}'), level=logging.ERROR)
        return {}


def erase_group_message(message_uuid):
    try:
        q = db.delete(bot_group_messages).where(bot_group_messages.c.uuid == message_uuid)
        with engine.connect() as connection:
            connection.execute(q)
            connection.commit()
    except Exception as E:
        logging.log(msg=str(f'get_group_message: {E}'), level=logging.ERROR)
        return -1
