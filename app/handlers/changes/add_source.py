from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest

from app.functions.other import link_author

async def add_source_handler(client: TelegramClient, event, target_channel_id: int):
    """Обработчик команды /add_source для добавления нового источника"""

    try:
        source_link = event.pattern_match.group(1).strip() # Получаем ссылку на источник из команды
        
        # Проверка на пустую ссылку
        if source_link == "":
            await client.send_message(
                entity=target_channel_id,
                message=('Пожалуйста, укажите ссылку на источник после команды.\n'
                        'Пример: /add_source @channel')
            )

            return # Пустая ссылка, выходим из функции
        
        dialogs = await client.get_dialogs() # Получаем список всех диалогов пользователя

        # Проверка, был ли уже добавлен этот источник
        for dialog in dialogs:
            # Сравниваем username канала с указанной ссылкой
            if dialog.entity.username == source_link.replace('@', ''):
                await client.send_message(
                    entity=target_channel_id,
                    message='Этот источник уже добавлен.'
                )

                return # Источник уже добавлен, выходим из функции

        # добавление нового источника (канала) по ссылке
        await client(JoinChannelRequest(source_link))

        user = await link_author(client, event.sender_id)

        await client.send_message(
            entity=target_channel_id,
            message=f'Пользователь {user} добавил новый источник: {source_link}',
            parse_mode='html',
            link_preview=False
        )

    except Exception as e:
        print(f'Ошибка при обработке команды /add_source: {e}')
        await client.send_message(
            entity=target_channel_id,
            message='Произошла ошибка при добавлении нового источника.'
        )
