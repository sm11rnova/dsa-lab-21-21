import asyncio
from db import engine
from models import Base

# создаю асинхронную функцию для создания таблиц
async def create_tables():
    # открываю асинхронное соединение с базой данных
    async with engine.begin() as conn:
        # выполняю синхронный метод создания всех таблиц
        await conn.run_sync(Base.metadata.create_all)

# проверяю, что скрипт запущен напрямую
if __name__ == "__main__":
    # запускаю асинхронную функцию через asyncio.run
    asyncio.run(create_tables())