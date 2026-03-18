import telebot
import time
from telebot import types

TOKEN = "8308935041:AAFTLJF1gSaxt7xdVUFHBlz9ev2710TGm_A"
CHANNEL = "@pizzabotinfo"
SUPPORT_USERNAME = "@maharaga_coder"
MENU_PHOTO = "AgACAgIAAxkBAAIBl2m5e_6xlcedCX01z9KAWL4PlWOsAALnEWsb7gzQSVRyFljghMRfAQADAgADeQADOgQ"

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
    else:
        users[uid]["name"] = full_name
        if username:
            users[uid]["username"] = username
    return users[uid]


def check_sub(user_id):
    try:
        member = bot.get_chat_member(CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False


def sub_kb():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("📢 Подписаться", url="https://t.me/pizzabotinfo"))
    kb.add(types.InlineKeyboardButton("✅ Проверить подписку", callback_data="check_sub"))
    return kb


def main_menu_kb():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("🔑 Купить private key", callback_data="buy_menu"),
        types.InlineKeyboardButton("👤 Мой профиль", callback_data="profile")
    )
    kb.add(
        types.InlineKeyboardButton("ℹ️ Информация", callback_data="info"),
        types.InlineKeyboardButton("🛠 Поддержка", callback_data="support")
    )
    return kb


def buy_menu_kb():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("1 запрос - 20₽", callback_data="buy_1"),
        types.InlineKeyboardButton("5 запросов - 100₽", callback_data="buy_5")
    )
    kb.add(
        types.InlineKeyboardButton("30 запросов - 150₽", callback_data="buy_30"),
        types.InlineKeyboardButton("100 запросов - 250₽", callback_data="buy_100")
    )
    kb.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="back_main"))
    return kb


def back_kb():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("⬅️ Назад в меню", callback_data="back_main"))
    return kb


def send_main_menu(chat_id):
    caption = (
        "🍕 <b>PIZZA BOT</b>\n\n"
        "Добро пожаловать в меню.\n"
        "Выберите нужный раздел ниже."
    )

    if MENU_PHOTO:
        bot.send_photo(
            chat_id,
            MENU_PHOTO,
            caption=caption,
            parse_mode="HTML",
            reply_markup=main_menu_kb()
        )
    else:
        bot.send_message(
            chat_id,
            caption,
            parse_mode="HTML",
            reply_markup=main_menu_kb()
        )


@bot.message_handler(commands=["start"])
def start(message):
    get_user(
        message.from_user.id,
        message.from_user.full_name,
        message.from_user.username
    )

    if not check_sub(message.from_user.id):
        bot.send_message(
            message.chat.id,
            "❌ <b>Доступ ограничен</b>\n\n"
            "Чтобы использовать <b>PIZZA BOT</b>, подпишитесь на канал:\n"
            "@pizzabotinfo",
            parse_mode="HTML",
            reply_markup=sub_kb()
        )
        return

    send_main_menu(message.chat.id)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user = get_user(
        call.from_user.id,
        call.from_user.full_name,
        call.from_user.username
    )

    if call.data == "check_sub":
        if check_sub(call.from_user.id):
            bot.answer_callback_query(call.id, "✅ Подписка подтверждена")
            bot.send_message(call.message.chat.id, "✅ Доступ открыт")
            send_main_menu(call.message.chat.id)
        else:
            bot.answer_callback_query(call.id, "❌ Вы еще не подписаны")
            bot.send_message(
                call.message.chat.id,
                "❌ Сначала подпишитесь на канал @pizzabotinfo",
                reply_markup=sub_kb()
            )
        return

    if not check_sub(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ Нужна подписка")
        bot.send_message(
            call.message.chat.id,
            "❌ Без подписки бот недоступен.",
            reply_markup=sub_kb()
        )
        return

    if call.data == "back_main":
        bot.answer_callback_query(call.id)
        send_main_menu(call.message.chat.id)

    elif call.data == "buy_menu":
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            "🔑 <b>Покупка private key</b>\n\n"
            "Выберите подходящий тариф:",
            parse_mode="HTML",
            reply_markup=buy_menu_kb()
        )

    elif call.data in ["buy_1", "buy_5", "buy_30", "buy_100"]:
        prices = {
            "buy_1": "1 запрос - 20₽",
            "buy_5": "5 запросов - 100₽",
            "buy_30": "30 запросов - 150₽",
            "buy_100": "100 запросов - 250₽"
        }
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            f"💳 <b>Вы выбрали:</b> {prices[call.data]}\n\n"
            f"Для покупки напишите в поддержку:\n{SUPPORT_USERNAME}",
            parse_mode="HTML",
            reply_markup=back_kb()
        )

    elif call.data == "profile":
        bot.answer_callback_query(call.id)
        username_text = f"@{user['username']}" if user["username"] else "Не указан"
        bot.send_message(
            call.message.chat.id,
            "👤 <b>Мой профиль</b>\n\n"
            f"📝 Имя: {user['name']}\n"
            f"🔹 Username: {username_text}\n"
            f"📅 Дата регистрации: {user['reg_date']}\n"
            f"📊 Всего запросов: {user['total_requests']}",
            parse_mode="HTML",
            reply_markup=back_kb()
        )

    elif call.data == "info":
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            "ℹ️ <b>Информация</b>\n\n"
            "Это PIZZA BOT.\n"
            "Доступ к меню открывается после подписки на канал.",
            parse_mode="HTML",
            reply_markup=back_kb()
        )

    elif call.data == "support":
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            "🛠 <b>Техническая поддержка</b>\n\n"
            f"Связь: {SUPPORT_USERNAME}",
            parse_mode="HTML",
            reply_markup=back_kb()
        )


@bot.message_handler(func=lambda message: True)
def text_handler(message):
    if not check_sub(message.from_user.id):
        bot.send_message(
            message.chat.id,
            "❌ Для использования бота нужно подписаться на канал @pizzabotinfo",
            reply_markup=sub_kb()
        )


print("PIZZA BOT запущен")
bot.infinity_polling(skip_pending=True)
