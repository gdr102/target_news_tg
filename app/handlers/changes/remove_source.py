from telethon import TelegramClient
from telethon.tl.functions.channels import LeaveChannelRequest

from app.functions.other import link_author

async def remove_source_handler(client: TelegramClient, event, target_channel_id: int):
    """Обработчик команды /remove_source для удаления источника"""

    try:
        source_link = event.pattern_match.group(1).strip()  # Получаем ссылку на источник из команды

        # Проверка на пустую ссылку
        if source_link == "":
            await client.send_message(
                entity=target_channel_id,
                message=('Пожалуйста, укажите ссылку на источник после команды.\n'
                         'Пример: /remove_source @channel')
            )
            return  # Пустая ссылка, выходим из функции

        # удаления источника (канала) по ссылке
        await client(LeaveChannelRequest(source_link))

        user = await link_author(client, event.sender_id)

        await client.send_message(
            entity=target_channel_id,
            message=f'Пользователь {user} удалил источник: {source_link}',
            parse_mode='html',
            link_preview=False
        )

    except Exception as e:
        print(f'Ошибка при обработке команды /remove_source: {e}')
        await client.send_message(
            entity=target_channel_id,
            message='Произошла ошибка при удалении источника.'
        )
