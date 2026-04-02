import telebot
from telebot import types
import json
import os
import random
import string

TOKEN = "8726545877:AAFXOrf351lpQKG4Mxd2WNxrAqZuJIQc1YI"
ADMIN_ID = 7738822030
LAUNCHER_URL = "https://t.me/br2testhubgames/3"

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

DATA_FILE = "data.json"

# состояния для админа
admin_states = {}


# =========================
# utils
# =========================
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"users": {}, "complaints": {}}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def get_user(data, user_id):
    user_id = str(user_id)
    if user_id not in data["users"]:
        data["users"][user_id] = {
            "status": "new",            # new / pending / approved / rejected
            "nickname": "",
            "password": "",
            "username": "",
            "first_name": "",
            "application_sent": False
        }
    return data["users"][user_id]


def generate_test_nickname():
    parts = [
        "fire", "dark", "fast", "wolf", "storm", "adar", "acar", "adse",
        "light", "nova", "zero", "flash", "blade", "frost", "ghost",
        "drift", "spark", "shadow", "sky", "rage"
    ]
    return f"test_{random.choice(parts)}"


def generate_password(length=5):
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))


# =========================
# keyboards
# =========================
def start_kb():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("Подать заявку", callback_data="apply"))
    return kb


def admin_kb(user_id):
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("✅ Одобрить", callback_data=f"approve_{user_id}"),
        types.InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{user_id}")
    )
    return kb


def approved_user_kb():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("Скачать launcher ⚡", url=LAUNCHER_URL))
    kb.add(types.InlineKeyboardButton("Оставить жалобу на обновление", callback_data="leave_complaint"))
    kb.add(types.InlineKeyboardButton("Ваши текущие жалобы", callback_data="my_complaints"))
    kb.add(types.InlineKeyboardButton("Запрос на выдачу игровых данных", callback_data="game_data_request"))
    return kb


def complaint_admin_kb(user_id, complaint_index):
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(
        "✉️ Ответить",
        callback_data=f"replycomplaint_{user_id}_{complaint_index}"
    ))
    return kb


# =========================
# messages
# =========================
def send_welcome(chat_id):
    text = (
        "👋 Привет! Добро пожаловать в закрытое бета-тестирование 2! "
        "Здесь ты можешь подать заявку на участие.\n\n"
        "🔍 Мы проверим твой аккаунт и сообщим, если всё в порядке. "
        "Просто нажми кнопку ниже!"
    )
    bot.send_message(chat_id, text, reply_markup=start_kb())


def send_approved_message(user_id, nickname, password):
    text = (
        "Добро пожаловать на закрытое бета-тестирование 2!\n\n"
        "Ваши данные\n\n"
        f"Nick-name : <code>{nickname}</code>\n"
        f"Пароль : <code>{password}</code>"
    )
    bot.send_message(user_id, text, reply_markup=approved_user_kb())


# =========================
# handlers
# =========================
@bot.message_handler(commands=["start"])
def start(message):
    data = load_data()
    user = get_user(data, message.from_user.id)
    user["username"] = message.from_user.username or ""
    user["first_name"] = message.from_user.first_name or ""
    save_data(data)

    send_welcome(message.chat.id)


