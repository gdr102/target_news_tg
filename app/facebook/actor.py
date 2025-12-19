import pytz
import asyncio

from typing import Dict
from apify_client import ApifyClient
from datetime import datetime, timedelta

from app.functions.message import Message
from app.functions.read_json import read_json
from app.functions.write_json import write_json

class Actor():
    def __init__(self, api_token: str, msg: Message, topics: Dict, interval: int = 3600):
        self.client = ApifyClient(api_token)
        self.msg = msg
        self.posts = {}
        self.maxPosts = 1
        self.sources = None
        self.topics = topics
        self.interval = interval

    # запуск
    async def run(self):
        run_input = await self.get_sources() 
        posts = await self.facebook_scraper(run_input=run_input)
        await self.handle_posts(posts)

    # Парсинг постов
    async def facebook_scraper(self, run_input) -> Dict:
        run = self.client.actor('scraper_one/facebook-posts-scraper').call(run_input=run_input)

        dataset = self.client.dataset(run["defaultDatasetId"])

        for item in dataset.iterate_items():
            postId = item.get('postId', '')

            postData = {
                'text': item.get('postText', ''),
                'page_id': item.get('pageId', ''),
                'post_url': item.get('url', '')
            }
            
            self.posts[postId] = postData # {"postId": {"text": "text text text", "page_id": "61553769081208", "post_url": "https://link.link/postId"}}

        return self.posts
    
    # получение списка источников и преобразование в правильный словарь для отправки запроса
    async def get_sources(self) -> Dict:
        input_data = []
        run_input = {}

        sources_fb = await read_json(file_path='app/storage/sources_fb.json')
        self.sources = sources_fb.get('sources', {})

        for page_id, value in self.sources.items():
            url = value.get('url', '')
            title = value.get('title', '')
            
            # Определяем тип URL и формируем правильную ссылку
            if url.startswith('profile_'):
                # Для профилей вида profile_100083010146725
                page_id_num = url.replace('profile_', '')
                fb_url = f'https://www.facebook.com/profile.php?id={page_id_num}'
            elif url.startswith('people_'):
                # Для people страниц вида people_100083010146725
                page_id_num = url.replace('people_', '')
                fb_url = f'https://www.facebook.com/people/{title.replace(" ", "-")}/{page_id_num}/'
            elif url.isdigit():
                # Если URL состоит только из цифр (ID)
                fb_url = f'https://www.facebook.com/profile.php?id={url}'
            else:
                # Стандартные страницы с username
                fb_url = f'https://www.facebook.com/{url}'

            input_data.append(fb_url)

        run_input["pageUrls"] = input_data
        run_input["resultsLimit"] = self.maxPosts

        return run_input

    async def handle_posts(self, posts: Dict) -> str:
        topic = int(self.topics.get('fb', ''))

        # Читаем существующие посты из JSON
        data_posts = await read_json(file_path='app/storage/posts.json')
        existing_posts = data_posts.get('posts', {})
        
        # Читаем ключевые слова из pattern.json
        pattern = await read_json(file_path='app/storage/pattern.json')
        keywords = pattern.get('keywords', [])
        
        # Статистика
        checked_sources = set()
        sent_posts_count = 0
        detected_keywords = set()
        
        # posts - это новые посты от facebook_scraper
        for post_id, post_data in posts.items():
            text = post_data.get('text', '')
            page_id = post_data.get('page_id', '')
            post_url = post_data.get('post_url', '')
            
            # Получаем информацию об источнике
            source = self.sources.get(page_id)
            if not source:
                print(f'Источник для page_id {page_id} не найден в источниках')
                continue
                
            source_url = source.get('url', '')
            source_title = source.get('title', '')
            
            # Добавляем источник в статистику
            checked_sources.add(page_id)
            
            # Проверяем, есть ли уже такой пост в базе
            if post_id in existing_posts:
                print(f'Пост {post_id} существует!')
                
                post_info = existing_posts[post_id]
                
                # Если пост уже отправлен - пропускаем
                if post_info.get('is_send', 0) == 1:
                    print(f'Пост {post_id} уже отправлен, пропускаю...')
                    continue
                
                # Если пост не был отправлен, проверяем причину
                if post_info.get('no_keyword', 0) == 1:
                    print(f'Пост {post_id} имеет флаг no_keyword, равный 1, проверяю еще раз...')
                    
                    # Проверяем наличие ключевых слов снова
                    found_keyword = None
                    for keyword in keywords:
                        if not keyword:
                            continue
                        
                        if keyword.lower() in text.lower():
                            found_keyword = keyword
                            break
                    
                    # Если все еще нет ключевого слова - пропускаем
                    if not found_keyword:
                        print(f'Пост {post_id} не имеет ключевых слов, пропускаю...')
                        continue
                    else:
                        print(f'Пост {post_id} имеет ключевое слово "{found_keyword}"!')
                        # Сбрасываем флаг no_keyword для последующей обработки
                        post_info['no_keyword'] = 0
            
            # Ищем ключевые слова в тексте поста
            found_keyword = None
            for keyword in keywords:
                if not keyword:
                    continue
                
                if keyword.lower() in text.lower():
                    found_keyword = keyword
                    break
            
            # Если ключевое слово найдено - отправляем
            if found_keyword:
                # Добавляем ключевое слово в статистику
                detected_keywords.add(found_keyword)

                # Формируем сообщение для отправки
                await self.msg.send(message = 
                    f'🟢 Обнаружено ключевое слово "<code>{found_keyword}</code>"\n\n'
                    f'<b>{source_title}</b>\n\n'
                    f'Оригинальный пост: <a href="{post_url}">link</a>\n\n'
                    f'<blockquote expandable>{text}</blockquote>\n\n'
                    f'Источник: <a href="https://facebook.com/{source_url}">{source_title}</a>',
                    topic=topic
                )

                await asyncio.sleep(2)
                
                # Обновляем информацию о посте в базе
                existing_posts[post_id] = {
                    'keyword': found_keyword,
                    'sourceTitle': source_title,
                    'postUrl': post_url,
                    'is_send': 1,  # Помечаем как отправленный
                    'no_keyword': 0  # Сбрасываем флаг отсутствия ключевого слова
                }
                
                # Увеличиваем счетчик отправленных постов
                sent_posts_count += 1
                
            else:
                # Если ключевых слов не найдено
                print(f'No keywords found in post {post_id}')
                
                # Если пост уже существует, обновляем флаг no_keyword
                if post_id in existing_posts:
                    existing_posts[post_id]['no_keyword'] = 1
                    existing_posts[post_id]['is_send'] = 0
                else:
                    # Добавляем новый пост с флагом no_keyword
                    existing_posts[post_id] = {
                        'keyword': '',
                        'sourceTitle': source_title,
                        'postUrl': post_url,
                        'is_send': 0,  # Не отправлен
                        'no_keyword': 1  # Нет ключевых слов
                    }
        
        # Сохраняем обновленные данные обратно в JSON
        data_posts['posts'] = existing_posts
        await write_json('app/storage/posts.json', data_posts)
        
        # Текущее время (можно настроить под ваш часовой пояс)
        tz = pytz.timezone('Europe/Moscow')  # Украинское время, можно изменить
        now = datetime.now(tz)
        
        # Добавляем интервал для получения времени следующей проверки
        next_check_time = now + timedelta(seconds=self.interval)
        
        # Форматируем в ЧЧ:ММ
        next_check_str = next_check_time.strftime("%H:%M")
        
        # Формируем и отправляем статистику
        stats_message = (
            f"📊 <b>Статистика обработки постов:</b>\n"
            f"• Проверено источников: {len(checked_sources)}\n"
            f"• Отправлено постов: {sent_posts_count}\n"
            f"• Ключевые слова: {', '.join(sorted(detected_keywords)) if detected_keywords else 'не обнаружены'}\n"
            f"• Следующая проверка в <code>{next_check_str}</code>"
        )
        
        await self.msg.send(message=stats_message, topic=topic)

    async def get_info_page(self, url):
        run_input = {
            "urls": [url]
        }

        run = self.client.actor('cleansyntax/facebook-pages-scraper').call(run_input=run_input)

        dataset = self.client.dataset(run["defaultDatasetId"])

        for item in dataset.iterate_items():
            return item
