from telethon import TelegramClient

class Message():
    def __init__(self, client: TelegramClient, target_channel_id: int):
        self.client = client
        self.target_channel_id = target_channel_id

    async def send(self, message: str, only_log: bool = False, link_preview: bool = True):
        """ Функция для отправки сообщений в целевой канал """

        print(f'Отправка сообщения в канал {self.target_channel_id}...'
                f'\nСообщение: {message}')
        
        # Отправка сообщения, если не только логирование
        if not only_log:
            await self.client.send_message(
                entity=self.target_channel_id,
                message=message,
                parse_mode='html',
                link_preview=link_preview
            )
    
    async def forward(self, message):
        """ Функция для пересылки сообщений в целевой канал """

        await self.client.forward_messages(
            entity=self.target_channel_id,
            messages=message
        )
    
    async def delete(self, message):
        """ Функция для удаления сообщения в целевом канале """

        await self.client.delete_messages(
            entity=self.target_channel_id,
            message_ids=message
        )
