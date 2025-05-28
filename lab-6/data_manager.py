from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DB_PATH = 'currencies.db'  # Используем ту же базу, что и currency-manager

@app.route('/convert', methods=['GET'])  # Эндпоинт для конвертации суммы
def convert_currency():
    name = request.args.get('currency_name')  # Получаем название валюты из query-параметров
    amount = request.args.get('amount')  # Получаем сумму для конвертации

    # Проверка: переданы ли оба параметра
    if not name or not amount:
        return jsonify({'error': 'Missing currency_name or amount'}), 400

    try:
        amount = float(amount)  # Преобразуем строку в число
    except ValueError:
        return jsonify({'error': 'Amount must be a number'}), 400

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            # Получаем курс для указанной валюты
            cursor.execute('SELECT rate FROM currencies WHERE currency_name = ?', (name,))
            row = cursor.fetchone()
            if not row:
                return jsonify({'error': 'Currency not found'}), 404

            rate = row[0]
            result = amount * rate  # Конвертируем
            return jsonify({'converted_amount': result}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/currencies', methods=['GET'])  # Эндпоинт для получения всех валют
def get_currencies():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT currency_name, rate FROM currencies')
            rows = cursor.fetchall()
            currencies = [{'currency_name': row[0], 'rate': row[1]} for row in rows]
            return jsonify({'currencies': currencies}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5002)  # Запускаем на порту 5002
