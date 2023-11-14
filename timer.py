import asyncio
from aiogram import types

# Словарь для хранения Event'ов для каждого пользователя
user_events = {}


async def stop_timer(user_id):
    event = user_events.get(user_id)
    if event:
        event.set()  # Устанавливаем сигнал для остановки таймера


async def timer(message: types.Message, delay, response_text):
    user_id = message.from_user.id
    event = user_events.get(user_id)

    if not event:
        event = asyncio.Event()
        user_events[user_id] = event

    try:
        while not event.is_set():
            await asyncio.sleep(1)
            delay -= 1

            if delay <= 0:
                await message.answer(response_text)
                break
    except asyncio.CancelledError:
        pass  # Ожидаемый отменяемый таймер
    finally:
        # По завершении таймера удаляем Event из словаря
        user_events.pop(user_id, None)


async def run_timer(message: types.Message):
    await timer(message, 10*60, "Добрый день!")
    await timer(message, 90*60, "Подготовила для вас материал")
    await timer(message, 120*60, "Скоро вернусь с новым материалом!")
