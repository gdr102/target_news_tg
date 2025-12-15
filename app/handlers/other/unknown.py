from app.functions.message import Message

async def unknown_handler(msg: Message):
    """Обработчик неизвестных команд"""

    await msg.send(
        message='Неизвестная команда. Пожалуйста, используйте /help для получения списка доступных команд.'
    )
