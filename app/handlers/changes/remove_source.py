from telethon import TelegramClient
from telethon.tl.functions.channels import LeaveChannelRequest

from app.functions.message import Message
from app.functions.other import link_author

async def remove_source_handler(client: TelegramClient, msg: Message, event, dialogs):
    """Обработчик команды /remove_source для удаления источника"""

    try:
        source_link = event.pattern_match.group(1)
        
        if source_link is None:
            await msg.send(
                message=('Пожалуйста, укажите ссылку на источник после команды.\n'
                         'Пример: /remove_source @channel')
            )
            return

        source_link = source_link.strip()
        # Проверка на пустую ссылку
        if source_link == "":
            await msg.send(
                message=('Пожалуйста, укажите ссылку на источник после команды.\n'
                         'Пример: /remove_source @channel')
            )
            return

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
                message=f'Источник ({source_link}) не найден.'
            )
            return

        # Удаляем(отписываемся от) найденного канала
        await client(LeaveChannelRequest(matched_dialog.entity))

        user = await link_author(client, event.sender_id)

        await msg.send(
            message=f'Пользователь {user} удалил источник: @{norm}',
            link_preview=False
        )

    except Exception as e:
        await msg.send(
            message=f'Ошибка при обработке команды /remove_source: {e}'
        )
