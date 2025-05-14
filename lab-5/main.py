import asyncio  
import sqlite3  

from aiogram import Bot, Dispatcher, types  # импортируем основные классы aiogram
from aiogram.filters import Command  # импортируем фильтр для команд
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, BotCommand  # типы Telegram-кнопок и команд
from aiogram.fsm.context import FSMContext  # контекст состояния FSM
from aiogram.fsm.state import State, StatesGroup  # объявления состояний FSM
from aiogram.fsm.storage.memory import MemoryStorage  # хранилище состояний в памяти

from db import init_db  # импортируем функцию инициализации БД

# класс состояний для FSM (Finite State Machine)
class CurrencyStates(StatesGroup):
    add_name = State()  # ввод названия при добавлении
    add_rate = State()  # ввод курса при добавлении
    del_name = State()  # ввод названия при удалении
    upd_name = State()  # ввод названия при обновлении
    upd_rate = State()  # ввод нового курса при обновлении
    conv_name = State()  # ввод названия для конвертации
    conv_amount = State()  # ввод суммы для конвертации

# функция проверки, является ли пользователь админом
def is_admin(conn: sqlite3.Connection, chat_id: int) -> bool:
    cur = conn.cursor()  # создаём курсор
    cur.execute("SELECT 1 FROM admins WHERE chat_id=?", (str(chat_id),))  # проверяем наличие chat_id
    return cur.fetchone() is not None  # возвращаем True, если запись найдена

