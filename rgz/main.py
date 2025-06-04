# импортирую необходимые компоненты из aiogram
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode  # для поддержки HTML-разметки
from aiogram.client.default import DefaultBotProperties  # для настроек бота по умолчанию
from aiogram.types import BotCommand  # для создания команд меню бота

# импортирую токен бота из конфигурационного файла
from config import BOT_TOKEN
# импортирую роутер с обработчиками команд
from handlers import router

# создаю экземпляр бота с HTML-разметкой по умолчанию
bot = Bot(
    token=BOT_TOKEN,  # передаю токен бота
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)  # устанавливаю HTML-разметку
)

# создаю диспетчер для обработки входящих сообщений
dp = Dispatcher()
# подключаю роутер с обработчиками к диспетчеру
dp.include_router(router)

# основная асинхронная функция для запуска бота
async def main():
    # устанавливаю команды меню бота
    await bot.set_my_commands([
        BotCommand(command="reg", description="Регистрация"),  # команда регистрации
        BotCommand(command="add_operation", description="Добавить операцию"),  # команда добавления операции
        BotCommand(command="operations", description="Показать операции")  # команда просмотра операций
    ])
    
    # запускаю бота в режиме опроса сервера Telegram
    await dp.start_polling(bot)

# точка входа в программу
if __name__ == "__main__":
    import asyncio  # импортирую модуль для асинхронного выполнения
    # запускаю основную функцию
    asyncio.run(main())