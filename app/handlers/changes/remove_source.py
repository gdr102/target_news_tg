from telethon import TelegramClient
from telethon.tl.functions.channels import LeaveChannelRequest

from app.functions.message import Message
from app.functions.other import link_author
from app.functions.read_json import read_json
from app.functions.write_json import write_json

async def remove_source_handler(client: TelegramClient, msg: Message, event, dialogs):
    """Обработчик команды /remove_source для удаления источника"""

    try:
        source_link = event.pattern_match.group(1)
        
        if source_link is None:
            await msg.send(
                message=(
                    '❗ Пожалуйста, укажите ссылку на источник после команды. ❗\n'
                    'Пример: <code>/remove_source</code> @channel'
                    'или: <code>/remove_source</code> https://www.facebook.com/username'
                ),
                link_preview=False
            )
            return

        source_link = source_link.strip()
        # Проверка на пустую ссылку
        if source_link == "":
            await msg.send(
                message=(
                    '❗ Пожалуйста, укажите ссылку на источник после команды. ❗\n'
                    'Пример: <code>/remove_source</code> @channel'
                    'или: <code>/remove_source</code> https://www.facebook.com/username'
                ),
                link_preview=False
            )
            return
        
        # --- Обработка Facebook-источников ---
        if 'facebook.com/' in source_link.lower():
            JSON_FILE_PATH = 'app/storage/sources_fb.json'
            
            try:
                # 1. Читаем данные из файла
                data = await read_json(JSON_FILE_PATH)
                if data is None or "sources" not in data:
                    await msg.send(
                        message='❌ Файл с источниками Facebook не найден или пуст.'
                    )
                    return
                
                # 2. Извлекаем идентификатор из ссылки
                source_to_remove = None
                page_id_to_remove = None
                
                # Проверяем разные форматы ссылок
                if 'profile.php?id=' in source_link.lower():
                    # Извлекаем ID из profile.php?id=...
                    import re
                    match = re.search(r'id=(\d+)', source_link)
                    if match:
                        page_id_to_remove = match.group(1)
                elif 'facebook.com/' in source_link:
                    # Для обычных ссылок ищем по username
                    path = source_link.lower().split('facebook.com/')[-1].strip('/').split('?')[0]
                    username_to_find = path.split('/')[0]
                    
                    # Ищем источник по username в данных
                    for page_id, source_data in data["sources"].items():
                        source_url = source_data.get("url", "")
                        # Проверяем разные форматы хранения URL
                        if username_to_find in source_url:
                            source_to_remove = page_id
                            
                            break
                
                # Если не нашли по username, пробуем найти по полному URL
                if not source_to_remove and not page_id_to_remove:
                    for page_id, source_data in data["sources"].items():
                        if source_link.lower() in source_data.get("url", "").lower():
                            source_to_remove = page_id
                            
                            break
                
                # Если нашли по profile.php, ищем в данных
                if page_id_to_remove and page_id_to_remove in data["sources"]:
                    source_to_remove = page_id_to_remove
                
                # 3. Если источник не найден
                if not source_to_remove:
                    await msg.send(
                        message=f'❌ Источник Facebook ({source_link}) не найден.'
                    )
                    return
                
                # 4. Удаляем источник
                removed_title = data["sources"][source_to_remove].get("title", "Без названия")
                del data["sources"][source_to_remove]
                
                # 5. Сохраняем обновленные данные
                await write_json(JSON_FILE_PATH, data)
                
                # 6. Отправляем подтверждение
                user = await link_author(client, event.sender_id)
                await msg.send(
                    message=f'✅ Пользователь {user} удалил источник Facebook: {removed_title}',
                    link_preview=False
                )
                
            except Exception as e:
                await msg.send(
                    message=f'❌ Ошибка при удалении Facebook-источника: {e}'
                )
            
            return  # Завершаем обработку для Facebook

        # Нормализация введённого значения (убираем @ и t.me/ если есть)
        norm = source_link.strip().rstrip('/')
        if norm.startswith('@'):
            norm = norm[1:]
        elif 't.me/' in norm:
            norm = norm.split('/')[-1].split('?')[0]

        norm_lower = norm.lower()

        # Поиск соответствующего канала в dialogs
        matched_dialog = None
        for dialog in dialogs:
            if getattr(dialog.entity, 'broadcast', False):
                username = getattr(dialog.entity, 'username', None)
                if username and username.lower() == norm_lower:
                    matched_dialog = dialog
                    break

        # Если канал не найден — сообщаем об этом
        if not matched_dialog:
            await msg.send(
                message=f'ℹ️ Источник ({source_link}) не найден.'
            )
            return

        # Удаляем(отписываемся от) найденного канала
        await client(LeaveChannelRequest(matched_dialog.entity))

        user = await link_author(client, event.sender_id)

        await msg.send(
            message=f'✅ Пользователь {user} удалил источник: @{norm}',
            link_preview=False
        )

    except Exception as e:
        await msg.send(
            message=f'❌ Ошибка при обработке команды /remove_source: {e}'
        )
