from app.functions.message import Message
from app.functions.read_json import read_json
from app.functions.other import link_msg_source

async def new_message_hanlder(msg: Message, event):
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
                        target = msg.target_channel_id
                        if event.chat_id == target:
                            await msg.send(message='ℹ️ Источник совпадает с целью, пропускаем.', only_log=True)
                            break

                        # Сообщаем, что обнаружено ключевое слово
                        await msg.send(
                            message=f'🟢 Обнаружено ключевое слово "<code>{keyword}</code>" в сообщении из канала "{event.chat.title}". Пересылаем сообщение...'
                        )

                        # Попытка прямого пересылания
                        await msg.forward(message=message)

                    # Если пересылка не удалась, обрабатываем ошибку
                    except Exception as e:
                        err_text = str(e).lower() # Текст ошибки в нижнем регистре для удобства поиска
                        
                        # Если сообщение из защищённого чата — нельзя пересылать, пробуем отправить копию
                        if ('protected' in err_text and 'forward' in err_text) or 'you can\'t forward' in err_text:
                            try:
                                source = await link_msg_source(event, message.id)

                                # Отправляем только текст
                                await msg.send(
                                    message=f'{message.message}\n\nИсточник: {source} (запрет на копирование контента)' or ''
                                )

                            except Exception as e2: # Ошибка при отправке копии сообщения
                                await msg.send(message=f'❌ Ошибка при отправке копии сообщения: {e2}')

                        else: # Общая ошибка пересылки
                            await msg.send(message=f'❌ Ошибка при пересылке сообщения: {e}')

                    break # Прерываем цикл после первого совпадения

    except Exception as e:
        await msg.send(message=f'❌ Ошибка при обработке сообщения: {e}')
