from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest

from app.functions.other import link_author
from app.functions.message import Message

async def add_source_handler(client: TelegramClient, msg: Message, event, dialogs):
    """Обработчик команды /add_source для добавления нового источника"""

    try:
        source_link = event.pattern_match.group(1)
        if source_link is None:
            await msg.send(
                message=('Пожалуйста, укажите ссылку на источник после команды.\n'
                        'Пример: /add_source @channel')
            )
            return

        source_link = source_link.strip()
        # Проверка на пустую ссылку
        if source_link == "":
            await msg.send(
                message=('Пожалуйста, укажите ссылку на источник после команды.\n'
                        'Пример: /add_source @channel')
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
                        message=f'Этот источник (@{username}) уже добавлен.'
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
                message=f'Не удалось добавить источник ({source_link}): {e_join}'
            )
            return

        # Добавление канала в папку (если возможно)
        await client.edit_folder(entity, folder=1)

        user = await link_author(client, event.sender_id)  # Получаем информацию о пользователе, добавившем источник

        await msg.send(
            message=f'Пользователь {user} добавил новый источник: @{norm}',
            link_preview=False
        )

    except Exception as e:
        await msg.send(
            message=f'Ошибка при обработке команды /add_source: {e}'
        )
