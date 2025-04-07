import asyncio
import json

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import StatesGroup, State
import datetime
import os

from keyboards.simple_row import make_row_keyboard
from aiogram.utils.chat_action import ChatActionSender

router_menu = Router()

register_menu_buttons = ["Отмена"]
SEND_MESSAGE_DELAY = 0.2


class Form(StatesGroup):
    _end_automates = {
        "text": [
            "ev_arrive_load",
            "ev_arrive_unload",
            "ev_arrive_parking",
            "ev_leave_parking",
            "ev_leave_repair",
        ],
        "text,photo": [
            "ev_arrive_repair",
            "ev_leave_cancel",
            "ev_leave_reroute",
            "ev_repair_need",
            "ev_repair_done",
            "ev_event_crash",
            "ev_event_cargo",
            "ev_event_late",
            "ev_event_police",
            "ev_event_medicine",
            "ev_change_tg_off",
            "ev_change_tg_on",
            "ev_change_pc_on",
            "ev_change_pc_off",
            "ev_work_base",
            "ev_work_cargo",
            "ev_work_vacation",
            "ev_work_weekend",
            "ev_work_i_can_die",
        ],
        "text,bool,photo": ["ev_leave_load", "ev_leave_unload"],
        "int": ["ev_money_need"],
        "int,text,photo": [
            "ev_money_sub",
            "ev_fuel_need_by_card",
            "ev_fuel_need_by_cash",
        ],
        "int,text": [
            "ev_money_add",
            "ev_fuel_need",
            "ev_fuel_not_can",
            "ev_fuel_not_station",
        ],
    }
    _end_automates_texts = {
        "ev_arrive_load": {"text": "Введите комментарий по поводу погрузки."},
        "ev_arrive_unload": {"text": "Введите комментарий о разгрузке."},
        "ev_arrive_parking": {"text": "Прокомментируйте прибытие на парковку..."},
        "ev_leave_parking": {
            "text": "Подробно опишите, зачем вы решили покинуть парковку?"
        },
        "ev_leave_repair": {"text": "Опишите, как прошел ремонт?"},
        "ev_arrive_repair": {
            "text": "Введите комментарий",
            "photo": "Приложите фотографию ТС",
        },
        "ev_leave_cancel": {
            "text": "Введите комментарий",
            "photo": "Приложите фотографию/скан документа",
        },
        "ev_leave_reroute": {
            "text": "Введите комментарий",
            "photo": "Приложите фотографию/скан документа",
        },
        "ev_repair_need": {
            "text": "Введите комментарий",
            "photo": "Приложите фотографию/скан документа для согласования ремонта.",
        },
        "ev_repair_done": {
            "text": "Введите комментарий",
            "photo": "Приложите фотографию/скан документа о ремонте.",
        },
        "ev_event_crash": {
            "text": "Введите комментарий",
            "photo": "Приложите фотографию с места ДТП.",
        },
        "ev_event_cargo": {
            "text": "Введите комментарий",
            "photo": "Приложите фотографию проблем с грузом.",
        },
        "ev_event_late": {
            "text": "Введите комментарий",
            "photo": "Приложите скан/фотографию документа, который подтверждает причину задержки.",
        },
        "ev_event_police": {
            "text": "Введите комментарий",
            "photo": "Приложите скан/фотографию документа-акта о правонарушении.",
        },
        "ev_event_medicine": {
            "text": "Опишите свое самочувствие",
            "photo": "Приложите фотографию/скан медицинского заключения.",
        },
        "ev_change_tg_off": {
            "text": "Введите комментарий",
            "photo": "Приложите фотографию тягача.",
        },
        "ev_change_tg_on": {
            "text": "Введите комментарий",
            "photo": "Приложите фотографию тягача.",
        },
        "ev_change_pc_on": {
            "text": "Введите комментарий",
            "photo": "Приложите фотографию прицепа.",
        },
        "ev_change_pc_off": {
            "text": "Введите комментарий",
            "photo": "Приложите фотографию прицепа.",
        },
        "ev_work_base": {
            "text": "Введите комментарий",
            "photo": "Приложите фотографию.",
        },
        "ev_work_cargo": {
            "text": "Введите комментарий",
            "photo": "Приложите фотографию.",
        },
        "ev_work_vacation": {
            "text": "Введите комментарий",
            "photo": "Приложите фотографию/скан заявления на отпуск.",
        },
        "ev_work_weekend": {
            "text": "Введите комментарий",
            "photo": "Приложите фотографию/скан заявления.",
        },
        "ev_work_i_can_die": {
            "text": "Введите комментарий",
            "photo": "Приложите фотографию/скан заключения врача/больничного.",
        },
        "ev_leave_load": {
            "text": "Введите комментарий",
            "bool": "Укажите, есть ли ТТН?",
            "photo": "Приложите фотографию/скан заключения врача/больничного.",
        },
        "ev_leave_unload": {
            "text": "Введите комментарий",
            "bool": "Укажите, есть ли ТТН?",
            "photo": "Приложите фотографию/скан заключения врача/больничного.",
        },
        "ev_money_need": {"int": "Введите сумму, которая вам требуется"},
        "ev_money_sub": {
            "int": "Введите сумму расхода",
            "text": "Комментарий",
            "photo": "Приложите скан/фото расходного документа",
        },
        "ev_fuel_need_by_card": {
            "int": "Введите требуемое количество топлива",
            "text": "Комментарий",
            "photo": "Приложите скан/фото",
        },
        "ev_fuel_need_by_cash": {
            "int": "Введите требуемое количество топлива",
            "text": "Комментарий",
            "photo": "Приложите скан/фото",
        },
        "ev_money_add": {"int": "Введите сумму", "text": "Комментарий"},
        "ev_fuel_need": {"int": "Введите количество горючки", "text": "Комментарий"},
        "ev_fuel_not_can": {"int": "Введите количество горючки", "text": "Комментарий"},
        "ev_fuel_not_station": {
            "int": "Введите количество горючки",
            "text": "Комментарий",
        },
    }

    init = State()
    init_chain = State()
    init_event = State()
    init_action = State()
    actions = State()
    current_event = State()
    command = State()
    raw_data = {}

    @classmethod
    def get_automate(cls, name):
        for k in cls._end_automates:
            if name in cls._end_automates[k]:
                return k
        return None

    @classmethod
    def get_action_text(cls, action: str, data_type: str) -> str:
        ret = "Описание для действия не задано!"
        try:
            _texts = cls._end_automates_texts.get(action.__str__(), None)
            if _texts:
                ret = _texts.get(data_type, ret)
        except ValueError:
            return ret
        return ret


