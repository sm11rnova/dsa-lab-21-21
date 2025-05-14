import telebot

bot = telebot.TeleBot('8055698799:AAHAG3KjNAV30aOOvYN2AmSAI3Uyc42kH_g')

currency_rates = {}

def show_commands(message):
    bot.send_message(message.chat.id,
                    "Доступные команды:\n"
                    "/save_currency - сохранить курс валюты\n"
                    "/convert - конвертировать валюту\n"
                    "/start - показать приветствие")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 
                "Привет! Давай сконвертируем валюту!")
    show_commands(message)


@bot.message_handler(commands=['save_currency'])
def ask_currency_name(message):
    msg = bot.send_message(message.chat.id, "Введите название валюты(USD):")
    bot.register_next_step_handler(msg, ask_currency_rate)

def ask_currency_rate(message):
    if message.text.startswith('/'):
        show_commands(message)
        return
    
    currency = message.text.upper()
    if not currency.isalpha():
        msg = bot.send_message(message.chat.id, "Название валюты должно содержать только буквы. Попробуйте снова.")
        bot.register_next_step_handler(msg, ask_currency_rate)
        return
    
    msg = bot.send_message(message.chat.id, f"Введите курс {currency} к рублю:")
    bot.register_next_step_handler(msg, save_currency, currency)

def save_currency(message, currency):
    if message.text.startswith('/'):
        show_commands(message)
        return
    
    try:
        rate = float(message.text.replace(',', '.'))
        if rate <= 0:
            raise ValueError()
            
        currency_rates[currency] = rate
        bot.send_message(message.chat.id, f"Курс сохранен: 1 {currency} = {rate} RUB")
    except:
        msg = bot.send_message(message.chat.id, "Некорректный курс. Введите число (например, 75.5)")
        bot.register_next_step_handler(msg, save_currency, currency)

@bot.message_handler(commands=['convert'])
def ask_currency_to_convert(message):
    if not currency_rates:
        bot.send_message(message.chat.id, "Нет сохраненных валют. Сначала добавьте валюту через /save_currency")
        return
    
    msg = bot.send_message(message.chat.id, "Введите название валюты для конвертации (например, USD):")
    bot.register_next_step_handler(msg, ask_amount_to_convert)

def ask_amount_to_convert(message):
    if message.text.startswith('/'):
        show_commands(message)
        return
    
    currency = message.text.upper()
    if currency not in currency_rates:
        msg = bot.send_message(message.chat.id, f"Валюта {currency} не найдена. Используйте /show_currencies для просмотра доступных валют.")
        bot.register_next_step_handler(msg, ask_amount_to_convert) 
        return
    
    msg = bot.send_message(message.chat.id, f"Введите сумму в {currency} для конвертации в рубли:")
    bot.register_next_step_handler(msg, convert_currency, currency)

def convert_currency(message, currency):
    if message.text.startswith('/'):
        show_commands(message)
        return
    
    try:
        amount = float(message.text.replace(',', '.'))
        if amount <= 0:
            raise ValueError()
        
        rate = currency_rates[currency]
        result = amount * rate
        bot.send_message(message.chat.id, f"{amount} {currency} = {round(result, 2)} RUB (курс: 1 {currency} = {rate} RUB)")
    except:
        msg = bot.send_message(message.chat.id, "Некорректная сумма. Введите число (например, 100)")
        bot.register_next_step_handler(msg, convert_currency, currency)

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    if not message.text.startswith('/'):
        show_commands(message)
        return
    
    bot.send_message(message.chat.id, "Неизвестная команда. Вот доступные команды:")
    show_commands(message)

bot.infinity_polling()