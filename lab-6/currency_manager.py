from flask import Flask, request, jsonify 
import sqlite3 

app = Flask(__name__)  # Создаём экземпляр приложения Flask
DB_PATH = 'currencies.db'  # Путь к базе данных

# Функция для создания таблицы, если её нет
def init_db():
    with sqlite3.connect(DB_PATH) as conn:  # Открываем соединение с базой
        conn.execute('''
            CREATE TABLE IF NOT EXISTS currencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                currency_name VARCHAR UNIQUE,
                rate NUMERIC
            )
        ''')  # Выполняем SQL-команду

@app.route('/load', methods=['POST'])  # Регистрируем обработчик POST-запроса на адрес /load
def load_currency():
    data = request.get_json()  # Получаем JSON-данные из тела запроса
    name = data.get('currency_name')  # Извлекаем имя валюты
    rate = data.get('rate')  # Извлекаем курс валюты к рублю

    # Проверка: если не передано имя валюты или курс
    if not name or rate is None:
        return jsonify({'error': 'Missing currency_name or rate'}), 400  # Возвращаем ошибку 400

    try:
        # Открываем соединение с базой данных
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()  # Создаём курсор для выполнения SQL-запросов

            # Проверяем, есть ли уже такая валюта в базе
            cursor.execute('SELECT id FROM currencies WHERE currency_name = ?', (name,))
            if cursor.fetchone():  # Если такая валюта найдена
                return jsonify({'message': 'Currency already exists'}), 400  # Возвращаем ошибку

            # Если валюты нет — добавляем её в таблицу
            cursor.execute('INSERT INTO currencies (currency_name, rate) VALUES (?, ?)', (name, rate))
            conn.commit()  # Подтверждаем изменения в базе

        # Возвращаем успешный ответ
        return jsonify({'message': 'Currency added successfully'}), 200

    except Exception as e:
        # Если произошла ошибка, возвращаем её описание
        return jsonify({'error': str(e)}), 500
    
@app.route('/update_currency', methods=['POST'])  # Регистрируем новый POST-эндпоинт
def update_currency():
    data = request.get_json()  # Получаем JSON-данные из запроса
    name = data.get('currency_name')  # Название валюты
    new_rate = data.get('rate')  # Новый курс валюты

    # Проверка наличия данных
    if not name or new_rate is None:
        return jsonify({'error': 'Missing currency_name or rate'}), 400

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            # Проверяем, существует ли валюта
            cursor.execute('SELECT id FROM currencies WHERE currency_name = ?', (name,))
            if not cursor.fetchone():
                return jsonify({'error': 'Currency not found'}), 404  # Если нет — 404 Not Found

            # Обновляем курс
            cursor.execute('UPDATE currencies SET rate = ? WHERE currency_name = ?', (new_rate, name))
            conn.commit()

        return jsonify({'message': 'Currency updated successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/delete', methods=['POST'])  # Регистрируем POST-запрос по адресу /delete
def delete_currency():
    data = request.get_json()  # Получаем JSON из запроса
    name = data.get('currency_name')  # Извлекаем имя валюты

    # Проверка: передано ли имя валюты
    if not name:
        return jsonify({'error': 'Missing currency_name'}), 400

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            # Проверяем, есть ли такая валюта
            cursor.execute('SELECT id FROM currencies WHERE currency_name = ?', (name,))
            if not cursor.fetchone():
                return jsonify({'error': 'Currency not found'}), 404

            # Удаляем валюту
            cursor.execute('DELETE FROM currencies WHERE currency_name = ?', (name,))
            conn.commit()

        return jsonify({'message': 'Currency deleted successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(port=5001)