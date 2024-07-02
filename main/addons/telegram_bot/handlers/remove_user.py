from aiogram import Router
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove

from ..keyboards.simple_row import make_row_keyboard
from ..services.database import delete_user_from_db

router_remove_user = Router()

register_menu_buttons = ["Отмена"]


class RemoveUser(StatesGroup):
    user_id = State()


@router_remove_user.message(StateFilter(None), Command("delete_user"))
async def cmd_register(message: Message, state: FSMContext, role_id: int):
    if role_id == 2:
        await message.answer(
            text="Введите TelegramID пользователя, которого нужно отключить от системы:",
            reply_markup=make_row_keyboard(register_menu_buttons)
        )
        await state.set_state(RemoveUser.user_id)
    else:
        await state.clear()


@router_remove_user.message(
    StateFilter("RemoveUser:user_id")
)
async def recieved_user_id(message: Message, state: FSMContext):
    await state.update_data(user_id=message.text.lower())
    user_data = await state.get_data()

    result = await delete_user_from_db(user_data['user_id'])

    await message.answer(
        text="Пользователь успешно удален.",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()
