from app.handlers.get.new_message import new_message_hanlder

from app.handlers.get.all_channels import get_sources_handler
from app.handlers.changes.add_source import add_source_handler
from app.handlers.changes.remove_source import remove_source_handler

from app.handlers.get.all_keyword import get_keywords_handler
from app.handlers.changes.add_keyword import add_keyword_handler
from app.handlers.changes.remove_keyword import remove_keyword_handler

from app.handlers.other.help import help_handler
from app.functions.other import delete_author_message

from app.storage.config import target_channel_id

async def core_handler(client, events):
    """Основной обработчик"""

    # Обработчик входящих сообщений
    @client.on(events.NewMessage(incoming=True))
    async def handle_new_message(event):
        await new_message_hanlder(client, event, target_channel_id)

    # Обработчик команды /sources для получения всех каналов
    @client.on(events.NewMessage(chats=target_channel_id, pattern='/sources'))
    async def handle_sources_command(event):
        await get_sources_handler(client, event, target_channel_id)
        await delete_author_message(client, event) # удаление сообщения команды

    # Обработчик команды /add_source для добавления нового источника
    @client.on(events.NewMessage(chats=target_channel_id, pattern='/add_source (.*)'))
    async def handle_add_source_command(event):
        await add_source_handler(client, event, target_channel_id)
        await delete_author_message(client, event) # удаление сообщения команды
    
    # Обработчик команды /remove_source для удаления источника
    @client.on(events.NewMessage(chats=target_channel_id, pattern='/remove_source (.*)'))
    async def handle_remove_source_command(event):
        await remove_source_handler(client, event, target_channel_id)
        await delete_author_message(client, event) # удаление сообщения команды

    # Обработчик команды /keywords для получения всех ключевых слов
    @client.on(events.NewMessage(chats=target_channel_id, pattern='/keywords'))
    async def handle_keywords_command(event):
        await get_keywords_handler(client, event, target_channel_id)
        await delete_author_message(client, event) # удаление сообщения команды

    # Обработчик команды /add_keyword для добавления нового ключевого слова
    @client.on(events.NewMessage(chats=target_channel_id, pattern='/add_keyword "(.*)"'))
    async def handle_add_keyword_command(event):
        await add_keyword_handler(client, event, target_channel_id)
        await delete_author_message(client, event) # удаление сообщения команды

    # Обработчик команды /remove_keyword для удаления ключевого слова
    @client.on(events.NewMessage(chats=target_channel_id, pattern='/remove_keyword "(.*)"'))
    async def handle_remove_keyword_command(event):
        await remove_keyword_handler(client, event, target_channel_id)
        await delete_author_message(client, event) # удаление сообщения команды

    # Обработчик команды /help для отображения справочной информации
    @client.on(events.NewMessage(chats=target_channel_id, pattern='/help'))
    async def handle_help_command(event):
        await help_handler(client, event, target_channel_id)   
        await delete_author_message(client, event) # удаление сообщения команды
