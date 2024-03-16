import json
import random
import string
import telebot

TOKEN = ""
bot = telebot.TeleBot(TOKEN)

def generate_wallet_address():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

def load_data():
    try:
        with open('bank_data.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_data(data):
    with open('bank_data.json', 'w') as file:
        json.dump(data, file, indent=4)

def notify_user(recipient_id, amount):
    bot.send_message(recipient_id, f"🎉 Вы получили перевод NeuroCoin на сумму {amount}.")

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    data = load_data()
    if user_id not in data:
        data[user_id] = {'balance': 0, 'wallet_address': generate_wallet_address()}
        save_data(data)
    bot.reply_to(message, f"👋 Привет! Это мини-банк. Ваш текущий баланс: {data[user_id]['balance']} NeuroCoin\n💼 Ваш адрес кошелька: {data[user_id]['wallet_address']}\n\nВы можете использовать следующие команды:\n/balance - Проверить баланс\n/transfer [id пользователя] [сумма] - Перевести NeuroCoin на другой кошелек\n/all_users - Показать данные всех пользователей")

@bot.message_handler(commands=['all_users'])
def show_all_users_data(message):
    data = load_data()
    if data:
        response = "📋 Данные всех пользователей:\n"
        for user_id, user_data in data.items():
            response += f"ID пользователя: {user_id}\n"
            response += f"Баланс: {user_data['balance']} NeuroCoin\n"
        bot.reply_to(message, response)
    else:
        bot.reply_to(message, "😔 Нет данных о пользователях.")

@bot.message_handler(commands=['balance'])
def balance(message):
    user_id = str(message.from_user.id)
    data = load_data()
    if user_id in data:
        bot.reply_to(message, f"💰 Ваш текущий баланс: {data[user_id]['balance']} NeuroCoin")
    else:
        bot.reply_to(message, "😔 У вас нет счета в нашем банке.")

@bot.message_handler(commands=['transfer'])
def process_transfer(message):
    try:
        parts = message.text.split(' ')
        recipient_id = parts[1]
        amount = float(parts[2])

        user_id = str(message.from_user.id)
        data = load_data()

        if user_id not in data:
            bot.reply_to(message, "😔 У вас нет счета в нашем банке.")
            return

        if amount <= 0:
            bot.reply_to(message, "⚠️ Сумма перевода должна быть положительной.")
            return

        if data[user_id]['balance'] < amount:
            bot.reply_to(message, "😔 Недостаточно средств на счете.")
            return

        recipient_data = data.get(recipient_id)

        if not recipient_data:
            bot.reply_to(message, "😔 Пользователь с указанным ID не найден.")
            return

        data[user_id]['balance'] -= amount
        recipient_data['balance'] += amount
        save_data(data)

        bot.reply_to(message, f"✅ Вы успешно перевели {amount} NeuroCoin пользователю с ID {recipient_id}. Ваш текущий баланс: {data[user_id]['balance']} NeuroCoin")

        notify_user(recipient_id, amount)
    except (IndexError, ValueError):
        bot.reply_to(message, "❌ Неверный формат ввода. Пожалуйста, введите ID пользователя и сумму для перевода в правильном формате: /transfer [id пользователя] [сумма]")

if __name__ == '__main__':
    bot.polling()
