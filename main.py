import telebot
import time
from telebot import types

TOKEN = "8308935041:AAFTLJF1gSaxt7xdVUFHBlz9ev2710TGm_A"

CHANNEL = "@pizzabotinfo"
SUPPORT_USERNAME = "@maharaga_coder"
MENU_PHOTO = AgACAgIAAxkBAAIBl2m5e_6xlcedCX01z9KAWL4PlWOsAALnEWsb7gzQSVRyFljghMRfAQADAgADeQADOgQ

bot = telebot.TeleBot(TOKEN)

users = {}

def get_user(user_id, full_name="Пользователь", username=None):
    uid = str(user_id)
    if uid not in users:
        users[uid] = {
            "name": full_name,
            "username": username or "",
            "reg_date": time.strftime("%d.%m.%Y"),
            "total_requests": 0
        }
    return users[uid]

def main_menu():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("👤 Профиль", callback_data="profile"))
    kb.add(types.InlineKeyboardButton("🛠 Поддержка", callback_data="support"))
    return kb

@bot.message_handler(commands=["start"])
def start(message):
    get_user(message.from_user.id, message.from_user.full_name, message.from_user.username)
    bot.send_message(message.chat.id, "🍕 PIZZA BOT запущен", reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    user = get_user(call.from_user.id)

    if call.data == "profile":
        bot.send_message(call.message.chat.id,
                         f"👤 Имя: {user['name']}\n📅 Регистрация: {user['reg_date']}")
    elif call.data == "support":
        bot.send_message(call.message.chat.id,
                         f"🛠 Поддержка: {SUPPORT_USERNAME}")

print("BOT STARTED")
bot.infinity_polling(skip_pending=True)
