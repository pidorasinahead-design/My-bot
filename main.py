import telebot
import time
from telebot import types

TOKEN = "ТВОЙ_НОВЫЙ_ТОКЕН"
ADMIN_ID = 7738822030 
CHANNEL = "@pizzabotinfo"
SUPPORT = "@maharaga_coder"
MENU_PHOTO = "AgACAgIAAxkBAAIBl2m5e_6xlcedCX01z9KAWL4PlWOsAALnEWsb7gzQSVRyFljghMRfAQADAgADeQADOgQ"

bot = telebot.TeleBot(TOKEN)

users = {}
pending_user_input = {}
admin_requests = {}


def get_user(user_id, full_name="Пользователь", username=""):
    uid = str(user_id)
    if uid not in users:
        users[uid] = {
            "name": full_name,
            "username": username,
            "reg_date": time.strftime("%d.%m.%Y"),
            "total_requests": 0,
            "private_requests": 0
        }
    else:
        users[uid]["name"] = full_name
        users[uid]["username"] = username or users[uid]["username"]
    return users[uid]


def check_sub(user_id):
    try:
        member = bot.get_chat_member(CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
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
        types.InlineKeyboardButton("👤 Профиль", callback_data="profile")
    )
    kb.add(
        types.InlineKeyboardButton("🎁 Бесплатные запросы", callback_data="free_requests"),
        types.InlineKeyboardButton("💎 Приватные запросы", callback_data="private_requests")
    )
    kb.add(types.InlineKeyboardButton("🛠 Поддержка", callback_data="support"))
    return kb


def buy_menu_kb():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("1 запрос — 20₽", callback_data="buy_1"),
        types.InlineKeyboardButton("5 запросов — 100₽", callback_data="buy_5")
    )
    kb.add(
        types.InlineKeyboardButton("30 запросов — 150₽", callback_data="buy_30"),
        types.InlineKeyboardButton("100 запросов — 250₽", callback_data="buy_100")
    )
    kb.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="back_main"))
    return kb


def back_kb():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="back_main"))
    return kb


def confirm_request_kb(req_id):
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("✅ Одобрить", callback_data=f"approve:{req_id}"),
        types.InlineKeyboardButton("❌ Отклонить", callback_data=f"decline:{req_id}")
    )
    return kb


def send_main_menu(chat_id, user):
    text = (
        "🍕 <b>PIZZA BOT</b>\n\n"
        "Выбери действие:"
    )

    if MENU_PHOTO:
        bot.send_photo(
            chat_id,
            MENU_PHOTO,
            caption=text,
            parse_mode="HTML",
            reply_markup=main_menu_kb()
        )
    else:
        bot.send_message(
            chat_id,
            text,
            parse_mode="HTML",
            reply_markup=main_menu_kb()
        )


@bot.message_handler(commands=["start"])
def start(message):
    user = get_user(
        message.from_user.id,
        message.from_user.full_name,
        message.from_user.username or ""
    )

    if not check_sub(message.from_user.id):
        return bot.send_message(
            message.chat.id,
            "❌ Для использования бота подпишись на канал @pizzabotinfo",
            reply_markup=sub_kb()
        )

    send_main_menu(message.chat.id, user)


@bot.message_handler(content_types=["photo"])
def get_photo_id(message):
    file_id = message.photo[-1].file_id
    bot.send_message(message.chat.id, f"FILE_ID:\n{file_id}")


