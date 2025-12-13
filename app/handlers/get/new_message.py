from telethon import TelegramClient

from app.functions.read_json import read_json

async def new_message_hanlder(client: TelegramClient, event, target_channel_id: int):
    """ Обработчик входящих сообщений из каналов"""
    
    try:
        # Проверяем, что сообщения из канала
        if not hasattr(event.chat, 'broadcast') or not event.chat.broadcast:
            return
        
        pattern = await read_json(file_path='app/storage/pattern.json') # чтение шаблона из JSON файла
        message = event.message # получение сообщения
        text = message.message or "" # получение текста сообщения, пустая строка если None

        # Проверка ключевых слов в сообщении
        if text or message.media:
            # Ищем ключевые слова из шаблона (регистр не важен)
            for keyword in pattern['keywords']:
                # Пропускаем пустые ключевые слова
                if not keyword:
                    continue

                # Проверка наличия ключевого слова в тексте (регистр не важен)
                if keyword.lower() in text.lower():
                    try:
                        # Не пересылаем в тот же канал
                        target = target_channel_id
                        if event.chat_id == target:
                            print("Источник совпадает с целью, пропускаем.")
                            break

                        print(f"Найдено ключевое слово '{keyword}' в тексте поста канала '{getattr(event.chat, 'title', event.chat_id)}'. Пересылаем сообщение...")

                        # Попытка прямого пересылания
                        await client.forward_messages(entity=target, messages=message)

                    # Если пересылка не удалась, обрабатываем ошибку
                    except Exception as e:
                        err_text = str(e).lower() # Текст ошибки в нижнем регистре для удобства поиска
                        
                        # Если сообщение из защищённого чата — нельзя пересылать, пробуем отправить копию
                        if ('protected' in err_text and 'forward' in err_text) or 'you can\'t forward' in err_text:
                            try:
                                source = f"{event.chat.title}"
                                chat_id = str(event.chat_id).replace('-100', '')

                                if event.chat.username is None:
                                    source = f"<a href=\"https://t.me/c/{chat_id}/{message.id}\">{event.chat.title}</a> - приватный канал"
                                else:
                                    source = f"<a href=\"https://t.me/{event.chat.username}/{message.id}\">{event.chat.title}</a> - открытый канал"

                                # Отправляем только текст
                                await client.send_message(
                                    entity=target,
                                    message=f"{message.message}\n\nИсточник: {source} (запрет на копирование контента)" or "",
                                    parse_mode='html'
                                )
                                print("Сообщение защищено — отправлено копией текста.")

                            except Exception as e2: # Обработка ошибки при отправке копии
                                print(f"Ошибка при отправке копии сообщения: {e2}")

                        else: # Общая ошибка пересылки
                            print(f"Ошибка при пересылке сообщения: {e}")

                    break # Прерываем цикл после первого совпадения

    except Exception as e:
        print(f"Ошибка при обработке сообщения: {e}")
