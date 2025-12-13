from telethon import TelegramClient

async def get_sources_handler(client: TelegramClient, event, target_channel_id: int):
    """Обработчик команды /sources для получения списка источников"""

    try:
        dialogs = await client.get_dialogs() # Получаем все диалоги
        channels = {} # Словарь для хранения информации о каналах

        for dialog in dialogs:
            # Более точная проверка на канал/супергруппу
            if hasattr(dialog.entity, 'broadcast') and dialog.entity.broadcast:
                channel_id = dialog.entity.id # ID канала
                username = f"@{dialog.entity.username}" if dialog.entity.username else f'https://t.me/c/{channel_id}' # Юзернейм или ссылка на канал

                # Сохраняем информацию о канале
                channels[channel_id] = {
                    'title': dialog.title,
                    'entity': dialog.entity,
                    'username': username
                }

        # Отправляем список каналов в целевой чат
        await client.send_message(
            entity=target_channel_id,
            message=f"Список отслеживаемых источников ({len(channels)}):\n" +
                    "\n".join([f"{i+1}. {info['title']} ({info['username']})" for i, info in enumerate(channels.values())]) or 'Нет отслеживаемых каналов.'
        )

    except Exception as e:
        print(f'Ошибка при обработке команды /sources: {e}')
        await client.send_message(
            entity=target_channel_id,
            message='Произошла ошибка при получении списка источников.'
        )