def create_main_keyboard():
    builder = InlineKeyboardBuilder()
    builder.max_width = 2
    builder.add(types.InlineKeyboardButton(text="Прибытие", callback_data="im_arrive"))
    builder.add(types.InlineKeyboardButton(text="Убытие", callback_data="im_leave"))
    builder.add(types.InlineKeyboardButton(text="Финансы", callback_data="im_money"))
    builder.add(types.InlineKeyboardButton(text="ГСМ", callback_data="im_fuel"))
    builder.add(types.InlineKeyboardButton(text="Ремонт", callback_data="im_repair"))
    builder.add(
        types.InlineKeyboardButton(text="Происшествие", callback_data="im_event")
    )
    builder.add(
        types.InlineKeyboardButton(text="Смена ТС", callback_data="im_change_tr")
    )
    builder.add(types.InlineKeyboardButton(text="Труд", callback_data="im_work"))

    return builder


@router_menu.callback_query(F.data == "main_menu")
async def cmd_main_menu_callback(
    callback: types.CallbackQuery, state: FSMContext, role_id: int
):
    await state.clear()
    if role_id > 0:
        builder = create_main_keyboard()
        async with ChatActionSender.typing(
            bot=callback.message.bot, chat_id=callback.message.chat.id
        ):
            await asyncio.sleep(SEND_MESSAGE_DELAY)
            await callback.message.answer(
                text="Выберите событие.", reply_markup=builder.as_markup()
            )
        await callback.message.delete()
        # await callback.message.edit_reply_markup(reply_markup=None)
        await state.set_state(Form.init_event)
    else:
        await callback.message.answer(
            text="ВЫ должны быть зарегистрированы, чтобы использовать данную команду"
        )


@router_menu.message(Command("menu"))
async def cmd_main_menu(message: types.Message, state: FSMContext, role_id: int):
    await state.clear()
    if role_id > 0:
        builder = create_main_keyboard()
        await state.clear()

        async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
            await asyncio.sleep(SEND_MESSAGE_DELAY)
            await message.answer(
                text="Выберите событие.", reply_markup=builder.as_markup()
            )
        await state.set_state(Form.init_event)
    else:
        await message.answer(
            text="ВЫ должны быть зарегистрированы, чтобы использовать данную команду"
        )


