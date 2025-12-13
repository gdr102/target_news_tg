from app.handlers.get.new_message import get_new_message
from app.handlers.get.all_channels import get_all_channels

from app.storage.config import target_channel_id

async def core_handler(client, events):
    """Основной обработчик"""

    # Обработчик входящих сообщений
    await get_new_message(client, events, target_channel_id)

    # Обработчик команды /sources для получения всех каналов
    await get_all_channels(client, events, target_channel_id)


    