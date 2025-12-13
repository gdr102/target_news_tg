from telethon import TelegramClient

from app.functions.other import link_author
from app.functions.read_json import read_json
from app.functions.write_json import write_json

async def add_keyword_handler(client, event, target_channel_id):
    """Обработчик команды /add_keyword для добавления нового ключевого слова"""

    try:
        keyword = event.pattern_match.group(1).strip()  # Получаем ключевое слово из команды

        # Проверка на пустое ключевое слово
        if keyword == "":
            await client.send_message(
                entity=target_channel_id,
                message=('Пожалуйста, укажите ключевое слово после команды.\n'
                         'Пример: /add_keyword \"слово\"')
            )

            return  # Пустое ключевое слово, выходим из функции

        pattern = await read_json(file_path='app/storage/pattern.json')  # чтение шаблона из JSON файла
        keywords = pattern.get('keywords', [])

        for kw in keywords:
            if kw.lower() == keyword.lower():
                await client.send_message(
                    entity=target_channel_id,
                    message=f'Ключевое слово \"{keyword}\" уже существует.'
                )

                return  # Ключевое слово уже существует, выходим из функции
        
        keywords.append(keyword)  # Добавляем новое ключевое слово в список
        pattern['keywords'] = keywords  # Обновляем словарь с ключевыми словами

        await write_json(file_path='app/storage/pattern.json', data=pattern) # Сохраняем обновленный шаблон обратно в JSON файл

        user = await link_author(client, event.sender_id)

        await client.send_message(
            entity=target_channel_id,
            message=f'Пользователь {user} добавил новое ключевое слово: \"<code>{keyword}</code>\"',
            parse_mode='html',
            link_preview=False
        )

    except Exception as e:
        print(f'Ошибка при обработке команды /add_keyword: {e}')
        await client.send_message(
            entity=target_channel_id,
            message='Произошла ошибка при добавлении нового ключевого слова.'
        )
