# импортирую необходимые компоненты из aiogram и других модулей
from aiogram import Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from db import SessionLocal
from models import User, Operation
from config import FLASK_URL
import aiohttp
from datetime import datetime
from decimal import Decimal

# создаю экземпляр роутера для обработки сообщений
router = Router()

# FSM состояния 
# определяю состояния для регистрации пользователя
class RegState(StatesGroup):
    waiting_for_login = State()  # состояние ожидания ввода логина

# определяю состояния для работы с операциями
class OperationState(StatesGroup):
    waiting_for_type = State()    # состояние ожидания выбора типа операции
    waiting_for_sum = State()     # состояние ожидания ввода суммы
    waiting_for_date = State()    # состояние ожидания ввода даты
    currency_select = State()     # состояние выбора валюты
    type_filter = State()         # состояние выбора фильтра операций

# Клавиатуры 
# создаю клавиатуру для выбора типа операции
def operation_type_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="ДОХОД", callback_data="ДОХОД")],
        [InlineKeyboardButton(text="РАСХОД", callback_data="РАСХОД")]
    ])

# создаю клавиатуру для выбора валюты
def currency_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="RUB", callback_data="RUB")],
        [InlineKeyboardButton(text="USD", callback_data="USD")],
        [InlineKeyboardButton(text="EUR", callback_data="EUR")]
    ])

# создаю клавиатуру для фильтрации операций
def filter_type_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="ВСЕ", callback_data="ALL")],
        [InlineKeyboardButton(text="ДОХОДНЫЕ ОПЕРАЦИИ", callback_data="INCOME")],
        [InlineKeyboardButton(text="РАСХОДНЫЕ ОПЕРАЦИИ", callback_data="EXPENSE")]
    ])

# Обработчики команд 
# обработчик команды /reg
@router.message(Command("reg"))
async def register_user(message: Message, state: FSMContext):
    async with SessionLocal() as session:
        # проверяю, есть ли пользователь в базе
        res = await session.execute(select(User).where(User.chat_id == message.chat.id))
        if res.scalar():
            await message.answer("Вы уже зарегистрированы.")
            return
    
    # перехожу в состояние ожидания логина
    await state.set_state(RegState.waiting_for_login)
    await message.answer("Введите логин:")

# обработчик ввода логина
@router.message(RegState.waiting_for_login)
async def save_login(message: Message, state: FSMContext):
    async with SessionLocal() as session:
        # создаю нового пользователя
        new_user = User(name=message.text, chat_id=message.chat.id)
        session.add(new_user)
        await session.commit()
    
    await message.answer("Регистрация прошла успешно.")
    # очищаю состояние
    await state.clear()

# обработчик команды /add_operation
@router.message(Command("add_operation"))
async def add_operation(message: Message, state: FSMContext):
    async with SessionLocal() as session:
        # проверяю, зарегистрирован ли пользователь
        user = await session.execute(select(User).where(User.chat_id == message.chat.id))
        if not user.scalar():
            await message.answer("Сначала зарегистрируйтесь с помощью /reg.")
            return
    
    # перехожу в состояние ожидания типа операции
    await state.set_state(OperationState.waiting_for_type)
    await message.answer("Выберите тип операции:", reply_markup=operation_type_kb())

# обработчик выбора типа операции
@router.callback_query(OperationState.waiting_for_type)
async def choose_type(callback: CallbackQuery, state: FSMContext):
    # сохраняю выбранный тип операции
    await state.update_data(type=callback.data)
    await callback.message.answer("Введите сумму в рублях:")
    # перехожу в состояние ожидания суммы
    await state.set_state(OperationState.waiting_for_sum)
    await callback.answer()

# обработчик ввода суммы
@router.message(OperationState.waiting_for_sum)
async def input_sum(message: Message, state: FSMContext):
    try:
        # преобразую введенную сумму в число
        amount = float(message.text)
        await state.update_data(sum=amount)
        await message.answer("Введите дату операции в формате ГГГГ-ММ-ДД:")
        # перехожу в состояние ожидания даты
        await state.set_state(OperationState.waiting_for_date)
    except ValueError:
        await message.answer("Введите корректную сумму.")

# обработчик ввода даты
@router.message(OperationState.waiting_for_date)
async def input_date(message: Message, state: FSMContext):
    try:
        # преобразую введенную дату
        date = datetime.strptime(message.text, "%Y-%m-%d").date()
        data = await state.get_data()
        
        async with SessionLocal() as session:
            # создаю новую операцию
            op = Operation(
                date=date,
                sum=data["sum"],
                chat_id=message.chat.id,
                type_operation=data["type"]
            )
            session.add(op)
            await session.commit()
        
        await message.answer("Операция успешно добавлена.")
        # очищаю состояние
        await state.clear()
    except ValueError:
        await message.answer("Введите дату в формате ГГГГ-ММ-ДД.")

# обработчик команды /operations
@router.message(Command("operations"))
async def view_operations(message: Message, state: FSMContext):
    async with SessionLocal() as session:
        # проверяю, зарегистрирован ли пользователь
        user = await session.execute(select(User).where(User.chat_id == message.chat.id))
        if not user.scalar():
            await message.answer("Сначала зарегистрируйтесь с помощью /reg.")
            return
    
    # перехожу в состояние выбора валюты
    await state.set_state(OperationState.currency_select)
    await message.answer("Выберите валюту:", reply_markup=currency_kb())

# обработчик выбора валюты
@router.callback_query(OperationState.currency_select)
async def select_currency(callback: CallbackQuery, state: FSMContext):
    # сохраняю выбранную валюту
    await state.update_data(currency=callback.data)
    # перехожу в состояние выбора фильтра
    await state.set_state(OperationState.type_filter)
    await callback.message.answer("Выберите тип операций:", reply_markup=filter_type_kb())
    await callback.answer()

# обработчик фильтрации операций
@router.callback_query(OperationState.type_filter)
async def filter_operations(callback: CallbackQuery, state: FSMContext):
    # получаю сохраненные данные
    data = await state.get_data()
    currency = data["currency"]
    type_filter = callback.data
    
    # формирую базовый запрос
    query = select(Operation).where(Operation.chat_id == callback.message.chat.id)

    # добавляю фильтр по типу операции
    if type_filter == "INCOME":
        query = query.where(Operation.type_operation == "ДОХОД")
    elif type_filter == "EXPENSE":
        query = query.where(Operation.type_operation == "РАСХОД")

    async with SessionLocal() as session:
        # выполняю запрос
        res = await session.execute(query)
        operations = res.scalars().all()

    # устанавливаю курс по умолчанию
    rate = Decimal("1.0")
    if currency != "RUB":
        async with aiohttp.ClientSession() as sess:
            async with sess.get(f"{FLASK_URL}/rate?currency={currency}") as resp:
                if resp.status == 200:
                    rate = Decimal(str((await resp.json())["rate"]))

    if not operations:
        await callback.message.answer("Операций не найдено.")
        return

    # формирую текст с операциями
    text = f"Операции в валюте: {currency}\n\n"
    for op in operations:
        # конвертирую сумму в выбранную валюту
        converted = round(op.sum / rate, 2)
        text += f"{op.date} | {op.type_operation} | {converted} {currency}\n"

    await callback.message.answer(text)
    # очищаю состояние
    await state.clear()
    await callback.answer()