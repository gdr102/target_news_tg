from app.functions.read_json import read_json

async def get_new_message(client, events, target_channel_id):
    """ Обработчик входящих сообщений из каналов"""
    
    @client.on(events.NewMessage(incoming=True))
    async def handle_new_message(event):
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

                            source = getattr(event.chat, 'username', event.chat_id) # Получаем юзернейм или ID источника
                            
                            # Если сообщение из защищённого чата — нельзя пересылать, пробуем отправить копию
                            if ('protected' in err_text and 'forward' in err_text) or 'you can\'t forward' in err_text:
                                try:
                                    # Отправляем только текст
                                    await client.send_message(
                                        entity=target,
                                        message=f"{message.message}\n\nИсточник: @{source}" or ""
                                    )
                                    print("Сообщение защищено — отправлено копией текста.")

                                except Exception as e2: # Обработка ошибки при отправке копии
                                    print(f"Ошибка при отправке копии сообщения: {e2}")

                            else: # Общая ошибка пересылки
                                print(f"Ошибка при пересылке сообщения: {e}")

                        break # Прерываем цикл после первого совпадения

        except Exception as e:
            print(f"Ошибка при обработке сообщения: {e}")
