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
    
async def check_message_topic(event, msg):
    message = event.message
    command = event.pattern_match.group(0)
    
    if message.reply_to and message.reply_to.forum_topic:
        await msg.delete(event.message)
        
        if command == '/check_fb':
            topic_fb = msg.topics.get('fb', '') # ID темы фейсбук

            if int(message.reply_to.reply_to_msg_id) == int(topic_fb):
                return True

        return False
    else:
        if command == '/check_fb':
            await msg.delete(event.message)
            return False
        
    return True