@bot.message_handler(commands=["msgall"])
def msgall_command(message):
    if message.from_user.id != ADMIN_ID:
        return

    text = message.text.replace("/msgall", "", 1).strip()
    if not text:
        bot.reply_to(message, "Использование: /msgall текст сообщения")
        return

    data = load_data()
    users = data.get("users", {})

    sent_count = 0
    failed_count = 0

    for user_id in users.keys():
        try:
            bot.send_message(int(user_id), f"📢 Сообщение от администрации:\n\n{text}")
            sent_count += 1
        except Exception:
            failed_count += 1

    bot.reply_to(
        message,
        f"✅ Рассылка завершена.\n\nОтправлено: {sent_count}\nНе удалось: {failed_count}"
    )


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    data = load_data()
    user_id = str(call.from_user.id)
    user = get_user(data, call.from_user.id)

    # =========================
    # apply
    # =========================
    if call.data == "apply":
        if user["status"] == "pending":
            bot.answer_callback_query(call.id, "Заявка уже отправлена")
            return

        if user["status"] == "approved":
            bot.answer_callback_query(call.id, "Вы уже одобрены")
            return

        user["status"] = "pending"
        user["application_sent"] = True
        user["username"] = call.from_user.username or ""
        user["first_name"] = call.from_user.first_name or ""
        save_data(data)

        username_text = f"@{call.from_user.username}" if call.from_user.username else "нет"
        admin_text = (
            "📥 <b>Новая заявка на ЗБТ 2</b>\n\n"
            f"👤 Имя: {call.from_user.first_name or 'Не указано'}\n"
            f"🆔 ID: <code>{call.from_user.id}</code>\n"
            f"🔗 Username: {username_text}"
        )

        try:
            bot.send_message(ADMIN_ID, admin_text, reply_markup=admin_kb(call.from_user.id))
        except Exception:
            pass

        try:
            bot.edit_message_text(
                "✅ Ваша заявка отправлена администрации. Ожидайте решения.",
                call.message.chat.id,
                call.message.message_id
            )
        except Exception:
            bot.send_message(call.message.chat.id, "✅ Ваша заявка отправлена администрации. Ожидайте решения.")

        bot.answer_callback_query(call.id, "Заявка отправлена")
        return

    # =========================
    # approve
    # =========================
    if call.data.startswith("approve_"):
        if call.from_user.id != ADMIN_ID:
            bot.answer_callback_query(call.id, "Нет доступа")
            return

        target_user_id = call.data.split("_", 1)[1]
        target_user = get_user(data, target_user_id)

        if target_user["status"] == "approved":
            bot.answer_callback_query(call.id, "Уже одобрено")
            return

        nickname = generate_test_nickname()
        password = generate_password(5)

        target_user["status"] = "approved"
        target_user["nickname"] = nickname
        target_user["password"] = password
        save_data(data)

        try:
            send_approved_message(int(target_user_id), nickname, password)
        except Exception:
            pass

        try:
            bot.edit_message_text(
                (
                    "✅ <b>Заявка одобрена</b>\n\n"
                    f"🆔 ID: <code>{target_user_id}</code>\n"
                    f"Nick-name: <code>{nickname}</code>\n"
                    f"Пароль: <code>{password}</code>"
                ),
                call.message.chat.id,
                call.message.message_id
            )
        except Exception:
            bot.send_message(
                call.message.chat.id,
                (
                    "✅ <b>Заявка одобрена</b>\n\n"
                    f"🆔 ID: <code>{target_user_id}</code>\n"
                    f"Nick-name: <code>{nickname}</code>\n"
                    f"Пароль: <code>{password}</code>"
                )
            )

        bot.answer_callback_query(call.id, "Одобрено")
        return

    # =========================
    # reject
    # =========================
    if call.data.startswith("reject_"):
        if call.from_user.id != ADMIN_ID:
            bot.answer_callback_query(call.id, "Нет доступа")
            return

        target_user_id = call.data.split("_", 1)[1]
        target_user = get_user(data, target_user_id)
        target_user["status"] = "rejected"
        save_data(data)

        try:
            bot.send_message(
                int(target_user_id),
                "⚠ К сожалению, ваш аккаунт не подходит для участия в ЗБТ 2."
            )
        except Exception:
            pass

        try:
            bot.edit_message_text(
                (
                    "❌ <b>Заявка отклонена</b>\n\n"
                    f"🆔 ID: <code>{target_user_id}</code>"
                ),
                call.message.chat.id,
                call.message.message_id
            )
        except Exception:
            bot.send_message(
                call.message.chat.id,
                (
                    "❌ <b>Заявка отклонена</b>\n\n"
                    f"🆔 ID: <code>{target_user_id}</code>"
                )
            )

        bot.answer_callback_query(call.id, "Отклонено")
        return

    # =========================
    # leave complaint
    # =========================
    if call.data == "leave_complaint":
        if user["status"] != "approved":
            bot.answer_callback_query(call.id, "Сначала нужно получить одобрение")
            return

        msg = bot.send_message(call.message.chat.id, "✍ Напишите вашу жалобу на обновление одним сообщением:")
        bot.register_next_step_handler(msg, save_complaint)
        bot.answer_callback_query(call.id)
        return

    # =========================
    # my complaints
    # =========================
    if call.data == "my_complaints":
        if user["status"] != "approved":
            bot.answer_callback_query(call.id, "Сначала нужно получить одобрение")
            return

        complaints = data.get("complaints", {}).get(user_id, [])
        if not complaints:
            text = "Ваши текущие жалобы:\n\nПока жалоб нет."
        else:
            text = "Ваши текущие жалобы:\n\n"
            for i, complaint in enumerate(complaints, start=1):
                text += f"{i}. {complaint.get('text', '')}\n"

        bot.send_message(call.message.chat.id, text)
        bot.answer_callback_query(call.id)
        return

    # =========================
    # game data request
    # =========================
    if call.data == "game_data_request":
        if user["status"] != "approved":
            bot.answer_callback_query(call.id, "Сначала нужно получить одобрение")
            return

        bot.send_message(
            call.message.chat.id,
            "✅ Заявка на выдачу донат валюты а также виртов подана."
        )

        try:
            bot.send_message(
                ADMIN_ID,
                (
                    "📨 <b>Новый запрос на выдачу игровых данных</b>\n\n"
                    f"🆔 ID: <code>{user_id}</code>\n"
                    f"👤 Nick-name: <code>{user.get('nickname', '-')}</code>"
                )
            )
        except Exception:
            pass

        bot.answer_callback_query(call.id, "Заявка отправлена")
        return

    # =========================
    # reply to complaint
    # =========================
    if call.data.startswith("replycomplaint_"):
        if call.from_user.id != ADMIN_ID:
            bot.answer_callback_query(call.id, "Нет доступа")
            return

        parts = call.data.split("_")
        if len(parts) < 3:
            bot.answer_callback_query(call.id, "Ошибка")
            return

        target_user_id = parts[1]
        complaint_index = int(parts[2])

        admin_states[str(call.from_user.id)] = {
            "state": "replying_complaint",
            "target_user_id": target_user_id,
            "complaint_index": complaint_index
        }

        bot.send_message(
            call.message.chat.id,
            (
                f"✉️ Напишите ответ пользователю <code>{target_user_id}</code>\n"
                f"по жалобе №{complaint_index + 1}:"
            )
        )
        bot.answer_callback_query(call.id, "Введите ответ")
        return


