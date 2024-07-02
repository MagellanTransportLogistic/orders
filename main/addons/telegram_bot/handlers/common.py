from aiogram import F, Router
from aiogram.filters import Command
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, ReplyKeyboardRemove

from ..services.database import get_admin_count

router_common = Router()

commands = [
    {"lvl": 0, "name": "/start", "description": "Список команд бота."},
    {"lvl": 0, "name": "/me", "description": "Получение информации об аккаунте, который вызвал данную команду."},

    {"lvl": 1, "name": "/send_doc", "description": "Отправка скан-копии документа боту."},

    {"lvl": 2, "name": "/register", "description": "Регистрация нового сотрудника в боте."},
    {"lvl": 2, "name": "/change_user", "description": "Изменение прав сотрудника в боте."},
    {"lvl": 2, "name": "/delete_user", "description": "Отключение сотрудника от бота."},
]


@router_common.message(Command(commands=["start", "help", "h"]))
async def cmd_start(message: Message, state: FSMContext, **kwargs):
    await state.clear()
    role_id = kwargs.get("role_id")
    msg = 'Список доступных команд: ' + chr(10)
    for cmd in commands:
        if cmd["lvl"] <= role_id:
            msg = msg + f'{cmd["name"]} - {cmd["description"]}' + chr(10)

    if await get_admin_count() == 0:
        msg = msg + chr(10) + ('<i>Работа пользователей и ролей включится автоматически, '
                               'как только появится первый администратор.</i>')

    await message.answer(
        text=msg,
        reply_markup=ReplyKeyboardRemove(),
        parse_mode='HTML'
    )


@router_common.message(Command(commands=["me"]))
async def cmd_start(message: Message, state: FSMContext, **kwargs):
    await state.clear()
    role_id = kwargs.get("role_id")
    user_name = f'{message.from_user.first_name} {message.from_user.last_name}'
    user_id = message.from_user.id
    msg = (f'Пользователь: {user_name}{chr(10)}'
           f'Идентификатор: {user_id}{chr(10)}'
           f'Статус: {"Зарегистрирован" if role_id > 0 else "Не зарегистрирован"}')
    if role_id > 0:
        msg = msg + chr(10) + f'Уровень доступа: {role_id}'
    else:
        msg = msg + chr(10) + chr(10) + ('<i>Для регистрации в системе '
                                         'данное сообщение нужно переслать администратору бота.</i>')

    if await get_admin_count() == 0:
        msg = msg + chr(10) + chr(10) + ('<i>Сейчас бот работает в режиме полного доступа для всех. '
                                         'Работа пользователей и ролей включится автоматически, '
                                         'как только появится первый администратор.</i>')

    await message.answer(
        text=msg,
        reply_markup=ReplyKeyboardRemove(),
        parse_mode='HTML'
    )


# Обработка отмен по кнопке "Отменить"
@router_common.message(StateFilter(None), Command(commands=["cancel"]))
@router_common.message(default_state, F.text.lower() == "отмена")
async def cmd_cancel_no_state(message: Message, state: FSMContext):
    # Стейт сбрасывать не нужно, удалим только данные
    await state.set_data({})
    await message.answer(
        text="Нечего отменять",
        reply_markup=ReplyKeyboardRemove()
    )


@router_common.message(Command(commands=["cancel"]))
@router_common.message(F.text.lower() == "отмена")
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Действие отменено",
        reply_markup=ReplyKeyboardRemove()
    )
