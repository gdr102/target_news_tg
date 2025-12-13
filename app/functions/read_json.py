import json

async def read_json(file_path):
    """Функция для чтения данных из JSON файла"""
    
    try:
        # Открытие и чтение JSON файла
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file) # Загрузка данных из файла

        return data # Возврат прочитанных данных
    
    except FileNotFoundError:
        print(f"Файл не найден: {file_path}")
        return None
    
    except json.JSONDecodeError:
        print(f"Ошибка декодирования JSON в файле: {file_path}")
        return None
    
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return None