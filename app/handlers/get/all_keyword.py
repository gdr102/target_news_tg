from app.functions.message import Message
from app.functions.read_json import read_json

async def get_keywords_handler(msg: Message):
    """Обработчик команды /keywords для получения всех ключевых слов"""
    
    pattern = await read_json(file_path='app/storage/pattern.json')  # чтение шаблона из JSON файла
    keywords = pattern.get('keywords', [])

    if keywords:
        keywords_list = '\n'.join(f'- <code>{kw}</code>' for kw in keywords if kw)
        message = f'Список ключевых слов ({len(keywords)}):\n{keywords_list}'

    else:
        message = 'Ключевые слова не заданы.'

    await msg.send(message=message)