async def main():  # основная асинхронная функция запуска бота
    conn = init_db()  # инициализируем базу данных
    bot = Bot(token="8121046553:AAGUhiytJBTSEs6BpUJCit3py1mxA8F1NLM")  # создаём объект бота с токеном
    dp = Dispatcher(storage=MemoryStorage())  # создаём диспетчер с хранением FSM в памяти

    # вспомогательная команда /get_id — выводит ваш chat_id
    async def get_id(m: types.Message):
        await m.answer(str(m.chat.id))  # отправляем chat_id обратно пользователю
    dp.message.register(get_id, Command(commands=["get_id"]))  # регистрируем хендлер

    # команда /start — настраиваем видимые команды бота
    async def cmd_start(m: types.Message):
        if is_admin(conn, m.chat.id):  # проверяем, админ ли пользователь
            cmds = [  # список команд для админа
                BotCommand(command="start", description="Начало"),
                BotCommand(command="manage_currency", description="Управление валютами"),
                BotCommand(command="get_currencies", description="Список валют"),
                BotCommand(command="convert", description="Конвертация"),
            ]
        else:
            cmds = [  # список команд для всех остальных
                BotCommand(command="start", description="Начало"),
                BotCommand(command="get_currencies", description="Список валют"),
                BotCommand(command="convert", description="Конвертация"),
            ]
        await bot.set_my_commands(cmds)  # применяем команды
        await m.answer("Меню обновлено")  # подтверждение пользователю
    dp.message.register(cmd_start, Command(commands=["start"]))  # регистрируем хендлер

    # команда /manage_currency — показывает меню управления валютами
    async def manage_currency(m: types.Message):
        if not is_admin(conn, m.chat.id):  # если не админ
            return await m.answer("Нет доступа к команде")  # отказ в доступе
        kb = InlineKeyboardMarkup(
            inline_keyboard=[[  # создаём одну строку кнопок
                InlineKeyboardButton(text="Добавить валюту", callback_data="add"),
                InlineKeyboardButton(text="Удалить валюту", callback_data="delete"),
                InlineKeyboardButton(text="Изменить курс", callback_data="update"),
            ]]
        )
        await m.answer("Выберите действие:", reply_markup=kb)  # отправляем меню
    dp.message.register(manage_currency, Command(commands=["manage_currency"]))  # регистрируем хендлер

    # обработчики callback-кнопок
    async def cb_add(cq: types.CallbackQuery, state: FSMContext):
        await cq.message.answer("Введите название валюты")  # просим указать название
        await state.set_state(CurrencyStates.add_name)  # переходим в состояние add_name
        await cq.answer()  # отвечаем на callback
    dp.callback_query.register(cb_add, lambda c: c.data == "add")  # регистрируем

    async def cb_delete(cq: types.CallbackQuery, state: FSMContext):
        await cq.message.answer("Введите название валюты")  # просим указать название для удаления
        await state.set_state(CurrencyStates.del_name)  # переходим в состояние del_name
        await cq.answer()  # отвечаем на callback
    dp.callback_query.register(cb_delete, lambda c: c.data == "delete")

    async def cb_update(cq: types.CallbackQuery, state: FSMContext):
        await cq.message.answer("Введите название валюты")  # просим указать название для обновления
        await state.set_state(CurrencyStates.upd_name)  # переходим в состояние upd_name
        await cq.answer()  # отвечаем на callback
    dp.callback_query.register(cb_update, lambda c: c.data == "update")

    # ввод названия валюты при добавлении
    async def add_name(m: types.Message, state: FSMContext):
        name = m.text.lower()  # приводим к lowercase
        cur = conn.cursor()  # создаём курсор
        cur.execute("SELECT 1 FROM currencies WHERE currency_name=?", (name,))  # проверяем существование
        if cur.fetchone():  # если есть
            await m.answer("Данная валюта уже существует")  # информируем
            await state.clear()  # сбрасываем состояние
            return
        await state.update_data(name=name)  # сохраняем имя в данных FSM
        await m.answer("Введите курс к рублю")  # просим курс
        await state.set_state(CurrencyStates.add_rate)  # переходим в состояние add_rate
    dp.message.register(add_name, CurrencyStates.add_name)

    # ввод курса при добавлении
    async def add_rate(m: types.Message, state: FSMContext):
        data = await state.get_data()  # получаем сохранённые данные
        rate = float(m.text.replace(",", "."))  # парсим число с запятой
        conn.cursor().execute(
            "INSERT INTO currencies(currency_name, rate) VALUES(?, ?)" ,
            (data["name"], rate)  # вставляем в таблицу
        )
        conn.commit()  # сохраняем изменения
        await m.answer(f"Валюта: {data['name']} успешно добавлена")  # подтверждаем
        await state.clear()  # сбрасываем состояние
    dp.message.register(add_rate, CurrencyStates.add_rate)

    # удаление валюты по названию
    async def delete_name(m: types.Message, state: FSMContext):
        name = m.text.lower()  # приводим к lowercase
        conn.cursor().execute(
            "DELETE FROM currencies WHERE currency_name=?", (name,)  # удаляем запись
        )
        conn.commit()  # сохраняем изменения
        await m.answer(f"Валюта: {name} удалена")  # подтверждение
        await state.clear()  # сброс состояния
    dp.message.register(delete_name, CurrencyStates.del_name)

    # ввод названия при обновлении курса
    async def upd_name(m: types.Message, state: FSMContext):
        name = m.text.lower()  # приводим к lowercase
        cur = conn.cursor()  # создаём курсор
        cur.execute("SELECT 1 FROM currencies WHERE currency_name=?", (name,))  # проверяем существование
        if not cur.fetchone():  # если нет
            await m.answer("Валюта не найдена")  # информируем
            await state.clear()  # сбрасываем состояние
            return
        await state.update_data(name=name)  # сохраняем имя
        await m.answer("Введите новый курс к рублю")  # просим новый курс
        await state.set_state(CurrencyStates.upd_rate)  # переходим в состояние upd_rate
    dp.message.register(upd_name, CurrencyStates.upd_name)

    # ввод нового курса при обновлении
    async def upd_rate(m: types.Message, state: FSMContext):
        data = await state.get_data()  # получаем имя из FSM
        rate = float(m.text.replace(",", "."))  # парсим число
        conn.cursor().execute(
            "UPDATE currencies SET rate=? WHERE currency_name=?" , (rate, data["name"])  # обновляем курс
        )
        conn.commit()  # сохраняем изменения
        await m.answer(f"Курс {data['name']} обновлён")  # подтверждение
        await state.clear()  # сброс состояния
    dp.message.register(upd_rate, CurrencyStates.upd_rate)

    # команда /get_currencies — выводит все валюты
    async def get_currencies(m: types.Message):
        rows = conn.cursor().execute(
            "SELECT currency_name, rate FROM currencies"  # выбираем пары
        ).fetchall()  # получаем все
        if not rows:
            await m.answer("Список пуст")  # если нет записей
        else:
            await m.answer("\n".join(f"{n}: {r}" for n, r in rows))  # выводим список
    dp.message.register(get_currencies, Command(commands=["get_currencies"]))

    # команда /convert — начало конвертации
    async def conv_start(m: types.Message, state: FSMContext):
        await m.answer("Введите название валюты")  # просим имя
        await state.set_state(CurrencyStates.conv_name)  # переходим в conv_name
    dp.message.register(conv_start, Command(commands=["convert"]))

    # ввод названия валюты для конвертации
    async def conv_name(m: types.Message, state: FSMContext):
        await state.update_data(name=m.text.lower())  # сохраняем имя
        await m.answer("Введите сумму")  # просим сумму
        await state.set_state(CurrencyStates.conv_amount)  # переходим в conv_amount
    dp.message.register(conv_name, CurrencyStates.conv_name)

    # ввод суммы и вывод результата в рублях
    async def conv_amount(m: types.Message, state: FSMContext):
        data = await state.get_data()  # получаем данные
        row = conn.cursor().execute(
            "SELECT rate FROM currencies WHERE currency_name=?", (data["name"],)
        ).fetchone()  # ищем курс
        if not row:
            await m.answer("Валюта не найдена")  # если нет такой валюты
        else:
            rub = float(m.text.replace(",", ".")) * row[0]  # считаем рубли
            await m.answer(f"{m.text} {data['name']} = {rub} RUB")  # выводим результат
        await state.clear()  # сбрасываем состояние
    dp.message.register(conv_amount, CurrencyStates.conv_amount)

    # запускаем polling и корректно обрабатываем выход
    try:
        await dp.start_polling(bot)  # запускаем обработку обновлений
    except (asyncio.CancelledError, KeyboardInterrupt):
        pass  # тихий выход при Ctrl+C
    finally:
        await bot.session.close()  # закрываем сессию бота

if __name__ == "__main__":
    asyncio.run(main())  # точка входа при запуске файла
