from aiogram import Router, F
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove

from main.addons.telegram_bot.keyboards.simple_row import make_row_keyboard
from main.addons.telegram_bot.services.database import add_user_to_db, change_user_role

router_change_user = Router()

change_menu_buttons = ["Отмена"]
change_access_buttons = ["1", "2", "Отмена"]


class ChangeUser(StatesGroup):
    user_id = State()
    user_level = State()


@router_change_user.message(StateFilter(None), Command("change_user"))
async def cmd_change(message: Message, state: FSMContext, role_id: int):
    if role_id == 2:
        await message.answer(
            text="Введите TelegramID пользователя, которого нужно редактировать:",
            reply_markup=make_row_keyboard(change_menu_buttons)
        )
        await state.set_state(ChangeUser.user_id)
    else:
        await state.clear()


@router_change_user.message(
    StateFilter("ChangeUser:user_id")
)
async def recieved_user_id(message: Message, state: FSMContext):
    await state.update_data(user_id=message.text.lower())
    await message.answer(
        text="Выберите новый уровень доступа сотрудника (1 - Обычный, 2 - Администратор):",
        reply_markup=make_row_keyboard(change_access_buttons)
    )
    await state.set_state(ChangeUser.user_level)


@router_change_user.message(ChangeUser.user_level, F.text.in_(change_access_buttons))
async def received_user_id(message: Message, state: FSMContext):
    await state.update_data(user_level=message.text)
    user_data = await state.get_data()

    result = await change_user_role(user_data['user_id'], user_data['user_level'])

    if result:
        await message.answer(
            text="Доступ пользователя успешно обновлен.",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await message.answer(
            text="Ошибка обновления доступа пользователя!",
            reply_markup=ReplyKeyboardRemove()
        )
    await state.clear()


@router_change_user.message(
    StateFilter("ChangeUser:user_level")
)
async def received_user_id(message: Message, state: FSMContext):
    await state.update_data(user_name=message.text)
    await message.answer(
        text="Указан некорректный уровень. Допустимые уровни: 1 = Пользователь, 2 = Администратор",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()
