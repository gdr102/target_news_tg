from telethon import TelegramClient

from app.functions.message import Message

from app.handlers.get.new_message import new_message_hanlder

from app.handlers.get.all_channels import get_sources_handler
from app.handlers.changes.add_source import add_source_handler
from app.handlers.changes.remove_source import remove_source_handler

from app.handlers.get.all_keyword import get_keywords_handler
from app.handlers.changes.add_keyword import add_keyword_handler
from app.handlers.changes.remove_keyword import remove_keyword_handler

from app.handlers.other.help import help_handler
from app.handlers.other.unknown import unknown_handler

async def core_handler(client: TelegramClient, events , msg: Message):
    """Основной обработчик"""

    target_channel_id = msg.target_channel_id  # Получение целевого канала из объекта Message

    # Обработчик входящих сообщений
    @client.on(events.NewMessage(incoming=True))
    async def handle_new_message(event):
        await new_message_hanlder(msg, event)

    # Обработчик команды /sources для получения всех каналов
    @client.on(events.NewMessage(chats=target_channel_id, pattern='/sources'))
    async def handle_sources_command(event):
        dialogs = await client.get_dialogs() # Получаем все диалоги

        await get_sources_handler(msg, dialogs) # вызов обработчика
        await msg.delete(event.message)  # удаление сообщения команды

    # Обработчик команды /add_source для добавления нового источника
    @client.on(events.NewMessage(chats=target_channel_id, pattern='/add_source (.*)'))
    async def handle_add_source_command(event):
        dialogs = await client.get_dialogs() # Получаем все диалоги

        await add_source_handler(client, msg, event, dialogs)
        await msg.delete(event.message)  # удаление сообщения команды
    
    # Обработчик команды /remove_source для удаления источника
    @client.on(events.NewMessage(chats=target_channel_id, pattern='/remove_source (.*)'))
    async def handle_remove_source_command(event):
        dialogs = await client.get_dialogs() # Получаем все диалоги

        await remove_source_handler(client, msg, event, dialogs)
        await msg.delete(event.message)  # удаление сообщения команды

    # Обработчик команды /keywords для получения всех ключевых слов
    @client.on(events.NewMessage(chats=target_channel_id, pattern='/keywords'))
    async def handle_keywords_command(event):
        await get_keywords_handler(msg)
        await msg.delete(event.message)  # удаление сообщения команды

    # Обработчик команды /add_keyword для добавления нового ключевого слова
    @client.on(events.NewMessage(chats=target_channel_id, pattern='/add_keyword "(.*)"'))
    async def handle_add_keyword_command(event):
        await add_keyword_handler(client, msg, event)
        await msg.delete(event.message)  # удаление сообщения команды

    # Обработчик команды /remove_keyword для удаления ключевого слова
    @client.on(events.NewMessage(chats=target_channel_id, pattern='/remove_keyword "(.*)"'))
    async def handle_remove_keyword_command(event):
        await remove_keyword_handler(client, msg, event)
        await msg.delete(event.message)  # удаление сообщения команды

    @client.on(events.NewMessage(chats=target_channel_id))
    async def handle_unknown_command(event):
        commands = ['/sources', '/add_source', '/remove_source', '/keywords', '/add_keyword', '/remove_keyword', '/help']

        if not any(event.message.message.startswith(cmd) for cmd in commands):
            await unknown_handler(msg)
            await msg.delete(event.message)  # удаление сообщения команды

    # Обработчик команды /help для отображения справочной информации
    @client.on(events.NewMessage(chats=target_channel_id, pattern='/help'))
    async def handle_help_command(event):
        await help_handler(msg)   
        await msg.delete(event.message)  # удаление сообщения команды
