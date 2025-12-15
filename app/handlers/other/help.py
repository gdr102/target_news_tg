from app.functions.message import Message

async def help_handler(msg: Message):
    """Обработчик команды /help для отображения справочной информации"""

    help_message = (
        "Доступные команды:\n"
        "<code>/sources</code> - Получить список всех каналов-источников\n"
        "<code>/add_source</code> @ссылка_на_канал - Добавить новый канал-источник\n"
        "<code>/remove_source</code> @ссылка_на_канал - Удалить канал-источник\n\n"
        "<code>/keywords</code> - Получить список всех ключевых слов\n"
        "<code>/add_keyword \"слово\"</code> - Добавить новое ключевое слово\n"
        "<code>/remove_keyword \"слово\"</code> - Удалить ключевое слово\n\n"
        "<code>/help</code> - Показать это сообщение помощи"
    )

    await msg.send(message=help_message)
