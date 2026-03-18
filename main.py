
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

def check_sub(user_id):
    try:
        m = bot.get_chat_member(CHANNEL, user_id)
        return m.status in ["member", "administrator", "creator"]
    except:
        return False

def sub_kb():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("📢 Подписаться", url="https://t.me/pizzabotinfo"))
    kb.add(types.InlineKeyboardButton("✅ Проверить", callback_data="check_sub"))
    return kb

def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🔑 Купить private key", "👤 Профиль")
    kb.row("🎁 Бесплатные запросы", "💎 Приватные запросы")
    kb.row("🛠 Поддержка")
    return kb

def back_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("⬅️ Назад")
    return kb

@bot.message_handler(commands=["start"])
def start(m):
    if not check_sub(m.from_user.id):
        return bot.send_message(
            m.chat.id,
            "❌ Подпишись на канал, чтобы использовать бота",
            reply_markup=sub_kb()
        )

    get_user(m.from_user.id, m.from_user.first_name)

    text = "🍕 PIZZA BOT\n\nВыбери действие:"
    if MENU_PHOTO:
        bot.send_photo(m.chat.id, MENU_PHOTO, caption=text, reply_markup=main_menu())
    else:
        bot.send_message(m.chat.id, text, reply_markup=main_menu())

@bot.callback_query_handler(func=lambda c: c.data == "check_sub")
def check_sub_callback(c):
    if check_sub(c.from_user.id):
        bot.answer_callback_query(c.id, "✅ Подписка найдена")
        bot.send_message(c.message.chat.id, "Доступ открыт ✅", reply_markup=main_menu())
    else:
        bot.answer_callback_query(c.id, "❌ Ты не подписан")

@bot.message_handler(func=lambda m: m.text == "🔑 Купить private key")
def buy_key(m):
    bot.send_message(
        m.chat.id,
        "💳 Тарифы:\n\n"
        "1 запрос — 20₽\n"
        "5 запросов — 100₽\n"
        "30 запросов — 150₽\n"
        "100 запросов — 250₽\n\n"
        f"Для покупки отпиши: {SUPPORT}",
        reply_markup=back_menu()
    )

@bot.message_handler(func=lambda m: m.text == "👤 Профиль")
def profile(m):
    u = get_user(m.from_user.id, m.from_user.first_name)
    bot.send_message(
        m.chat.id,
        f"👤 Имя: {u['name']}\n"
        f"📅 Дата регистрации: {u['reg']}\n"
        f"📊 Всего запросов: {u['total']}\n"
        f"💎 Приватных осталось: {u['private']}",
        reply_markup=back_menu()
    )

@bot.message_handler(func=lambda m: m.text == "🎁 Бесплатные запросы")
def free_requests(m):
    pending[str(m.from_user.id)] = {"mode": "free_wait"}
    bot.send_message(
        m.chat.id,
        "📥 Введи данные в формате:\n@username 10 причина",
        reply_markup=back_menu()
    )

@bot.message_handler(func=lambda m: m.text == "💎 Приватные запросы")
def private_requests(m):
    u = get_user(m.from_user.id, m.from_user.first_name)
    if u["private"] <= 0:
        return bot.send_message(
            m.chat.id,
            "❌ У тебя нет приватных запросов.\nСначала купи их в разделе 🔑 Купить private key",
            reply_markup=back_menu()
        )

    pending[str(m.from_user.id)] = {"mode": "private_wait"}
    bot.send_message(
        m.chat.id,
        f"💎 У тебя доступно {u['private']} приватных запросов.\n\n"
        "Введи данные в формате:\n@username 10 причина",
        reply_markup=back_menu()
    )

@bot.message_handler(func=lambda m: m.text == "🛠 Поддержка")
def support(m):
    bot.send_message(
        m.chat.id,
        f"🛠 Техническая поддержка:\n{SUPPORT}",
        reply_markup=back_menu()
    )

@bot.message_handler(func=lambda m: m.text == "⬅️ Назад")
def back(m):
    bot.send_message(m.chat.id, "🍕 Главное меню:", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.content_type == "text")
def handle_text(m):
    uid = str(m.from_user.id)
    state = pending.get(uid)

    if not state:
        return

    parts = m.text.split(maxsplit=2)
    if len(parts) < 2 or not parts[0].startswith("@"):
        return bot.send_message(m.chat.id, "❌ Пример: @user 10 причина")

    username = parts[0]

    try:
        total = int(parts[1])
    except:
        return bot.send_message(m.chat.id, "❌ Количество должно быть числом")

    reason = parts[2] if len(parts) > 2 else "—"

    u = get_user(m.from_user.id, m.from_user.first_name)

    if state["mode"] == "private_wait" and total > u["private"]:
        return bot.send_message(
            m.chat.id,
            f"❌ У тебя только {u['private']} приватных запросов"
        )

    bot.send_message(
        m.chat.id,
        f"🎯 Цель: {username}\n"
        f"📦 Запросов: {total}\n"
        f"📝 Причина: {reason}\n\n"
        "✅ Запуск..."
    )

    for i in range(1, total + 1):
        time.sleep(1)
        bot.send_message(
            m.chat.id,
            f"✅ Цель: {username}\n"
            f"📊 Проверка: в процессе\n"
            f"⚡ Выполнено: {i}/{total}"
        )

    u["total"] += total
    if state["mode"] == "private_wait":
        u["private"] -= total

    bot.send_message(
        m.chat.id,
        f"🏁 Готово\n\n"
        f"🎯 Цель: {username}\n"
        f"📦 Выполнено: {total}",
        reply_markup=main_menu()
    )

    pending.pop(uid, None)

print("Бот запущен")
bot.infinity_polling(skip_pending=True)