@router_menu.callback_query(F.data == "im_arrive", Form.init_event)
async def cmd_im_arrive(callback: types.CallbackQuery, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.max_width = 2
    builder.add(
        types.InlineKeyboardButton(text="На загрузку", callback_data="ev_arrive_load")
    )
    builder.add(
        types.InlineKeyboardButton(text="На выгрузку", callback_data="ev_arrive_unload")
    )
    builder.add(
        types.InlineKeyboardButton(text="На стоянку", callback_data="ev_arrive_parking")
    )
    builder.add(
        types.InlineKeyboardButton(text="На ремонт", callback_data="ev_arrive_repair")
    )
    builder.add(types.InlineKeyboardButton(text="<- Назад", callback_data="main_menu"))

    async with ChatActionSender.typing(
        bot=callback.message.bot, chat_id=callback.message.chat.id
    ):
        await asyncio.sleep(SEND_MESSAGE_DELAY)
        await callback.message.answer(
            text="Прибытие на загрузку/выгрузку: Выберите действие.",
            reply_markup=builder.as_markup(),
        )
        await callback.message.delete()
        # await callback.message.edit_reply_markup(reply_markup=None)
    await state.set_state(Form.init_action)


@router_menu.callback_query(F.data == "im_leave", Form.init_event)
async def cmd_im_leave(callback: types.CallbackQuery, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.max_width = 2
    builder.add(
        types.InlineKeyboardButton(text="Загрузился", callback_data="ev_leave_load")
    )
    builder.add(
        types.InlineKeyboardButton(text="Выгрузился", callback_data="ev_leave_unload")
    )
    builder.add(
        types.InlineKeyboardButton(text="Со стоянки", callback_data="ev_leave_parking")
    )
    builder.add(
        types.InlineKeyboardButton(text="C ремонта", callback_data="ev_leave_repair")
    )
    builder.add(
        types.InlineKeyboardButton(
            text="Отмена загрузки", callback_data="ev_leave_cancel"
        )
    )
    builder.add(
        types.InlineKeyboardButton(
            text="Переадресация", callback_data="ev_leave_reroute"
        )
    )
    builder.add(types.InlineKeyboardButton(text="<- Назад", callback_data="main_menu"))

    async with ChatActionSender.typing(
        bot=callback.message.bot, chat_id=callback.message.chat.id
    ):
        await asyncio.sleep(SEND_MESSAGE_DELAY)
        await callback.message.answer(
            text="Убытие с загрузки/выгрузки: Выберите действие.", reply_markup=builder.as_markup()
        )
        await callback.message.delete()
        # await callback.message.edit_reply_markup(reply_markup=None)
    await state.set_state(Form.init_action)


@router_menu.callback_query(F.data == "im_money", Form.init_event)
async def cmd_im_leave(callback: types.CallbackQuery, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.max_width = 1
    builder.add(
        types.InlineKeyboardButton(text="Нужны деньги", callback_data="ev_money_need")
    )
    builder.add(types.InlineKeyboardButton(text="Расход", callback_data="ev_money_sub"))
    builder.add(types.InlineKeyboardButton(text="Приход", callback_data="ev_money_add"))
    builder.add(types.InlineKeyboardButton(text="<- Назад", callback_data="main_menu"))

    async with ChatActionSender.typing(
        bot=callback.message.bot, chat_id=callback.message.chat.id
    ):
        await asyncio.sleep(SEND_MESSAGE_DELAY)
        await callback.message.answer(
            text="Деньги: Выберите действие.", reply_markup=builder.as_markup()
        )
        # await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.delete()
    await state.set_state(Form.init_action)


@router_menu.callback_query(F.data == "im_fuel", Form.init_event)
async def cmd_im_leave(callback: types.CallbackQuery, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.max_width = 2
    builder.add(
        types.InlineKeyboardButton(text="Нужна заправка", callback_data="ev_fuel_need")
    )
    builder.add(
        types.InlineKeyboardButton(
            text="По топл. карте", callback_data="ev_fuel_need_by_card"
        )
    )
    builder.add(
        types.InlineKeyboardButton(
            text="За наличные", callback_data="ev_fuel_need_by_cash"
        )
    )
    builder.add(
        types.InlineKeyboardButton(text="Не в бак", callback_data="ev_fuel_not_can")
    )
    builder.add(
        types.InlineKeyboardButton(
            text="Не на АЗС", callback_data="ev_fuel_not_station"
        )
    )
    builder.add(types.InlineKeyboardButton(text="<- Назад", callback_data="main_menu"))

    async with ChatActionSender.typing(
        bot=callback.message.bot, chat_id=callback.message.chat.id
    ):
        await asyncio.sleep(SEND_MESSAGE_DELAY)
        await callback.message.answer(
            text="ГСМ: Выберите действие.", reply_markup=builder.as_markup()
        )
        # await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.delete()
    await state.set_state(Form.init_action)


@router_menu.callback_query(F.data == "im_repair", Form.init_event)
async def cmd_im_leave(callback: types.CallbackQuery, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.max_width = 1
    builder.add(
        types.InlineKeyboardButton(
            text="Запрос на ремонт", callback_data="ev_repair_need"
        )
    )
    builder.add(
        types.InlineKeyboardButton(
            text="Ремонт выполнен", callback_data="ev_repair_done"
        )
    )
    builder.add(types.InlineKeyboardButton(text="<- Назад", callback_data="main_menu"))

    async with ChatActionSender.typing(
        bot=callback.message.bot, chat_id=callback.message.chat.id
    ):
        await asyncio.sleep(SEND_MESSAGE_DELAY)
        await callback.message.answer(
            text="Ремонт: Выберите действие.", reply_markup=builder.as_markup()
        )
        # await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.delete()
    await state.set_state(Form.init_action)


@router_menu.callback_query(F.data == "im_event", Form.init_event)
async def cmd_im_leave(callback: types.CallbackQuery, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.max_width = 1
    builder.add(types.InlineKeyboardButton(text="ДТП", callback_data="ev_event_crash"))
    builder.add(
        types.InlineKeyboardButton(
            text="Проблема с грузом", callback_data="ev_event_cargo"
        )
    )
    builder.add(
        types.InlineKeyboardButton(
            text="Задержка в пути", callback_data="ev_event_late"
        )
    )
    builder.add(
        types.InlineKeyboardButton(
            text="Правонарушение", callback_data="ev_event_police"
        )
    )
    builder.add(
        types.InlineKeyboardButton(text="Медпомощь", callback_data="ev_event_medicine")
    )
    builder.add(types.InlineKeyboardButton(text="<- Назад", callback_data="main_menu"))

    async with ChatActionSender.typing(
        bot=callback.message.bot, chat_id=callback.message.chat.id
    ):
        await asyncio.sleep(SEND_MESSAGE_DELAY)
        await callback.message.answer(
            text="Происшествие: Выберите действие.", reply_markup=builder.as_markup()
        )
        # await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.delete()
    await state.set_state(Form.init_action)


@router_menu.callback_query(F.data == "im_change_tr", Form.init_event)
async def cmd_im_leave(callback: types.CallbackQuery, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.max_width = 1
    builder.add(
        types.InlineKeyboardButton(text="Тягач сдал", callback_data="ev_change_tg_off")
    )
    builder.add(
        types.InlineKeyboardButton(text="Тягач принял", callback_data="ev_change_tg_on")
    )
    builder.add(
        types.InlineKeyboardButton(text="Прицеп сдал", callback_data="ev_change_pc_off")
    )
    builder.add(
        types.InlineKeyboardButton(text="Прицеп принял", callback_data="ev_change_pc_on")
    )
    builder.add(types.InlineKeyboardButton(text="<- Назад", callback_data="main_menu"))

    async with ChatActionSender.typing(
        bot=callback.message.bot, chat_id=callback.message.chat.id
    ):
        await asyncio.sleep(SEND_MESSAGE_DELAY)
        await callback.message.answer(
            text="Смена ТС: Выберите действие.", reply_markup=builder.as_markup()
        )
        # await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.delete()
    await state.set_state(Form.init_action)


@router_menu.callback_query(F.data == "im_work", Form.init_event)
async def cmd_im_leave(callback: types.CallbackQuery, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.max_width = 1
    builder.add(
        types.InlineKeyboardButton(text="Работа на базе", callback_data="ev_work_base")
    )
    builder.add(
        types.InlineKeyboardButton(
            text="Работа с грузом", callback_data="ev_work_cargo"
        )
    )
    builder.add(
        types.InlineKeyboardButton(
            text="Запрос на отпуск", callback_data="ev_work_vacation"
        )
    )
    builder.add(
        types.InlineKeyboardButton(
            text="Нужен выходной", callback_data="ev_work_weekend"
        )
    )
    builder.add(
        types.InlineKeyboardButton(text="Больничный", callback_data="ev_work_i_can_die")
    )
    builder.add(types.InlineKeyboardButton(text="<- Назад", callback_data="main_menu"))

    async with ChatActionSender.typing(
        bot=callback.message.bot, chat_id=callback.message.chat.id
    ):
        await asyncio.sleep(SEND_MESSAGE_DELAY)
        await callback.message.answer(
            text="Труд: Выберите действие.", reply_markup=builder.as_markup()
        )
        # await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.delete()
    await state.set_state(Form.init_action)


@router_menu.callback_query(F.data.startswith("ev_"), Form.init_action)
async def cmd_init_action(callback: types.CallbackQuery, state: FSMContext):
    # Тут надо запустить конечный автомат нужного вида.
    # Определим какой автомат нужно запускать - у нас есть массив данных по видам автоматов.
    _type = Form.get_automate(callback.data)
    await callback.message.edit_reply_markup(reply_markup=None)

    if _type is not None:
        # Вид автомата определен
        _actions = list(_type.split(","))
        _current_event = _actions[0]
        await state.update_data(actions=_actions)
        await state.update_data(current_event=_current_event)
        await state.update_data(command=callback.data)
        await callback.message.answer(
            text=Form.get_action_text(callback.data, _current_event),
            reply_markup=make_row_keyboard(register_menu_buttons),
        )
        await state.set_state(Form.actions)
    else:
        await state.clear()


@router_menu.message(StateFilter("Form:actions"))
async def cmd_dynamic_fsm(message: Message, state: FSMContext, path: str):
    from bot import read_settings

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

    data = await state.get_data()
    _actions = data.get("actions", [])
    _command = data.get("command", "_none")
    _current_event = data.get("current_event", None)
    _raw_data = data.get("raw_data", {})

    if _current_event == "photo":
        try:
            await state.update_data(send_doc=message.document)
            user_data = await state.get_data()
        except Exception:
            await message.answer(
                text="Ошибка разбора документа. Вы не отправили файл? "
                "Отправьте файл повторно или отмените действие.",
                reply_markup=make_row_keyboard(register_menu_buttons),
            )
            return
        if user_data.get("send_doc") is not None:
            file_id = user_data["send_doc"].file_id
            file_name = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{user_data['send_doc'].file_name}"
            mime_type = user_data["send_doc"].mime_type

            # Что-то прислали.
            if mime_type in ["image/png", "image/jpeg"]:
                create_path_tree("", [read_settings("MEDIA_PATH"), "bot/", path])

                await message.bot.download(
                    file_id,
                    os.path.join(read_settings("MEDIA_PATH"), "bot/", path, file_name),
                )
                await message.answer(
                    text=f"Файл: {user_data['send_doc'].file_name} принят, спасибо.",
                    reply_markup=ReplyKeyboardRemove(),
                )
                _raw_data[_current_event] = file_name
            else:
                await message.answer(
                    text="Вы отправили файл неподдерживаемого формата. "
                    "Возможно вы отправили его как картинку, а не как файл?",
                    reply_markup=make_row_keyboard(register_menu_buttons),
                )
                return
        else:
            await message.answer(
                text="Вы не отправили файл. Отправьте файл или отмените действие.",
                reply_markup=make_row_keyboard(register_menu_buttons),
            )
            return
    else:
        _raw_data[_current_event] = message.text

    _actions.pop(0)

    _raw_data["command"] = _command
    _raw_data["user_id"] = message.from_user.id

    if len(_actions) > 0:
        _current_event = _actions[0]
        await message.answer(
            text=Form.get_action_text(_command, _current_event),
            reply_markup=make_row_keyboard(register_menu_buttons),
        )

    await state.update_data(actions=_actions)
    await state.update_data(current_event=_current_event)
    await state.update_data(raw_data=_raw_data)

    if len(_actions) == 0:
        # А вот тут надо записать данные в БД.
        _raw_data["dts"] = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        file_name = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        with open(
            os.path.join(
                os.path.join(read_settings("MEDIA_PATH"), "bot/", path, file_name)
            ),
            "w",
        ) as f:
            create_path_tree("", [read_settings("MEDIA_PATH"), "bot/", path])
            f.write(json.dumps(_raw_data, ensure_ascii=False, indent=4))
        await message.answer(
            text=f"Данные успешно записаны.", reply_markup=ReplyKeyboardRemove()
        )
        await state.clear()
