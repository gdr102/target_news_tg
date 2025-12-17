from telethon import TelegramClient

from app.functions.message import Message

from app.functions.other import link_author
from app.functions.read_json import read_json
from app.functions.write_json import write_json

async def remove_keyword_handler(client: TelegramClient, msg: Message, event):
	"""Обработчик команды /remove_keyword для удаления ключевого слова"""
	try:
		# Извлечение и нормализация ключевого слова из команды
		raw = event.pattern_match.group(1) if event.pattern_match else None
		if raw is None:
			await msg.send(
				message=(
					'❗ Пожалуйста, укажите ключевое слово после команды. ❗\n\n'
					'Пример: <code>/remove_keyword</code> "слово"'
				)
			)
			return

		keyword = raw.strip() # Убираем внешние пробелы
		
		# Убираем внешние кавычки если есть
		if (keyword.startswith('"') and keyword.endswith('"')) or \
		   (keyword.startswith("'") and keyword.endswith("'")) or \
		   (keyword.startswith("`") and keyword.endswith("`")):
			keyword = keyword[1:-1].strip()

		if keyword == "":
			await msg.send(
				message=(
					'❗ Пожалуйста, укажите ключевое слово после команды. ❗\n\n'
					'Пример: <code>/remove_keyword</code> "слово"'
				)
			)
			return

		pattern = await read_json(file_path='app/storage/pattern.json') or {}
		keywords = pattern.get('keywords', []) or []

		# Поиск ключевого слова регистронезависимо
		lower = keyword.lower()
		match_index = None
		for i, kw in enumerate(keywords):
			if kw.lower() == lower:
				match_index = i
				break

		if match_index is None:
			await msg.send(message=f'ℹ️ Ключевое слово "{keyword}" не найдено в списке.')
			return

		# Удаление найденного ключевого слова и сохранение
		removed = keywords.pop(match_index)
		pattern['keywords'] = keywords
		await write_json(file_path='app/storage/pattern.json', data=pattern)

		user = await link_author(client, event.sender_id)

		await msg.send(
			message=f'✅ Пользователь {user} удалил ключевое слово \"<code>{removed}</code>\"',
			link_preview=False
		)

	except Exception as e:
		await msg.send(message=f'❌ Ошибка при удалении ключевого слова: {e}')
