import telebot
import time
from telebot import types

TOKEN = "8308935041:AAFTLJF1gSaxt7xdVUFHBlz9ev2710TGm_A"
CHANNEL = "@pizzabotinfo"
SUPPORT = "@maharaga_coder"

MENU_PHOTO = "AgACAgIAAxkBAAIBl2m5e_6xlcedCX01z9KAWL4PlWOsAALnEWsb7gzQSVRyFljghMRfAQADAgADeQADOgQ"

bot = telebot.TeleBot(TOKEN)

users = {}
pending = {}

# -------- ЮЗЕР --------
def get_user(uid, name):
    uid = str(uid)
    if uid not in users:
        users[uid] = {
            "name": name,
            "reg": time.strftime("%d.%m.%Y"),
            "total": 0,
            "private": 0
        }
    return users[uid]

# -------- ПОДПИСКА --------
def check_sub(user_id):
    try:
        m = bot.get_chat_member(CHANNEL, user_id)
        return m.status in ["member", "administrator", "creator"]
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
        types.InlineKeyboardButton("👤 Профиль", callback_data="profile")
    )
    kb.add(
        types.InlineKeyboardButton("🎁 Бесплатные запросы", callback_data="free"),
        types.InlineKeyboardButton("💎 Приватные запросы", callback_data="private_menu")
    )
    kb.add(types.InlineKeyboardButton("🛠 Поддержка", callback_data="support"))
    return kb

# -------- START --------
@bot.message_handler(commands=["start"])
def start(m):
    if not check_sub(m.from_user.id):
        return bot.send_message(m.chat.id, "❌ Подпишись", reply_markup=sub_kb())

    get_user(m.from_user.id, m.from_user.first_name)

    text = "🍕 PIZZA BOT\n\nВыбери действие:"
    if MENU_PHOTO:
        bot.send_photo(m.chat.id, MENU_PHOTO, caption=text, reply_markup=menu())
    else:
        bot.send_message(m.chat.id, text, reply_markup=menu())

# -------- CALLBACK --------
@bot.callback_query_handler(func=lambda c: True)
def call(c):
    uid = str(c.from_user.id)
    user = get_user(c.from_user.id, c.from_user.first_name)

    # проверка подписки
    if c.data == "check":
        if check_sub(c.from_user.id):
            bot.answer_callback_query(c.id, "✅ Готово")
            bot.send_message(c.message.chat.id, "Доступ открыт", reply_markup=menu())
        else:
            bot.answer_callback_query(c.id, "❌ Нет подписки")

    # назад
    elif c.data == "back":
        bot.edit_message_text("🍕 PIZZA BOT\n\nМеню:",
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=menu())

    # профиль
    elif c.data == "profile":
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="back"))

        bot.edit_message_text(
            f"👤 Имя: {user['name']}\n"
            f"📅 Регистрация: {user['reg']}\n"
            f"⚡ Всего: {user['total']}\n"
            f"💎 Приватных: {user['private']}",
            c.message.chat.id,
            c.message.message_id,
            reply_markup=kb
        )

    # покупка
    elif c.data == "buy":
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("100 запросов", callback_data="buy_private"))
        kb.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="back"))

        bot.edit_message_text("💳 Покупка\n\nНажми:", c.message.chat.id, c.message.message_id, reply_markup=kb)

    elif c.data == "buy_private":
        user["private"] += 100
        bot.answer_callback_query(c.id, "Куплено 100")
        bot.edit_message_text("✅ Куплено 100 приватных запросов",
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=menu())

    # -------- ПРИВАТНЫЕ --------
    elif c.data == "private_menu":
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("🚀 Использовать", callback_data="use_private"))
        kb.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="back"))

        bot.edit_message_text(
            f"💎 Приватные запросы\n\nДоступно: {user['private']}",
            c.message.chat.id,
            c.message.message_id,
            reply_markup=kb
        )

    elif c.data == "use_private":
        if user["private"] <= 0:
            return bot.answer_callback_query(c.id, "❌ Нет запросов")

        pending[uid] = "wait_private"
        bot.edit_message_text("📥 Введи:\n@user 10 причина",
                              c.message.chat.id,
                              c.message.message_id)

    # запуск
    elif c.data == "start":
        data = pending.get(uid)
        if not data:
            return

        username, total, mode = data

        for i in range(1, total + 1):
            time.sleep(1)
            bot.send_message(
                c.message.chat.id,
                f"✅ {username}\n⚡ {i}/{total}"
            )

        user["total"] += total
        if mode == "private":
            user["private"] -= total

        bot.send_message(c.message.chat.id, "🏁 Готово")
        pending.pop(uid, None)

    # поддержка
    elif c.data == "support":
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="back"))

        bot.edit_message_text(
            f"🛠 Поддержка:\n{SUPPORT}",
            c.message.chat.id,
            c.message.message_id,
            reply_markup=kb
        )

# -------- ВВОД --------
@bot.message_handler(func=lambda m: True)
def handle(m):
    uid = str(m.from_user.id)
    state = pending.get(uid)

    if state != "wait_private":
        return

    parts = m.text.split()
    if len(parts) < 2:
        return bot.send_message(m.chat.id, "❌ Пример: @user 10")

    username = parts[0]
    total = int(parts[1])

    pending[uid] = (username, total, "private")

    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🚀 Начать", callback_data="start"))

    bot.send_message(
        m.chat.id,
        f"🎯 {username}\n📦 {total}\n\nЗапустить?",
        reply_markup=kb
    )

print("Бот запущен")
bot.infinity_polling()
