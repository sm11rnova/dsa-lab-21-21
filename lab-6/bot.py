import os
import logging
import requests
from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from dotenv import load_dotenv

# Загрузка токена из .env
load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")

if not API_TOKEN:
    raise ValueError("API_TOKEN is not set in .env")

# Настройка логирования и компонентов aiogram
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
router = Router()

# Состояния для FSM
class CurrencyState(StatesGroup):
    action = State()
    add_name = State()
    add_rate = State()
    delete_name = State()
    update_name = State()
    update_rate = State()
    convert_name = State()
    convert_amount = State()

@router.message(Command("start"))
async def cmd_start(message: Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text="/manage_currency")],
        [KeyboardButton(text="/get_currencies")],
        [KeyboardButton(text="/convert")]
    ])
    await message.answer("Выберите команду:", reply_markup=keyboard)

@router.message(Command("manage_currency"))
async def cmd_manage(message: Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, keyboard=[
        [KeyboardButton(text="Добавить валюту"), KeyboardButton(text="Удалить валюту")],
        [KeyboardButton(text="Изменить курс валюты")]
    ])
    await message.answer("Выберите действие:", reply_markup=keyboard)
    await state.set_state(CurrencyState.action)

@router.message(CurrencyState.action)
async def process_action(message: Message, state: FSMContext):
    if message.text == "Добавить валюту":
        await state.set_state(CurrencyState.add_name)
        await message.answer("Введите название валюты:")
    elif message.text == "Удалить валюту":
        await state.set_state(CurrencyState.delete_name)
        await message.answer("Введите название валюты:")
    elif message.text == "Изменить курс валюты":
        await state.set_state(CurrencyState.update_name)
        await message.answer("Введите название валюты:")
    else:
        await state.clear()
        await message.answer("Неверный выбор.")

@router.message(CurrencyState.add_name)
async def add_currency_name(message: Message, state: FSMContext):
    name = message.text
    r = requests.post('http://localhost:5001/load', json={'currency_name': name, 'rate': 0})
    if r.status_code == 400:
        await state.clear()
        await message.answer("Данная валюта уже существует.")
    else:
        await state.update_data(add_name=name)
        await state.set_state(CurrencyState.add_rate)
        await message.answer("Введите курс к рублю:")

@router.message(CurrencyState.add_rate)
async def add_currency_rate(message: Message, state: FSMContext):
    try:
        rate = float(message.text)
    except ValueError:
        await message.answer("Введите корректное число.")
        return
    data = await state.get_data()
    name = data['add_name']
    requests.post('http://localhost:5001/delete', json={'currency_name': name})
    requests.post('http://localhost:5001/load', json={'currency_name': name, 'rate': rate})
    await state.clear()
    await message.answer(f"Валюта {name} успешно добавлена.")

@router.message(CurrencyState.delete_name)
async def delete_currency(message: Message, state: FSMContext):
    name = message.text
    requests.post('http://localhost:5001/delete', json={'currency_name': name})
    await state.clear()
    await message.answer(f"Валюта {name} удалена (если существовала).")

@router.message(CurrencyState.update_name)
async def update_currency_name(message: Message, state: FSMContext):
    await state.update_data(update_name=message.text)
    await state.set_state(CurrencyState.update_rate)
    await message.answer("Введите курс к рублю:")

@router.message(CurrencyState.update_rate)
async def update_currency_rate(message: Message, state: FSMContext):
    try:
        rate = float(message.text)
    except ValueError:
        await message.answer("Введите корректное число.")
        return
    data = await state.get_data()
    name = data['update_name']
    r = requests.post('http://localhost:5001/update_currency', json={'currency_name': name, 'rate': rate})
    await state.clear()
    if r.status_code == 404:
        await message.answer("Валюта не найдена.")
    else:
        await message.answer(f"Курс валюты {name} обновлён.")

@router.message(Command("get_currencies"))
async def get_currencies(message: Message):
    r = requests.get('http://localhost:5002/currencies')
    if r.status_code != 200:
        await message.answer("Ошибка при получении валют.")
        return
    currencies = r.json().get("currencies", [])
    if not currencies:
        await message.answer("Валют нет.")
    else:
        text = "\n".join([f"{c['currency_name']}: {c['rate']}" for c in currencies])
        await message.answer(text)

@router.message(Command("convert"))
async def convert_start(message: Message, state: FSMContext):
    await state.set_state(CurrencyState.convert_name)
    await message.answer("Введите название валюты:")

@router.message(CurrencyState.convert_name)
async def convert_currency_name(message: Message, state: FSMContext):
    await state.update_data(convert_name=message.text)
    await state.set_state(CurrencyState.convert_amount)
    await message.answer("Введите сумму:")

@router.message(CurrencyState.convert_amount)
async def convert_currency_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
    except ValueError:
        await message.answer("Введите корректное число.")
        return
    data = await state.get_data()
    name = data['convert_name']
    r = requests.get(f"http://localhost:5002/convert?currency_name={name}&amount={amount}")
    await state.clear()
    if r.status_code == 404:
        await message.answer("Валюта не найдена.")
    else:
        result = r.json().get("converted_amount")
        await message.answer(f"Сумма в рублях: {result}")

# Запуск бота
async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
