from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest

from app.functions.other import link_author

from app.facebook.actor import Actor
from app.functions.message import Message
from app.functions.read_json import read_json
from app.functions.write_json import write_json

async def add_source_handler(client: TelegramClient, msg: Message, event, dialogs, actor: Actor):
    """Обработчик команды /add_source для добавления нового источника"""

    try:
        source_link = event.pattern_match.group(1)
        if source_link is None:
            await msg.send(
                message=(
                    '❗ Пожалуйста, укажите ссылку на источник после команды. ❗\n\n'
                    'Пример: <code>/add_source</code> @channel'
                    'или: <code>/add_source</code> https://www.facebook.com/username'
                ),
                link_preview=False
            )
            return

        source_link = source_link.strip()
        # Проверка на пустую ссылку
        if source_link == "":
            await msg.send(
                message=(
                    '❗ Пожалуйста, укажите ссылку на источник после команды. ❗\n\n'
                    'Пример: <code>/add_source</code> @channel'
                    'или: <code>/add_source</code> https://www.facebook.com/username'
                ),
                link_preview=False
            )
            return

        if 'facebook.com/' in source_link.lower():
            await msg.send(
                message='ℹ️ Пожалуйста, подождите, получаю информацию о странице...'
            )

            page_info = await actor.get_info_page(url=source_link)

            page_id = page_info.get('page_id', '')
            page_url = page_info.get('url', '') 
            page_title = page_info.get('name', '')

            # Извлекаем username из URL с учетом разных форматов
            path = page_url.lower().split('facebook.com/')[-1].strip('/')
            path = path.split('?')[0]
            
            # Обрабатываем специальный случай для profile.php и people/
            if 'profile.php?id=' in source_link.lower():
                # Если исходная ссылка была вида profile.php?id=..., используем ID как username
                page_username = page_id
            elif path.startswith('people/'):
                # Для ссылок вида facebook.com/people/name-ID/ используем ID
                # Извлекаем ID из пути (последний сегмент)
                segments = path.split('/')
                if len(segments) > 1:
                    # Берем последний сегмент как ID (если он числовой)
                    last_segment = segments[-1]
                    if last_segment.isdigit():
                        page_username = last_segment
                    else:
                        page_username = page_id  # Используем page_id как fallback
                else:
                    page_username = page_id
            else:
                # Стандартная обработка для обычных страниц
                page_username = path.split('/')[0] if '/' in path else path

            sources_fb = 'app/storage/sources_fb.json'

            try:
                # 1. Читаем существующие данные
                data = await read_json(sources_fb)
                
                # Если файла нет или он пустой, создаем базовую структуру
                if data is None:
                    data = {"sources": {}}
                
                # 2. Проверяем, существует ли уже источник с таким page_id
                if page_id in data.get("sources", {}):
                    await msg.send(
                        message=f'⚠ Этот источник Facebook (ID: {page_id}, <a href=\"{page_url}\">{page_title}</a>) уже добавлен.'
                    )
                    return
                
                # 3. Добавляем новый источник
                data.setdefault("sources", {})[page_id] = {
                    "url": page_username,
                    "title": page_title
                }
                
                # 4. Записываем обновленные данные обратно в файл
                await write_json(sources_fb, data)
                
                # 5. Отправляем подтверждение пользователю
                user = await link_author(client, event.sender_id)
                await msg.send(
                    message=f'✅ Пользователь {user} добавил новый источник Facebook: <a href=\"{page_url}\">{page_title}</a>',
                    link_preview=False
                )
                
            except Exception as e:
                await msg.send(
                    message=f'❌ Ошибка при сохранении источника в файл: {e}'
                )
            
            return


        # Нормализация введённого значения (убираем @ и t.me/ если есть)
        norm = source_link.strip().rstrip('/')
        if norm.startswith('@'): # Если начинается с @, убираем его
            norm = norm[1:]
        elif 't.me/' in norm: # Если содержит t.me/, извлекаем username
            norm = norm.split('/')[-1].split('?')[0]

        norm_lower = norm.lower() # Нормализованное значение в нижнем регистре

        # Проверка, был ли уже добавлен этот источник
        for dialog in dialogs:
            if getattr(dialog.entity, 'broadcast', False): # Только каналы
                username = getattr(dialog.entity, 'username', None) # Получаем username канала
                if username and username.lower() == norm_lower:
                    await msg.send(
                        message=f'⚠ Этот источник (@{username}) уже добавлен.'
                    )

                    return  # Источник уже добавлен, выходим

        # Попытка присоединиться к каналу (поддерживаем и username и прямые ссылки)
        try:
            # если исходная ссылка явно содержит t.me и не похожа на username (например invite), используем её
            if 't.me/' in source_link and ('joinchat' in source_link or source_link.count('/') > 1):
                await client(JoinChannelRequest(source_link)) # Присоединение к каналу по прямой ссылке
                entity = await client.get_entity(source_link) # Получение сущности канала
            else:
                await client(JoinChannelRequest(f'@{norm}')) # Присоединение к каналу по username
                entity = await client.get_entity(f'@{norm}') # Получение сущности канала
        except Exception as e_join:
            await msg.send(
                message=f'❌ Не удалось добавить источник ({source_link}): {e_join}'
            )
            return

        # Добавление канала в папку (если возможно)
        await client.edit_folder(entity, folder=1)

        user = await link_author(client, event.sender_id)  # Получаем информацию о пользователе, добавившем источник

        await msg.send(
            message=f'✅ Пользователь {user} добавил новый источник: @{norm}',
            link_preview=False
        )

    except Exception as e:
        await msg.send(
            message=f'❌ Ошибка при обработке команды /add_source: {e}'
        )
