from telethon import TelegramClient

async def help_handler(client: TelegramClient, target_channel_id: int):
    """Обработчик команды /help для отображения справочной информации"""

    help_message = (
        "Доступные команды:\n"
        "`/sources` - Получить список всех каналов-источников\n"
        "`/add_source` <@ссылка_на_канал> - Добавить новый канал-источник\n"
        "`/remove_source` <@ссылка_на_канал> - Удалить канал-источник\n"
        "`/keywords` - Получить список всех ключевых слов\n"
        "`/add_keyword \"слово\"` - Добавить новое ключевое слово\n"
        "`/remove_keyword \"слово\"` - Удалить ключевое слово\n"
        "`/help` - Показать это сообщение помощи"
    )

    await client.send_message(
        entity=target_channel_id,
        message=help_message
    )
