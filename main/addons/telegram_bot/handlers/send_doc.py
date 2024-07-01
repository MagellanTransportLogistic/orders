import datetime
import os

from aiogram import Router
from aiogram.client import bot
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove

from main.addons.telegram_bot.keyboards.simple_row import make_row_keyboard
from magellan_web.settings import MEDIA_ROOT

router_send_doc = Router()

send_doc_menu_buttons = ["Отмена"]


class SendDoc(StatesGroup):
    send_doc = State()


@router_send_doc.message(StateFilter(None), Command("send_doc"))
async def cmd_send_doc(message: Message, state: FSMContext, role_id: int):
    if role_id >= 1:
        await message.answer(
            text="Нажмите на скрепку и приложите в качестве сообщения документ, который хотите отправить."
                 + chr(10) + "Изображение нужно отправлять без сжатия, как файл.",
            reply_markup=make_row_keyboard(send_doc_menu_buttons)
        )
        await state.set_state(SendDoc.send_doc)
    else:
        await state.clear()


@router_send_doc.message(
    StateFilter("SendDoc:send_doc")
)
async def received_message(message: Message, state: FSMContext, path: str):
    def create_path_tree(dir_path, parts):
        if len(parts) == 0:
            return
        if len(dir_path) == 0:
            _path = parts.pop(0)
        else:
            _path = os.path.join(dir_path, parts.pop(0))
        if not os.path.isdir(_path):
            os.mkdir(_path)
        create_path_tree(_path, parts)

    user_data = None
    try:
        await state.update_data(send_doc=message.document)
        user_data = await state.get_data()
    except Exception as E:
        await message.answer(
            text="Ошибка разбора документа. Вы не отправили файл?",
            reply_markup=ReplyKeyboardRemove()
        )
        print(f'send_doc:received_message: {E}')
        await state.clear()
    if user_data.get('send_doc') is not None:
        file_id = user_data['send_doc'].file_id
        file_name = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{user_data['send_doc'].file_name}"
        mime_type = user_data['send_doc'].mime_type

        # Что-то прислали.
        if mime_type in ['image/png', 'image/jpeg']:
            create_path_tree('', [MEDIA_ROOT, 'bot/', path])

            await message.bot.download(file_id, os.path.join(MEDIA_ROOT, 'bot/', path, file_name))
            await message.answer(
                text=f"Файл: {user_data['send_doc'].file_name} принят, спасибо.",
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            await message.answer(
                text="Вы отправили файл неподдерживаемого формата. "
                     "Возможно вы отправили его как картинку, а не как файл?",
                reply_markup=ReplyKeyboardRemove()
            )
    else:
        await message.answer(
            text="Вы не отправили файл.",
            reply_markup=ReplyKeyboardRemove()
        )
    await state.clear()
