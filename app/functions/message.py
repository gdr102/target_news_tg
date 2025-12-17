from telethon import TelegramClient
from telethon.functions import messages

class Message():
    def __init__(self, client: TelegramClient, target_channel_id: int, topics: list):
        self.client = client
        self.topics = topics
        self.target_channel_id = target_channel_id

    async def send(self, message: str, only_log: bool = False, link_preview: bool = True, topic = None):
        """ Функция для отправки сообщений в целевой канал """

        print(f'Отправка сообщения в канал {self.target_channel_id}...'
                f'\nСообщение: {message}')
        
        # Отправка сообщения, если не только логирование
        if not only_log:
            await self.client.send_message(
                entity=self.target_channel_id,
                message=message,
                parse_mode='html',
                link_preview=link_preview,
                reply_to=topic
            )
    
    async def forward(self, event, topic):
        """ Функция для пересылки сообщений в целевой канал """

        message_id = event.id
        source_chat = event.chat_id

        await self.client(messages.ForwardMessagesRequest(
            from_peer=source_chat, 
            id=[message_id], 
            to_peer=self.target_channel_id, 
            top_msg_id=topic,
        ))

    async def delete(self, message):
        """ Функция для удаления сообщения в целевом канале """

        await self.client.delete_messages(
            entity=self.target_channel_id,
            message_ids=message
        )
