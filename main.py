import json
import random
import string
import telebot
from telebot import types
from yoomoney import Quickpay, Client

TOKEN = ""
bot = telebot.TeleBot(TOKEN)
YOOMONEY_TOKEN = ""
ym_client = Client(YOOMONEY_TOKEN)

def purchase_coins(user_id, amount):
    label = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    quickpay = Quickpay(
        receiver="Номер кошелька получателя",
        quickpay_form="shop",
        targets="Покупка NeuroCoin",
        paymentType="SB",
        sum=2,
        label=label
    )
    save_label(user_id, label)
    return quickpay.redirected_url, label

def save_label(user_id, label):
    data = load_data()
    if user_id in data:
        data[user_id]['label'] = label
        save_data(data)

def check_payment(user_id):
    data = load_data()
    if user_id in data and 'label' in data[user_id]:
        label = data[user_id]['label']
        history = ym_client.operation_history(label=label)
        if history.operations:
            return history.operations[0].amount
        return False

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

@bot.message_handler(commands=['getCoin'])
def start(message):
    try:
        command_parts = message.text.split(' ')
        if len(command_parts) < 2:
            bot.reply_to(message, "❗️ Укажите количество монет для покупки.")
            return
        coins_to_buy = int(command_parts[1])
        if coins_to_buy <= 0:
            bot.reply_to(message, "❗️ Укажите корректное количество монет для покупки.")
            return
        user_id = str(message.from_user.id)
        url, label = purchase_coins(user_id, coins_to_buy)
        
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Проверить оплату", callback_data="check_payment"))
        
        bot.send_message(message.chat.id, f"Ссылка для оплаты {coins_to_buy} монет: {url}", reply_markup=keyboard)

    except ValueError:
        bot.reply_to(message, "❗️ Пожалуйста, укажите корректное количество монет для покупки.")

    except Exception as e:
        bot.reply_to(message, f"❗️ Произошла ошибка: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data == 'check_payment')
def check_payment_callback(call):
    user_id = str(call.from_user.id)
    amount = check_payment(user_id)
    data = load_data()
    if amount:
        label = data[user_id]['label']
        if label not in data[user_id]['processed_labels']:
            coins_bought = int(label.split('_')[0]) 
            data[user_id]['balance'] += coins_bought  
            data[user_id].setdefault('processed_labels', []).append(label) 
            save_data(data)
            bot.send_message(call.message.chat.id, f"Оплата успешно проведена. Вам начислено {coins_bought} NeuroCoin.")
        else:
            bot.send_message(call.message.chat.id, "Эта оплата уже обработана.")
    else:
        bot.send_message(call.message.chat.id, "Оплата не завершена или не найдена.")
        
@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    data = load_data()
    if user_id not in data:
        data[user_id] = {'balance': 0, 'wallet_address': generate_wallet_address()}
        save_data(data)
    bot.reply_to(message, f"👋 Привет! Это мини-банк. Ваш текущий баланс: {data[user_id]['balance']} NeuroCoin\n💼 Ваш адрес кошелька: {data[user_id]['wallet_address']}\n\nВы можете использовать следующие команды:\n/balance - Проверить баланс\n/transfer [user id] [amount] - Перевести NeuroCoin на другой кошелек\n/all_users - Показать данные всех пользователей\n/getCoin [amount] - Купить NeuroCoin")

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
        bot.reply_to(message, "😔 Нет доступных данных о пользователях.")

@bot.message_handler(commands=['balance'])
def balance(message):
    user_id = str(message.from_user.id)
    data = load_data()
    if user_id in data:
        bot.reply_to(message, f"💰 Ваш текущий баланс: {data[user_id]['balance']} NeuroCoin")
    else:
        bot.reply_to(message, "😔 У вас нет аккаунта в нашем банке.")

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
