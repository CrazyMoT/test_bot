import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram.types import FSInputFile
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from database import User, create_engine_and_session
from timer import run_timer, stop_timer


load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
dp = Dispatcher()
engine, async_session = create_engine_and_session()


@dp.message(Command('start'))
async def send_welcome(message: types.Message):
    await User.create_table(engine)
    result = await User.add_user(async_session, message.from_user)
    if result:
        photo = FSInputFile("./profile_photo.jpg")
        await message.answer_photo(photo, caption='This is pest programmer - my owner!')
    await run_timer(message)


@dp.message(Command('users_today'))
async def send_stat(message: types.Message):
    user_count = await User.count_users(async_session)
    await message.answer(f'Total users in DB: {user_count}')


@dp.message()
async def send_stat(message: types.Message):
    if message.text == 'Хорошего дня':
        await stop_timer(message.from_user.id)
        print('Он знает секрет, отмена операции!')
    else:
        await run_timer(message)


async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR, filename='bot.log')
    asyncio.run(main())
