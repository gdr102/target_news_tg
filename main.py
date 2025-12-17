import os
import asyncio

from dotenv import load_dotenv

from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError

from app.facebook.actor import Actor
from app.functions.message import Message

from app.handlers.core import core_handler

# Загрузка переменных из .env
load_dotenv()

API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
SESSION_NAME = os.getenv('SESSION_NAME')
TARGET_CHANNEL_ID = int(os.getenv('TARGET_CHANNEL_ID'))

TOKEN_APIFY = os.getenv('TOKEN_APIFY')
INTERVAL_CHECK = int(os.getenv('INTERVAL_CHECK'))

# Создаем клиента
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# Основная функция
async def main():
    print("Бот запущен...")
    print("Ожидание сообщений...")

    # получение информации о аккаунте
    me = await client.get_me()
    print(f"Вы вошли как: {me.first_name} (@{me.username})")

    msg = Message(client, TARGET_CHANNEL_ID)
    actor = Actor(api_token=TOKEN_APIFY, msg=msg, interval=INTERVAL_CHECK)
    
    # регистрируем обработчики
    await core_handler(client, events, msg, actor)
    
    async def handle_check_fb():
        await msg.send(message='ℹ️ <b>Запускаю проверку Facebook источников...</b>')
        await actor.run()

    # ПОТОМ запускаем периодическую проверку
    async def start_periodic_check():
        await handle_check_fb()

        while True:
            await asyncio.sleep(INTERVAL_CHECK)
            await handle_check_fb()
    
    asyncio.create_task(start_periodic_check())

    # клиент будет работать пока не будет остановлен вручную
    await client.run_until_disconnected()

if __name__ == '__main__':
    try:
        with client:
            client.loop.run_until_complete(main())
    except SessionPasswordNeededError:
        print("Требуется двухфакторная аутентификация. Проверьте Telegram.")
    except Exception as e:
        print(f"Ошибка: {e}")
