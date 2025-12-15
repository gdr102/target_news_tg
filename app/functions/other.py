async def link_author(client, user_id: int) -> str:
    """Функция для получения ссылки на профиль пользователя по его user_id"""

    user = await client.get_entity(user_id) # получение информации о пользователе

    # Формируем ссылку на профиль пользователя
    if user.username is not None:
        return f'<a href=\"https://t.me/{user.username}\">{user.first_name}</a>'
    else:
        return f'<a href=\"tg://user?id={user.id}\">{user.first_name}</a>'
    
async def link_msg_source(event, message_id: int) -> str:
    """Функция для получения ссылки на сообщение в канале по chat_id и message_id"""

    # Формируем ссылку на сообщение
    if event.chat.username is None:
        return f'<a href=\"https://t.me/{event.chat.username}/{message_id}\">{event.chat.title}</a>'
    else:
        chat_id_str = str(event.chat_id).replace('-100', '') # удаление префикса -100 для приватных каналов
        return f'<a href=\"https://t.me/c/{chat_id_str}/{message_id}\">{event.chat.title}</a>'
    