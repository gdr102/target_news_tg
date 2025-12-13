async def link_author(client, user_id: int) -> str:
    """Функция для получения ссылки на профиль пользователя по его user_id"""

    user = await client.get_entity(user_id)

    if user.username is not None:
        return f"<a href=\"https://t.me/{user.username}\">{user.first_name}</a>"
    else:
        return f"<a href=\"tg://user?id={user.id}\">{user.first_name}</a>"
    
async def delete_author_message(client, event):
    """Функция для удаления сообщения автора команды"""

    message = event.message # получение сообщения команды
    await client.delete_messages(entity=message.chat_id, message_ids=message.id) # удаление сообщения команды
    