@bot.callback_query_handler(func=lambda c: True)
def callback_handler(call):
    user = get_user(
        call.from_user.id,
        call.from_user.full_name,
        call.from_user.username or ""
    )
    uid = str(call.from_user.id)

    if call.data == "check_sub":
        if check_sub(call.from_user.id):
            bot.answer_callback_query(call.id, "✅ Подписка подтверждена")
            bot.send_message(call.message.chat.id, "✅ Доступ открыт")
            send_main_menu(call.message.chat.id, user)
        else:
            bot.answer_callback_query(call.id, "❌ Ты не подписан")
        return

    if not check_sub(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ Нужна подписка")
        bot.send_message(call.message.chat.id, "❌ Без подписки бот недоступен", reply_markup=sub_kb())
        return

    if call.data == "back_main":
        bot.answer_callback_query(call.id)
        send_main_menu(call.message.chat.id, user)

    elif call.data == "buy_menu":
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            "🔑 <b>Купить private key</b>\n\nВыбери тариф:",
            parse_mode="HTML",
            reply_markup=buy_menu_kb()
        )

    elif call.data in ["buy_1", "buy_5", "buy_30", "buy_100"]:
        price_map = {
            "buy_1": ("1 запрос", 1, "20₽"),
            "buy_5": ("5 запросов", 5, "100₽"),
            "buy_30": ("30 запросов", 30, "150₽"),
            "buy_100": ("100 запросов", 100, "250₽"),
        }
        title, amount, price = price_map[call.data]
        user["private_requests"] += amount
        bot.answer_callback_query(call.id, "✅ Начислено")
        bot.send_message(
            call.message.chat.id,
            f"💳 Выбран тариф: <b>{title}</b>\n"
            f"💰 Цена: <b>{price}</b>\n\n"
            f"Для оплаты/подтверждения отпиши: {SUPPORT}\n"
            f"Тестово начислено: {amount} приватных запросов.",
            parse_mode="HTML",
            reply_markup=back_kb()
        )

    elif call.data == "profile":
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            "👤 <b>Профиль</b>\n\n"
            f"📝 Имя: {user['name']}\n"
            f"📅 Дата регистрации: {user['reg_date']}\n"
            f"📊 Всего запросов: {user['total_requests']}\n"
            f"💎 Приватных запросов: {user['private_requests']}",
            parse_mode="HTML",
            reply_markup=back_kb()
        )

    elif call.data == "free_requests":
        bot.answer_callback_query(call.id)
        pending_user_input[uid] = {"mode": "free"}
        bot.send_message(
            call.message.chat.id,
            "🎁 <b>Бесплатные запросы</b>\n\n"
            "Введи данные в формате:\n"
            "<code>@username 10 причина</code>",
            parse_mode="HTML",
            reply_markup=back_kb()
        )

    elif call.data == "private_requests":
        bot.answer_callback_query(call.id)
        if user["private_requests"] <= 0:
            return bot.send_message(
                call.message.chat.id,
                "❌ У тебя нет приватных запросов.\nКупи их в разделе 🔑 Купить private key",
                reply_markup=back_kb()
            )

        pending_user_input[uid] = {"mode": "private"}
        bot.send_message(
            call.message.chat.id,
            f"💎 <b>Приватные запросы</b>\n\n"
            f"Доступно: <b>{user['private_requests']}</b>\n\n"
            "Введи данные в формате:\n"
            "<code>@username 5 причина</code>",
            parse_mode="HTML",
            reply_markup=back_kb()
        )

    elif call.data == "support":
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            f"🛠 <b>Поддержка</b>\n\n{SUPPORT}",
            parse_mode="HTML",
            reply_markup=back_kb()
        )

    elif call.data.startswith("approve:"):
        if call.from_user.id != ADMIN_ID:
            return bot.answer_callback_query(call.id, "Нет доступа")

        req_id = call.data.split(":", 1)[1]
        req = admin_requests.get(req_id)
        if not req:
            return bot.answer_callback_query(call.id, "Заявка не найдена")

        bot.answer_callback_query(call.id, "✅ Одобрено")
        bot.send_message(
            req["chat_id"],
            f"✅ <b>Заявка одобрена администратором</b>\n\n"
            f"🎯 Цель: {req['target']}\n"
            f"📦 Запросов: {req['count']}\n"
            f"📝 Причина: {req['reason']}\n\n"
            f"⏳ Начинаю выполнение...",
            parse_mode="HTML"
        )

        for i in range(1, req["count"] + 1):
            time.sleep(1)
            bot.send_message(
                req["chat_id"],
                f"✅ Цель: {req['target']}\n"
                f"📊 Проверка: в процессе\n"
                f"⚡ Выполнено: {i}/{req['count']}"
            )

        req_user = get_user(req["user_id"])
        req_user["total_requests"] += req["count"]
        if req["mode"] == "private":
            req_user["private_requests"] -= req["count"]

        bot.send_message(
            req["chat_id"],
            f"🏁 <b>Готово</b>\n\n"
            f"🎯 Цель: {req['target']}\n"
            f"📦 Выполнено: {req['count']}",
            parse_mode="HTML",
            reply_markup=main_menu_kb()
        )
        admin_requests.pop(req_id, None)

    elif call.data.startswith("decline:"):
        if call.from_user.id != ADMIN_ID:
            return bot.answer_callback_query(call.id, "Нет доступа")

        req_id = call.data.split(":", 1)[1]
        req = admin_requests.get(req_id)
        if not req:
            return bot.answer_callback_query(call.id, "Заявка не найдена")

        bot.answer_callback_query(call.id, "❌ Отклонено")
        bot.send_message(req["chat_id"], "❌ Заявка отклонена администратором", reply_markup=main_menu_kb())
        admin_requests.pop(req_id, None)


@bot.message_handler(func=lambda m: True)
def handle_text(message):
    if not check_sub(message.from_user.id):
        return bot.send_message(message.chat.id, "❌ Подпишись на канал @pizzabotinfo", reply_markup=sub_kb())

    uid = str(message.from_user.id)
    state = pending_user_input.get(uid)
    if not state:
        return

    parts = message.text.split(maxsplit=2)
    if len(parts) < 2 or not parts[0].startswith("@"):
        return bot.send_message(message.chat.id, "❌ Пример: <code>@user 10 причина</code>", parse_mode="HTML")

    target = parts[0]

    try:
        count = int(parts[1])
    except:
        return bot.send_message(message.chat.id, "❌ Количество должно быть числом")

    if count < 1:
        return bot.send_message(message.chat.id, "❌ Минимум 1 запрос")

    reason = parts[2] if len(parts) > 2 else "—"

    user = get_user(message.from_user.id, message.from_user.full_name, message.from_user.username or "")

    if state["mode"] == "private" and count > user["private_requests"]:
        return bot.send_message(
            message.chat.id,
            f"❌ У тебя только {user['private_requests']} приватных запросов"
        )

    req_id = f"{message.from_user.id}_{int(time.time())}"
    admin_requests[req_id] = {
        "user_id": message.from_user.id,
        "chat_id": message.chat.id,
        "target": target,
        "count": count,
        "reason": reason,
        "mode": state["mode"]
    }

    pending_user_input.pop(uid, None)

    bot.send_message(
        message.chat.id,
        "📋 <b>Заявка отправлена на подтверждение администратору</b>\n\n"
        f"🎯 Цель: {target}\n"
        f"📦 Запросов: {count}\n"
        f"📝 Причина: {reason}",
        parse_mode="HTML"
    )

    bot.send_message(
        ADMIN_ID,
        "📨 <b>Новая заявка</b>\n\n"
        f"👤 От: {message.from_user.full_name}\n"
        f"🎯 Цель: {target}\n"
        f"📦 Запросов: {count}\n"
        f"📝 Причина: {reason}\n"
        f"🔖 Режим: {state['mode']}",
        parse_mode="HTML",
        reply_markup=confirm_request_kb(req_id)
    )


print("PIZZA BOT запущен")
bot.infinity_polling(skip_pending=True)