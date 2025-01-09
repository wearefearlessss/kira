import asyncio
import logging
import os
import sqlite3
from datetime import datetime

import handlers.handlers
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Бот и диспетчер
bot = Bot(token=os.getenv("TOKEN"))
dp = Dispatcher(storage=MemoryStorage())

dp.include_router(handlers.handlers.router)

# Асинхронный запуск
async def main():
    logging.info("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())