@bot.message_handler(func=lambda message: True, content_types=["text"])
def handle_all_messages(message):
    user_id = str(message.from_user.id)

    # админ отвечает на жалобу
    if message.from_user.id == ADMIN_ID:
        admin_state = admin_states.get(user_id)
        if admin_state and admin_state.get("state") == "replying_complaint":
            target_user_id = admin_state["target_user_id"]
            complaint_index = admin_state["complaint_index"]
            reply_text = message.text.strip()

            data = load_data()

            try:
                bot.send_message(
                    int(target_user_id),
                    (
                        "📩 Ответ от администрации по вашей жалобе:\n\n"
                        f"{reply_text}"
                    )
                )
            except Exception:
                bot.reply_to(message, "❌ Не удалось отправить ответ пользователю.")
                return

            complaints = data.get("complaints", {}).get(target_user_id, [])
            if 0 <= complaint_index < len(complaints):
                complaints[complaint_index]["admin_reply"] = reply_text
                save_data(data)

            admin_states.pop(user_id, None)
            bot.reply_to(message, "✅ Ответ отправлен пользователю.")
            return


def save_complaint(message):
    data = load_data()
    user_id = str(message.from_user.id)
    user = get_user(data, user_id)

    if user["status"] != "approved":
        bot.send_message(message.chat.id, "⚠ У вас нет доступа к этой функции.")
        return

    complaint_text = message.text.strip()
    if not complaint_text:
        bot.send_message(message.chat.id, "⚠ Жалоба не может быть пустой.")
        return

    if "complaints" not in data:
        data["complaints"] = {}

    if user_id not in data["complaints"]:
        data["complaints"][user_id] = []

    complaint_obj = {
        "text": complaint_text,
        "admin_reply": ""
    }

    data["complaints"][user_id].append(complaint_obj)
    complaint_index = len(data["complaints"][user_id]) - 1
    save_data(data)

    bot.send_message(message.chat.id, "✅ Жалоба отправлена.")

    try:
        bot.send_message(
            ADMIN_ID,
            (
                "📢 <b>Новая жалоба на обновление</b>\n\n"
                f"🆔 ID: <code>{user_id}</code>\n"
                f"👤 Nick-name: <code>{user.get('nickname', '-')}</code>\n"
                f"📝 Жалоба: {complaint_text}"
            ),
            reply_markup=complaint_admin_kb(user_id, complaint_index)
        )
    except Exception:
        pass


print("Bot started")
bot.infinity_polling(skip_pending=True)
