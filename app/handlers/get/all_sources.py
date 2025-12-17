from app.functions.message import Message
from app.functions.read_json import read_json

async def get_sources_handler(msg: Message, dialogs):
    """Обработчик команды /sources для получения списка всех источников"""

    try:
        telegram_sources = []  # Список для хранения информации о Telegram каналах
        facebook_sources = []   # Список для хранения информации о Facebook страницах

        # --- Telegram источники ---
        for dialog in dialogs:
            # Более точная проверка на канал/супергруппу
            if hasattr(dialog.entity, 'broadcast') and dialog.entity.broadcast:
                channel_id = dialog.entity.id  # ID канала
                username = f"@{dialog.entity.username}" if dialog.entity.username else f'https://t.me/c/{channel_id}'  # Юзернейм или ссылка на канал

                # Сохраняем информацию о канале
                telegram_sources.append({
                    'title': dialog.title,
                    'entity': dialog.entity,
                    'username': username,
                    'type': 'telegram'
                })

        # --- Facebook источники ---
        try:
            sources_fb = 'app/storage/sources_fb.json'
            data = await read_json(sources_fb)
            
            if data and 'sources' in data:
                for page_id, source_data in data["sources"].items():
                    title = source_data.get('title', 'Без названия')
                    url = source_data.get('url', '')
                    
                    # Формируем отображаемую ссылку
                    if url.startswith('https://'):
                        # Если это полный URL, оставляем как есть
                        display_url = url
                    elif 'profile.php?id=' in url:
                        # Для profile.php ссылок
                        profile_id = url.split('=')[-1]
                        display_url = f'https://facebook.com/{profile_id}'
                    else:
                        # Для username
                        display_url = f'https://facebook.com/{url}'
                    
                    facebook_sources.append({
                        'title': title,
                        'username': display_url,
                        'type': 'facebook'
                    })
        except Exception as e:
            print(f'Ошибка при чтении Facebook источников: {e}')
            # Продолжаем выполнение даже если Facebook источники не загрузились

        # --- Формируем итоговое сообщение ---
        message_lines = []
        
        if telegram_sources:
            message_lines.append(f'📢 <b>Telegram источники ({len(telegram_sources)}):</b>')
            for i, source in enumerate(telegram_sources, 1):
                message_lines.append(f'{i}. {source["title"]} ({source["username"]})')
            message_lines.append("")  # Пустая строка между разделами
        
        if facebook_sources:
            message_lines.append(f'📘 <b>Facebook источники ({len(facebook_sources)}):</b>')
            for j, source in enumerate(facebook_sources, 1):
                message_lines.append(f'{j}. <a href="{source["username"]}">{source["title"]}</a>')
        
        # Если источников нет вообще
        if not telegram_sources and not facebook_sources:
            message_lines.append('❌ Нет отслеживаемых источников.')
        
        # Итоговый счетчик
        total_count = len(telegram_sources) + len(facebook_sources)
        if total_count > 0:
            summary = f'\n\n📊 Всего источников: {total_count} (Telegram: {len(telegram_sources)}, Facebook: {len(facebook_sources)})'
        else:
            summary = ''
        
        # Отправляем сообщение
        await msg.send(
            message='\n'.join(message_lines) + summary,
            link_preview=False
        )

    except Exception as e:
        await msg.send(
            message=f'❌ Произошла ошибка при получении списка источников: {e}'
        )
