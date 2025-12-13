from telethon import TelegramClient

from app.functions.read_json import read_json
from app.functions.write_json import write_json

async def remove_keyword_handler(client: TelegramClient, event, target_channel_id: int):
    """Обработчик команды /remove_keyword для удаления ключевого слова"""
    try:
        # Извлечение ключевого слова из команды
        keyword = event.pattern_match.group(1).strip()

        pattern = await read_json(file_path='app/storage/pattern.json')  # чтение шаблона из JSON файла
        keywords = pattern.get('keywords', []) # получение текущего списка ключевых слов

        if keyword not in keywords:
            await client.send_message(
                target_channel_id,
                f'Ключевое слово "{keyword}" не найдено в списке.'
            )
            return
        
        # Удаление ключевого слова из списка
        keywords.remove(keyword)
        pattern['keywords'] = keywords
        # Сохранение обновленного шаблона обратно в JSON файл
        await write_json(file_path='app/storage/pattern.json', data=pattern)

        # Отправка подтверждения пользователю
        await client.send_message(
            target_channel_id,
            f'Ключевое слово "{keyword}" успешно удалено.'
        )
    except Exception as e:
        # Обработка ошибок и отправка сообщения об ошибке
        await client.send_message(
            target_channel_id,
            f'Ошибка при удалении ключевого слова: {e}'
        )
