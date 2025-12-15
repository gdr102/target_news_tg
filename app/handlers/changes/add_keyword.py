from telethon import TelegramClient
from app.functions.message import Message

from app.functions.other import link_author
from app.functions.read_json import read_json
from app.functions.write_json import write_json

async def add_keyword_handler(client: TelegramClient, msg: Message, event):
    """Обработчик команды /add_keyword для добавления нового ключевого слова"""

    try:
        raw = event.pattern_match.group(1) if event.pattern_match else None
        if raw is None:
            await msg.send(
                message=('Пожалуйста, укажите ключевое слово после команды.\n'
                         'Пример: /add_keyword "слово"')
            )
            return

        # Нормализация: убираем внешние пробелы и кавычки (", ', `)
        keyword = raw.strip()
        if (keyword.startswith('"') and keyword.endswith('"')) or \
           (keyword.startswith("'") and keyword.endswith("'")) or \
           (keyword.startswith("`") and keyword.endswith("`")):
            keyword = keyword[1:-1].strip()

        # Проверка на пустое ключевое слово
        if keyword == "":
            await msg.send(
                message=('Пожалуйста, укажите ключевое слово после команды.\n'
                         'Пример: /add_keyword "слово"')
            )
            return

        pattern = await read_json(file_path='app/storage/pattern.json') or {} # Чтение текущих данных
        keywords = pattern.get('keywords', []) or [] # Получение списка ключевых слов

        # Проверка на дубликат (регистронезависимо)
        lower = keyword.lower()
        for kw in keywords: # Проверка существующих ключевых слов
            if kw.lower() == lower:
                await msg.send(
                    message=f'Ключевое слово "{keyword}" уже существует.'
                )
                return

        # Добавляем новое ключевое слово и сохраняем
        keywords.append(keyword) # Добавление нового ключевого слова
        pattern['keywords'] = keywords # Обновление данных
        await write_json(file_path='app/storage/pattern.json', data=pattern) # Сохранение обновленных данных

        user = await link_author(client, event.sender_id) # Получение информации об авторе команды

        await msg.send(
            message=f'Пользователь {user} добавил новое ключевое слово: "<code>{keyword}</code>"',
            link_preview=False
        )

    except Exception as e:
        await msg.send(
            message=f'Ошибка при обработке команды /add_keyword: {e}'
        )
