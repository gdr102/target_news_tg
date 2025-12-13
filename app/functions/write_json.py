import json

async def write_json(file_path, data):
    """Функция для записи данных в JSON файл"""

    # Запись данных в JSON файл
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4) # Запись данных в файл с отступами для читаемости
