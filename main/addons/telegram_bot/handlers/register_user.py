from aiogram import Router
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove

from keyboards.simple_row import make_row_keyboard
from services.database import add_user_to_db

router_register_user = Router()

register_menu_buttons = ["Отмена"]


class RegisterUser(StatesGroup):
    user_id = State()
    user_name = State()
    user_snils = State()


@router_register_user.message(StateFilter(None), Command("register"))
async def cmd_register(message: Message, state: FSMContext, role_id: int):
    if role_id == 2:
        await message.answer(
            text="Введите TelegramID пользователя, которого нужно зарегистрировать:",
            reply_markup=make_row_keyboard(register_menu_buttons)
        )
        await state.set_state(RegisterUser.user_id)
    else:
        await state.clear()


@router_register_user.message(
    StateFilter("RegisterUser:user_id")
)
async def recieved_user_id(message: Message, state: FSMContext):
    await state.update_data(user_id=message.text.lower())
    await message.answer(
        text="Теперь введите полностью ФИО сотрудника:",
        reply_markup=make_row_keyboard(register_menu_buttons)
    )
    await state.set_state(RegisterUser.user_name)


@router_register_user.message(
    StateFilter("RegisterUser:user_name")
)
async def received_user_id(message: Message, state: FSMContext):
    await state.update_data(user_name=message.text)
    await message.answer(
        text="Теперь введите СНИЛС сотрудника:",
        reply_markup=make_row_keyboard(register_menu_buttons)
    )
    await state.set_state(RegisterUser.user_snils)


@router_register_user.message(
    StateFilter("RegisterUser:user_snils")
)
async def received_user_id(message: Message, state: FSMContext):
    await state.update_data(user_snils=message.text.lower())
    user_data = await state.get_data()

    result = await add_user_to_db(user_data['user_id'], user_data['user_name'], user_data['user_snils'])

    if result:
        await message.answer(
            text="Спасибо. Регистрация завершена.",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await message.answer(
            text="Ошибка регистрации пользователя!",
            reply_markup=ReplyKeyboardRemove()
        )
    await state.clear()
