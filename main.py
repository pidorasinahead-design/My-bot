import os
import telebot
import time
from telebot import types

TOKEN = os.getenv("8308935041:AAFxsIyJ-m8lh6a8Kz8PbK92KKMREcOprG4")
CHANNEL = "@pizzabotinfo"
SUPPORT_USERNAME = "@maharaga_coder"

# Сюда вставь file_id картинки, если загрузишь ее один раз в Telegram.
# Если file_id нет, бот отправит меню без картинки.
MENU_PHOTO = AgACAgIAAxkBAAIBl2m5e_6xlcedCX01z9KAWL4PlWOsAALnEWsb7gzQSVRyFljghMRfAQADAgADeQADOgQ

bot = telebot.TeleBot(TOKEN)

users = {}
pending_input = {}


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
        users[uid]["username"] = username or users[uid]["username"]
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
        types.InlineKeyboardButton("🎁 Бесплатные запросы", callback_data="free_requests"),
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


def confirm_kb():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🚀 Начать", callback_data="start_request"))
    kb.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="back_main"))
    return kb


def send_main_menu(chat_id, user):
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
    user = get_user(
        message.from_user.id,
        message.from_user.full_name,
        message.from_user.username
    )

    if not check_sub(message.from_user.id):
        return bot.send_message(
            message.chat.id,
            "❌ <b>Доступ ограничен</b>\n\n"
            "Чтобы использовать <b>PIZZA BOT</b>, подпишитесь на канал:\n"
            "@pizzabotinfo",
            parse_mode="HTML",
            reply_markup=sub_kb()
        )

    send_main_menu(message.chat.id, user)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user = get_user(
        call.from_user.id,
        call.from_user.full_name,
        call.from_user.username
    )
    uid = str(call.from_user.id)

    if call.data == "check_sub":
        if check_sub(call.from_user.id):
            bot.answer_callback_query(call.id, "✅ Подписка подтверждена")
            bot.send_message(call.message.chat.id, "✅ Доступ открыт")
            send_main_menu(call.message.chat.id, user)
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
        bot.send_message(call.message.chat.id, "🍕 Возвращаю в главное меню...")
        send_main_menu(call.message.chat.id, user)

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
            f"Для покупки отпишите в поддержку:\n{SUPPORT_USERNAME}",
            parse_mode="HTML",
            reply_markup=back_kb()
        )

    elif call.data == "profile":
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            "👤 <b>Мой профиль</b>\n\n"
            f"📝 Имя: {user['name']}\n"
            f"📅 Дата регистрации: {user['reg_date']}\n"
            f"📊 Всего запросов: {user['total_requests']}",
            parse_mode="HTML",
            reply_markup=back_kb()
        )

    elif call.data == "free_requests":
        bot.answer_callback_query(call.id)
        pending_input[uid] = {"step": "wait_data"}
        bot.send_message(
            call.message.chat.id,
            "🎁 <b>Бесплатные запросы</b>\n\n"
            "Введите данные в формате:\n"
            "<code>@username 30 причина</code>\n\n"
            "Пример:\n"
            "<code>@example_user 10 тестовый запрос</code>",
            parse_mode="HTML",
            reply_markup=back_kb()
        )

    elif call.data == "start_request":
        info = pending_input.get(uid)
        if not info or "target" not in info:
            bot.answer_callback_query(call.id, "Данные не найдены")
            return

        bot.answer_callback_query(call.id, "🚀 Запуск...")
        target = info["target"]
        total = info["total"]

        bot.send_message(
            call.message.chat.id,
            f"🚀 <b>Запуск выполнен</b>\n\n"
            f"🎯 Цель: {target}\n"
            f"📦 Запросов: {total}\n\n"
            f"⏳ Начинаю выполнение...",
            parse_mode="HTML"
        )

        for i in range(1, total + 1):
            time.sleep(1)
            bot.send_message(
                call.message.chat.id,
                f"✅ Цель: {target}\n"
                f"📊 Статус: в процессе\n"
                f"⚡ Выполнено: {i}",
                parse_mode="HTML"
            )

        user["total_requests"] += total

        bot.send_message(
            call.message.chat.id,
            f"🏁 <b>Завершено</b>\n\n"
            f"🎯 Цель: {target}\n"
            f"📦 Всего запросов: {total}\n"
            f"✅ Успешно обработано: {total}",
            parse_mode="HTML",
            reply_markup=back_kb()
        )

        pending_input.pop(uid, None)

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
    user = get_user(
        message.from_user.id,
        message.from_user.full_name,
        message.from_user.username
    )
    uid = str(message.from_user.id)

    if not check_sub(message.from_user.id):
        return bot.send_message(
            message.chat.id,
            "❌ Для использования бота нужно подписаться на канал @pizzabotinfo",
            reply_markup=sub_kb()
        )

    state = pending_input.get(uid)
    if not state or state.get("step") != "wait_data":
        return

    text = message.text.strip()
    parts = text.split(maxsplit=2)

    if len(parts) < 2 or not parts[0].startswith("@"):
        return bot.send_message(
            message.chat.id,
            "❌ Неверный формат.\n\n"
            "Введите так:\n"
            "<code>@username 30 причина</code>",
            parse_mode="HTML"
        )

    target = parts[0]

    try:
        total = int(parts[1])
    except ValueError:
        return bot.send_message(
            message.chat.id,
            "❌ Количество запросов должно быть числом."
        )

    if total < 1:
        return bot.send_message(message.chat.id, "❌ Минимум 1 запрос.")
    if total > 50:
        total = 50

    reason = parts[2] if len(parts) > 2 else "Не указана"

    pending_input[uid] = {
        "step": "confirm",
        "target": target,
        "total": total,
        "reason": reason
    }

    bot.send_message(
        message.chat.id,
        "📋 <b>Подтверждение</b>\n\n"
        f"🎯 Цель: {target}\n"
        f"📦 Запросов: {total}\n"
        f"📝 Причина: {reason}\n\n"
        "❓ Вы уверены в своем решении?",
        parse_mode="HTML",
        reply_markup=confirm_kb()
    )


print("PIZZA BOT запущен")
bot.infinity_polling(skip_pending=True)
