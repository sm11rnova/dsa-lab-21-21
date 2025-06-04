# создаю экземпляр приложения flask
from flask import Flask, request, jsonify  

# инициализирую приложение
app = Flask(__name__)  

# создаю словарь с фиксированными курсами валют
STATIC_RATES = {  
    "USD": 91.0,  
    "EUR": 98.0  
}  

# создаю маршрут для обработки запросов по адресу /rate
@app.route("/rate")  
def get_rate():  
    # получаю параметр currency из запроса
    currency = request.args.get("currency")  
    # проверяю, что в запросе указана известная валюта
    if currency not in STATIC_RATES:  
        # возвращаю ошибку, если валюта неизвестна
        return jsonify({"message": "UNKNOWN CURRENCY"}), 400  
    try:  
        # возвращаю курс валюты при успешном запросе
        return jsonify({"rate": STATIC_RATES[currency]}), 200  
    except Exception:  
        # возвращаю ошибку при непредвиденной проблеме
        return jsonify({"message": "UNEXPECTED ERROR"}), 500  

# запускаю приложение в режиме отладки
if __name__ == "__main__":  
    app.run(debug=True)  