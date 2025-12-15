import os

from dotenv import load_dotenv

from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError

from app.functions.message import Message

from app.handlers.core import core_handler

# Загрузка переменных из .env
load_dotenv()

API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
SESSION_NAME = os.getenv('SESSION_NAME')
TARGET_CHANNEL_ID = int(os.getenv('TARGET_CHANNEL_ID'))

# Создаем клиента
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# Основная функция
async def main():
    print("Бот запущен...")
    print("Ожидание сообщений...")

    # получение информации о аккаунте
    me = await client.get_me()
    print(f"Вы вошли как: {me.first_name} (@{me.username})")

    msg = Message(client, TARGET_CHANNEL_ID)  # Инициализация класса Message
    
    # запуск основного обработчика
    await core_handler(client, events, msg)

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
