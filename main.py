import telebot
import time
import random
from telebot import types

TOKEN = "8308935041:AAFTLJF1gSaxt7xdVUFHBlz9ev2710TGm_A"
CHANNEL = "@pizzabotinfo"
SUPPORT = "@maharaga_coder"

bot = telebot.TeleBot(TOKEN)

users = {}
pending = {}

# -------- ПРОВЕРКА ПОДПИСКИ --------
def check_sub(user_id):
    try:
        member = bot.get_chat_member(CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

def sub_kb():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("📢 Подписаться", url="https://t.me/pizzabotinfo"))
    kb.add(types.InlineKeyboardButton("✅ Проверить", callback_data="check"))
    return kb

# -------- МЕНЮ --------
def menu():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("🔑 Купить private key", callback_data="buy"),
        types.InlineKeyboardButton("👤 Мой профиль", callback_data="profile")
    )
    kb.add(
        types.InlineKeyboardButton("🎁 Бесплатные запросы", callback_data="free"),
        types.InlineKeyboardButton("🛠 Поддержка", callback_data="support")
    )
    return kb

# -------- СТАРТ --------
@bot.message_handler(commands=["start"])
def start(m):
    if not check_sub(m.from_user.id):
        return bot.send_message(
            m.chat.id,
            "❌ Подпишись на канал чтобы использовать бота",
            reply_markup=sub_kb()
        )

    uid = str(m.from_user.id)
    if uid not in users:
        users[uid] = {
            "reg": time.strftime("%d.%m.%Y"),
            "total": 0
        }

    bot.send_message(
        m.chat.id,
        "🍕 PIZZA BOT\n\nВыбери действие:",
        reply_markup=menu()
    )

# -------- ПРОВЕРКА --------
@bot.callback_query_handler(func=lambda c: c.data == "check")
def check(call):
    if check_sub(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ Готово")
        bot.send_message(call.message.chat.id, "Доступ открыт", reply_markup=menu())
    else:
        bot.answer_callback_query(call.id, "❌ Ты не подписан")

# -------- ПОКУПКА --------
@bot.callback_query_handler(func=lambda c: c.data == "buy")
def buy(call):
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("1 запрос - 20₽", callback_data="x"),
        types.InlineKeyboardButton("5 запросов - 100₽", callback_data="x")
    )
    kb.add(
        types.InlineKeyboardButton("30 запросов - 150₽", callback_data="x"),
        types.InlineKeyboardButton("100 запросов - 250₽", callback_data="x")
    )
    kb.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="back"))

    bot.edit_message_text(
        "💳 Покупка private key\n\nВыбери тариф:",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=kb
    )

# -------- ПРОФИЛЬ --------
@bot.callback_query_handler(func=lambda c: c.data == "profile")
def profile(call):
    uid = str(call.from_user.id)
    u = users[uid]

    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="back"))

    bot.edit_message_text(
        f"👤 Имя: {call.from_user.first_name}\n"
        f"📅 Регистрация: {u['reg']}\n"
        f"⚡ Всего запросов: {u['total']}",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=kb
    )

# -------- БЕСПЛАТНЫЕ --------
@bot.callback_query_handler(func=lambda c: c.data == "free")
def free(call):
    pending[str(call.from_user.id)] = "wait"

    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="back"))

    bot.edit_message_text(
        "📥 Введи:\n\n@username 30 причина",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=kb
    )

# -------- ВВОД --------
@bot.message_handler(func=lambda m: True)
def input_data(m):
    uid = str(m.from_user.id)

    if pending.get(uid) != "wait":
        return

    parts = m.text.split(maxsplit=2)

    if len(parts) < 2:
        return bot.send_message(m.chat.id, "❌ Пример: @user 10 причина")

    username = parts[0]

    try:
        total = int(parts[1])
    except:
        return bot.send_message(m.chat.id, "❌ Ошибка числа")

    pending[uid] = (username, total)

    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🚀 Начать", callback_data="start"))

    bot.send_message(
        m.chat.id,
        f"🎯 Цель: {username}\n"
        f"📦 Запросов: {total}\n\n❗ Вы уверены?",
        reply_markup=kb
    )

# -------- ЗАПУСК --------
@bot.callback_query_handler(func=lambda c: c.data == "start")
def start_req(call):
    uid = str(call.from_user.id)

    if uid not in pending:
        return

    username, total = pending[uid]

    for i in range(1, total + 1):
        time.sleep(1)
        bot.send_message(
            call.message.chat.id,
            f"✅ Цель: {username}\n"
            f"📊 Проверка: в процессе\n"
            f"⚡ Выполнено: {i}"
        )

    users[uid]["total"] += total

    bot.send_message(
        call.message.chat.id,
        f"🏁 Готово\n\nВыполнено: {total}"
    )

    pending.pop(uid)

# -------- ПОДДЕРЖКА --------
@bot.callback_query_handler(func=lambda c: c.data == "support")
def support(call):
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="back"))

    bot.edit_message_text(
        f"🛠 Поддержка:\n{SUPPORT}",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=kb
    )

# -------- НАЗАД --------
@bot.callback_query_handler(func=lambda c: c.data == "back")
def back(call):
    bot.edit_message_text(
        "🍕 PIZZA BOT\n\nВыбери действие:",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=menu()
    )

print("Бот запущен")
bot.infinity_polling(skip_pending=True)
