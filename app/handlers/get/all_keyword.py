from telethon import TelegramClient

from app.functions.read_json import read_json

async def get_keywords_handler(client: TelegramClient, event, target_channel_id: int):
    """Обработчик команды /keywords для получения всех ключевых слов"""
    
    pattern = await read_json(file_path='app/storage/pattern.json')  # чтение шаблона из JSON файла
    keywords = pattern.get('keywords', [])

    if keywords:
        keywords_list = '\n'.join(f'- `{kw}`' for kw in keywords if kw)
        message = f'Список ключевых слов ({len(keywords)}):\n{keywords_list}'

    else:
        message = 'Ключевые слова не заданы.'

    await client.send_message(
        entity=target_channel_id,
        message=message
    )
