import telebot
from telebot import TeleBot, types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import init_db, add_user, get_user, update_user, get_top_users

# Вызовите инициализацию базы данных при запуске бота
init_db()

# Замените на фактический токен
TOKEN = '7769368074:AAEKrvcUcSJHFLlVnEk6jHsfrXnOVu_8gZg'
bot = telebot.TeleBot(TOKEN)



# Хранилище данных о пользователях
user_data = {}

premium_prices = {
    "1_month": 10000,
    "12_months": 120000,
    "3_months_gift": 30000,
    "6_months_gift": 60000,
    "12_months_gift": 120000
}

stars_prices = {
    "1_stars": 1000,
    "2_stars": 2000,
    "3_stars": 3000,
    "4_stars": 4000,
    "5_stars": 5000
}

admin_settings = {
    "user_admin": "@user_admin"  # Юзернейм администратора, по умолчанию
}

# Начальная минимальная сумма для вывода
MIN_WITHDRAW_AMOUNT = 10000  # Минимальная сумма вывода в суммах (измените по необходимости)


# Сумма за приглашенного пользователя
INVITE_BONUS = 5000  # Измените на нужную сумму

# Telegram ID администратора, куда будет отправляться заявка
ADMIN_ID = 7769368074  # Замените на ID вашего Telegram аккаунта

# Список обязательных каналов
REQUIRED_CHANNELS = [
    {'name': 'Канал 1', 'username': 'channel1', 'active': True},
    {'name': 'Канал 2', 'username': '@channel2', 'active': False},
    {'name': 'Канал 3', 'username': '@channel3', 'active': False},
    {'name': 'Канал 4', 'username': '@channel4', 'active': False},
    {'name': 'Канал 5', 'username': '@channel5', 'active': False},
    {'name': 'Канал 6', 'username': '@channel6', 'active': False},
    {'name': 'Канал 7', 'username': '@channel7', 'active': False},
    {'name': 'Канал 8', 'username': '@channel8', 'active': False},
    {'name': 'Канал 9', 'username': '@channel9', 'active': False},
    {'name': 'Канал 10', 'username': '@channel10', 'active': False}


]


# Функция для создания главного меню
# Функция для создания главного меню
def create_main_menu(user_id):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton("💸 Pul ishlash")
    btn2 = types.KeyboardButton("💰 Hisobim")
    btn3 = types.KeyboardButton("⭐ Premium olish")
    btn4 = types.KeyboardButton("📄 Murojaat")
    btn5 = types.KeyboardButton("🏆 Top reyting")
    btn6 = types.KeyboardButton("⭐ Stars olish")

    # Проверяем, является ли пользователь администратором
    if user_id == ADMIN_ID:  # Проверка, что ID пользователя совпадает с ADMIN_ID
        btn_admin = types.KeyboardButton("🔧 Admin panel")
        keyboard.add(btn_admin)

    keyboard.add(btn1)
    keyboard.add(btn2, btn3)
    keyboard.add(btn4, btn5)
    keyboard.add(btn6)
    return keyboard


# Функция для создания кнопки "Orqaga"
def create_back_button():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back_button = types.KeyboardButton("🔙 Orqaga")
    keyboard.add(back_button)
    return keyboard


# Функция для создания меню подписки
def create_subscription_menu():
    keyboard = types.InlineKeyboardMarkup()
    for channel in REQUIRED_CHANNELS:
        if channel['active']:
            button = types.InlineKeyboardButton(
                f"{channel['name']}",
                url=f"https://t.me/{channel['username'][1:]}")
            keyboard.add(button)
    check_button = types.InlineKeyboardButton(
        "🔄 Obunani tekshirish", callback_data="check_subscription")
    keyboard.add(check_button)
    return keyboard



# Функция для проверки подписки на каналы
def check_subscriptions(user_id):
    not_subscribed = []
    for channel in REQUIRED_CHANNELS:
        if channel['active']:
            try:
                chat_member = bot.get_chat_member(channel['username'], user_id)
                if chat_member.status in ['left', 'kicked']:
                    not_subscribed.append(channel)
            except Exception as e:
                print(f"Obunani tekshirishda xato: {e}")
                not_subscribed.append(channel)
    return not_subscribed



# Начальная точка /start
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id

    # Сохраняем реферальный код, если он есть
    if len(message.text.split()) > 1:
        referrer_id = int(message.text.split()[1])
        user_data[user_id] = {
            'referrer_id': referrer_id,
            'balance': 0,
            'invites': 0
        }
    else:
        user_data[user_id] = {'balance': 0, 'invites': 0}
    
    # Приветственное сообщение и главное меню для пользователя
    bot.send_message(
        message.chat.id,
        "🖥Xush kelibsiz! Asosiy menu.",
        reply_markup=create_main_menu(user_id)  # Передаем user_id в create_main_menu
    )

    # Инициализация данных пользователя, если они ещё не существуют
    if user_id not in user_data:
        user_data[user_id] = {'balance': 0, 'invites': 0}

# Функция завершения регистрации, обновления данных и уведомления пригласившего
def complete_registration(user_id, message):
    referrer_id = user_data.get(user_id, {}).get('referrer_id')

    # Увеличиваем баланс и количество приглашений у пригласившего, если есть
    if referrer_id and referrer_id in user_data:
        user_data[referrer_id]['balance'] += INVITE_BONUS
        user_data[referrer_id]['invites'] += 1
        bot.send_message(
            referrer_id,
            f"🎉 Sizda yangi referal @{message.from_user.username}! Sizning balansingiz {INVITE_BONUS} so'mga oshdi. Takliflaringiz soni: {user_data[referrer_id]['invites']} ta."
        )

    # Отправляем приветственное сообщение и главное меню пользователю
    bot.send_message(message.chat.id,
                     "🖥Xush kelibsiz! Asosiy menu.",
                     reply_markup=create_main_menu())


@bot.message_handler(func=lambda message: message.text == "⭐ Premium olish")
def premium_olish(message):
    # Text for premium options
    text = ("✅ Premium sotib olish uchun narxlar bilan tanishing!\n\n"
            "Profilga kirb:\n"
            "[1] ⭐ 1 Oylik Premium - {} so'm\n"
            "[2] ⭐ 12 Oylik Premium - {} so'm\n\n"
            "Gift:\n"
            "[3] ⭐ 3 Oylik Premium - {} so'm\n"
            "[4] ⭐ 6 Oylik Premium - {} so'm\n"
            "[5] ⭐ 12 Oylik Premium - {} so'm\n\n"
            "⬇️ Quyidagilardan birini tanlang:").format(
                premium_prices["1_month"], premium_prices["12_months"],
                premium_prices["3_months_gift"],
                premium_prices["6_months_gift"],
                premium_prices["12_months_gift"])

    markup = types.InlineKeyboardMarkup(row_width=3)
    
    buttons2 = [
        types.InlineKeyboardButton("⭐ 1", callback_data="1_month"),
        types.InlineKeyboardButton("⭐ 2", callback_data="12_months"),
        types.InlineKeyboardButton("⭐ 3", callback_data="3_months_gift"),
        types.InlineKeyboardButton("⭐ 4", callback_data="6_months_gift"),
        types.InlineKeyboardButton("⭐ 5", callback_data="12_months_gift")
    ]

    markup.add(buttons2[0], buttons2[1], buttons2[2])  # Первый ряд
    markup.add(buttons2[3], buttons2[4])               # Второй ряд

    # Отправляем сообщение с премиум-опциями и встроенной клавиатурой
    bot.send_message(message.chat.id, text, reply_markup=markup)


# Function to show admin contact
@bot.callback_query_handler(
    func=lambda call: call.data in ["1_month", "12_months", "3_months_gift",
                                   "6_months_gift", "12_months_gift"]
)
def show_admin_contact(call):
    # Send the admin's username when a premium button is clicked
    bot.send_message(
        call.message.chat.id,
        f"⭐️ Premium olish uchun admin useri - {admin_settings['user_admin']}"
    )


@bot.message_handler(func=lambda message: message.text == "⭐ Stars olish")
def stars_olish(message):
    # Текст с информацией о покупке звезд и контактом администратора
    text = ("⭐️ Stars olish uchun admin useri - {}\n\n"
            "✅ Stars sotib olish uchun narxlar bilan tanishing:\n\n"
            "[1] ⭐ 50 Stars - {} so'm\n"
            "[2] ⭐ 100 Stars - {} so'm\n"
            "[3] ⭐ 150 Stars - {} so'm\n\n"
            "[4] ⭐ 250 Stars - {} so'm\n\n"
            "[5] ⭐ 350 Stars - {} so'm\n\n"
            "⬇️ Quyidagilardan birini tanlang:").format(
                admin_settings["user_admin"], stars_prices["1_stars"],
                stars_prices["2_stars"], stars_prices["3_stars"],
                stars_prices["4_stars"], stars_prices["5_stars"])

    markup = types.InlineKeyboardMarkup(row_width=3)

    # Создаем кнопки
    buttons = [
        types.InlineKeyboardButton("⭐ 1", callback_data="stars_1_stars"),
        types.InlineKeyboardButton("⭐ 2", callback_data="stars_2_stars"),
        types.InlineKeyboardButton("⭐ 3", callback_data="stars_3_stars"),
        types.InlineKeyboardButton("⭐ 4", callback_data="stars_4_stars"),
        types.InlineKeyboardButton("⭐ 5", callback_data="stars_5_stars"),
    ]

    # Добавляем кнопки двумя рядами
    markup.add(buttons[0], buttons[1], buttons[2])  # Первый ряд
    markup.add(buttons[3], buttons[4])  # Второй ряд
    
    bot.send_message(message.chat.id, text, reply_markup=markup)



# Обработчик показа контакта админа при нажатии на кнопку "Stars"
@bot.callback_query_handler(func=lambda call: call.data in [
    "stars_1_stars", "stars_2_stars", "stars_3_stars", "stars_4_stars",
    "stars_5_stars"
])
def show_admin_contact(call):
    # Выводим контакт админа при нажатии на любую кнопку Stars
    bot.send_message(
        call.message.chat.id,
        f"⭐️ Stars olish uchun admin useri - {admin_settings['user_admin']}")


@bot.message_handler(func=lambda message: message.text == "🔧 Admin panel" and
                     message.from_user.id == ADMIN_ID)
def admin_panel(message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton("Referalga summani o'gartirish",
                                   callback_data="change_bonus"))
    keyboard.add(
        types.InlineKeyboardButton("Premiumga narxlarni o'zgartirish",
                                   callback_data="change_prices"))
    keyboard.add(
        types.InlineKeyboardButton("Globalniy habar yuborish",
                                   callback_data="broadcast_message"))
    keyboard.add(
        types.InlineKeyboardButton(
            "Premium/Starsdagi admin userini o'zgartirish",
            callback_data="change_user_admin"))
    keyboard.add(
        types.InlineKeyboardButton("Stars narxlarini o'zgartirish",
                                   callback_data="change_stars_prices"))
    keyboard.add(
        types.InlineKeyboardButton("Homiy kanallarni ozgartirish",
                                   callback_data="change_channels"))
    keyboard.add(
        types.InlineKeyboardButton("Kanallarni ko'rish",
                                   callback_data="view_channels"))
    keyboard.add(
        types.InlineKeyboardButton("Foydalanuvchi qidirish",
                                   callback_data="view_user"))
    keyboard.add(
        types.InlineKeyboardButton("Minimal yechib olish summasini o'zgartirish",
                                   callback_data="set_min_withdraw"))
    bot.send_message(message.chat.id, "🔧 Admin panel", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == "set_min_withdraw")
def set_min_withdraw(call):
    if call.from_user.id == ADMIN_ID:
        bot.send_message(
            call.message.chat.id,
            f"Hozirgi minimal yechib olish summasi: {MIN_WITHDRAW_AMOUNT} so'm.\n"
            "Yangi minimal yechib olish summasini kiriting:")
        bot.register_next_step_handler(call.message, save_min_withdraw)
    else:
        bot.send_message(call.message.chat.id, "Sizda ushbu amalni bajarish uchun huquq yo'q.")

def save_min_withdraw(message):
    global MIN_WITHDRAW_AMOUNT
    try:
        new_min_amount = int(message.text)
        if new_min_amount > 0:
            MIN_WITHDRAW_AMOUNT = new_min_amount
            bot.send_message(
                message.chat.id,
                f"Minimal yechib olish summasi muvaffaqiyatli o'zgartirildi: {MIN_WITHDRAW_AMOUNT} so'm.")
        else:
            bot.send_message(message.chat.id, "Summani musbat raqam sifatida kiriting.")
    except ValueError:
        bot.send_message(message.chat.id, "Iltimos, faqat raqam kiriting.")


@bot.callback_query_handler(func=lambda call: call.data == "change_user_admin")
def callback_change_user_admin(call):
    bot.send_message(call.message.chat.id,
                     "Yangi admin userini kiriting (например, @new_admin):")
    bot.register_next_step_handler(call.message, set_user_admin)


def set_user_admin(message):
    global admin_settings
    new_admin_user = message.text
    if new_admin_user.startswith("@"):
        admin_settings["user_admin"] = new_admin_user
        bot.send_message(
            message.chat.id,
            f"Admin user muvaffaqiyatli o'zgartirildi: {new_admin_user}")
    else:
        bot.send_message(message.chat.id,
                         "Iltimos, userni '@' bilan kiriting.")


@bot.callback_query_handler(func=lambda call: call.data == "view_user")
def ask_user_id(call):
    bot.send_message(call.message.chat.id, "Iltimos, foydalanuvchi ID kiriting:")
    bot.register_next_step_handler(call.message, get_user_info)

def get_user_info(message):
    try:
        user_id = int(message.text)
        user = get_user(user_id)
        
        if user:
            status = "Blocked" if user[3] == 1 else "Active"
            response = (f"User ID: {user_id}\n"
                        f"Balance: {user[1]} so'm\n"
                        f"Invites: {user[2]}\n"
                        f"Status: {status}\n\n"
                        "Quyidagilardan birini tanlang:\n"
                        "1️⃣ Block\n"
                        "2️⃣ Unblock")
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                               one_time_keyboard=True)
            markup.add("1️⃣ Block", "2️⃣ Unblock")
            bot.send_message(message.chat.id, response, reply_markup=markup)
            bot.register_next_step_handler(message, block_unblock_user, user_id)
        else:
            bot.send_message(message.chat.id, "Bunday foydalanuvchi topilmadi.")
    except ValueError:
        bot.send_message(message.chat.id, "Iltimos, to'g'ri Telegram ID kiriting.")

def block_unblock_user(message, user_id):
    if message.text == "1️⃣ Block":
        update_user(user_id, is_banned=1)
        bot.send_message(message.chat.id, f"Foydalanuvchi {user_id} bloklandi.")
    elif message.text == "2️⃣ Unblock":
        update_user(user_id, is_banned=0)
        bot.send_message(message.chat.id, f"Foydalanuvchi {user_id} unblocked.")
    else:
        bot.send_message(message.chat.id, "Iltimos, to'g'ri variantni tanlang.")


@bot.callback_query_handler(
    func=lambda call: call.data == "change_stars_prices")
def callback_change_stars_prices(call):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton("⭐ 50 Stars narxini o'zgartirish",
                                   callback_data="change_1_star_price"))
    keyboard.add(
        types.InlineKeyboardButton("⭐ 100 Stars narxini o'zgartirish",
                                   callback_data="change_2_stars_price"))
    keyboard.add(
        types.InlineKeyboardButton("⭐ 150 Stars narxini o'zgartirish",
                                   callback_data="change_3_stars_price"))
    keyboard.add(
        types.InlineKeyboardButton("⭐ 250 Stars narxini o'zgartirish",
                                   callback_data="change_4_stars_price"))
    keyboard.add(
        types.InlineKeyboardButton("⭐ 350 Stars narxini o'zgartirish",
                                   callback_data="change_5_stars_price"))
    bot.send_message(
        call.message.chat.id,
        "⭐️ Stars narxlarini o'zgartirish uchun biror bir variantni tanlang.",
        reply_markup=keyboard)


# Обработчик для изменения цены 1 Star
@bot.callback_query_handler(
    func=lambda call: call.data == "change_1_star_price")
def change_1_star_price(call):
    bot.send_message(call.message.chat.id,
                     "Yangi narxni kiriting (masalan, 50000 so'm):")
    bot.register_next_step_handler(call.message, set_1_star_price)


def set_1_star_price(message):
    try:
        new_price = int(message.text)
        stars_prices["1_stars"] = new_price
        bot.send_message(
            message.chat.id,
            f"⭐ 50 Stars narxi muvaffaqiyatli o'zgartirildi: {new_price} so'm")
    except ValueError:
        bot.send_message(message.chat.id, "Iltimos, to'g'ri raqam kiriting.")


# Обработчик для изменения цены 5 Stars
@bot.callback_query_handler(
    func=lambda call: call.data == "change_2_stars_price")
def change_2_stars_price(call):
    bot.send_message(call.message.chat.id,
                     "Yangi narxni kiriting (masalan, 100000 so'm):")
    bot.register_next_step_handler(call.message, set_2_stars_price)


def set_2_stars_price(message):
    try:
        new_price = int(message.text)
        stars_prices["2_stars"] = new_price
        bot.send_message(
            message.chat.id,
            f"⭐ 100 Stars narxi muvaffaqiyatli o'zgartirildi: {new_price} so'm"
        )
    except ValueError:
        bot.send_message(message.chat.id, "Iltimos, to'g'ri raqam kiriting.")


# Обработчик для изменения цены 10 Stars
@bot.callback_query_handler(
    func=lambda call: call.data == "change_3_stars_price")
def change_3_stars_price(call):
    bot.send_message(call.message.chat.id,
                     "Yangi narxni kiriting (masalan, 150000 so'm):")
    bot.register_next_step_handler(call.message, set_3_stars_price)


def set_3_stars_price(message):
    try:
        new_price = int(message.text)
        stars_prices["3_stars"] = new_price
        bot.send_message(
            message.chat.id,
            f"⭐ 150 Stars narxi muvaffaqiyatli o'zgartirildi: {new_price} so'm"
        )
    except ValueError:
        bot.send_message(message.chat.id, "Iltimos, to'g'ri raqam kiriting.")


@bot.callback_query_handler(
    func=lambda call: call.data == "change_4_stars_price")
def change_4_stars_price(call):
    bot.send_message(call.message.chat.id,
                     "Yangi narxni kiriting (masalan, 200000 so'm):")
    bot.register_next_step_handler(call.message, set_4_stars_price)


def set_4_stars_price(message):
    try:
        new_price = int(message.text)
        stars_prices["4_stars"] = new_price
        bot.send_message(
            message.chat.id,
            f"⭐ 250 Stars narxi muvaffaqiyatli o'zgartirildi: {new_price} so'm"
        )
    except ValueError:
        bot.send_message(message.chat.id, "Iltimos, to'g'ri raqam kiriting.")


@bot.callback_query_handler(
    func=lambda call: call.data == "change_5_stars_price")
def change_5_stars_price(call):
    bot.send_message(call.message.chat.id,
                     "Yangi narxni kiriting (masalan, 300000 so'm):")
    bot.register_next_step_handler(call.message, set_5_stars_price)


def set_5_stars_price(message):
    try:
        new_price = int(message.text)
        stars_prices["5_stars"] = new_price
        bot.send_message(
            message.chat.id,
            f"⭐ 350 Stars narxi muvaffaqiyatli o'zgartirildi: {new_price} so'm"
        )
    except ValueError:
        bot.send_message(message.chat.id, "Iltimos, to'g'ri raqam kiriting.")


@bot.callback_query_handler(func=lambda call: call.data == "change_prices")
def set_premium_prices(call):
    global premium_prices  # Access global variable
    bot.send_message(
        call.message.chat.id,
        "Narxlarni vergul bilan ajratib kiriting: 1 oy, 12 oy, 3 oy gift, 6 oy gift, 12 oy gift"
    )
    bot.register_next_step_handler(call.message, update_premium_prices)


def update_premium_prices(message):
    global premium_prices
    try:
        prices = list(map(int, message.text.split(',')))
        if len(prices) == 5:
            premium_prices["1_month"], premium_prices[
                "12_months"], premium_prices["3_months_gift"], premium_prices[
                    "6_months_gift"], premium_prices["12_months_gift"] = prices
            bot.send_message(message.chat.id,
                             "Narxlar muvaffaqiyatli yangilandi.")
        else:
            bot.send_message(message.chat.id,
                             "Iltimos, to'g'ri formatda 5 ta narx kiriting.")
    except ValueError:
        bot.send_message(message.chat.id,
                         "Iltimos, faqat raqamlarni kiriting.")


# Обработчик изменения бонуса для рефералов
@bot.callback_query_handler(func=lambda call: call.data == "change_bonus")
def callback_change_bonus(call):
    bot.send_message(call.message.chat.id, "Yangi summani kiritish:")
    bot.register_next_step_handler(call.message, set_invite_bonus)


def set_invite_bonus(message):
    try:
        new_bonus = int(message.text)
        # Присваиваем новую сумму бонуса
        global INVITE_BONUS
        INVITE_BONUS = new_bonus
        bot.send_message(message.chat.id, f"Summa kiritldi {new_bonus}")
    except ValueError:
        bot.send_message(message.chat.id, "Iltimos son yozing:")


# Обработчик для отправки глобального сообщения
@bot.callback_query_handler(func=lambda call: call.data == "broadcast_message")
def callback_broadcast_message(call):
    bot.send_message(call.message.chat.id, "Globalniy habarni yozing:")
    bot.register_next_step_handler(call.message, broadcast_message)


def broadcast_message(message):
    # Отправка сообщения всем пользователям
    for user_id in user_data.keys():
        bot.send_message(user_id, message.text)
    bot.send_message(message.chat.id, "Habar hammaga yuborildi")


@bot.callback_query_handler(func=lambda call: call.data == "change_channels")
def change_channels(call):
    # Создаем клавиатуру с кнопками-ячейками для каждого канала
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for i, channel in enumerate(REQUIRED_CHANNELS):
        button_text = f"{channel['name']} {'✅' if channel['active'] else '🚫'}"
        callback_data = f"edit_channel_{i}"
        keyboard.add(types.InlineKeyboardButton(button_text, callback_data=callback_data))

    bot.send_message(call.message.chat.id, "Tahrirlash uchun kanalni tanlang:", reply_markup=keyboard)

# Обработчик для редактирования канала на узбекском
@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_channel_"))
def edit_channel(call):
    channel_index = int(call.data.split("_")[-1])
    selected_channel = REQUIRED_CHANNELS[channel_index]

    bot.send_message(
        call.message.chat.id,
        f"Tahrirlanmoqda: {selected_channel['name']} (faol: {selected_channel['active']})\n"
        "Yangi kanal nomini kiriting, format: Nomi, @username (yoki o'chirish uchun bo'sh qoldiring)\n"
        "Masalan: 'Kanal 1, @kanal1'")

    bot.register_next_step_handler(call.message, save_channel_info, channel_index)

def save_channel_info(message, channel_index):
    try:
        if message.text.strip():
            name, username = message.text.split(", ")
            REQUIRED_CHANNELS[channel_index]['name'] = name.strip()
            REQUIRED_CHANNELS[channel_index]['username'] = username.strip()
            REQUIRED_CHANNELS[channel_index]['active'] = True
        else:
            # Деактивировать, если сообщение пустое
            REQUIRED_CHANNELS[channel_index]['active'] = False
    except Exception as e:
        bot.send_message(message.chat.id, f"Xato: {e}")
    bot.send_message(message.chat.id, "Kanal yangilandi!")


# Обработчик для просмотра каналов
@bot.callback_query_handler(func=lambda call: call.data == "view_channels")
def view_channels(call):
    if REQUIRED_CHANNELS:
        channels_info = "\n".join([
            f"Nom: {channel['name']}, Username: {channel['username']}"
            for channel in REQUIRED_CHANNELS
        ])
    else:
        channels_info = "Kanallar mavjud emas."

    bot.send_message(call.message.chat.id,
                     f"🔧 Hozirgi kanallar:\n{channels_info}")


# Обработчик кнопки "Murojaat"
@bot.message_handler(func=lambda message: message.text == "📄 Murojaat")
def handle_request(message):
    bot.send_message(message.chat.id,
                     "📝 Murojaat matnini yuboring:",
                     reply_markup=create_back_button())
    bot.register_next_step_handler(message, receive_request)

# Обработчик получения текста заявки
def receive_request(message):
    user_id = message.from_user.id
    request_text = message.text

    # Проверяем, не нажата ли кнопка "🔙 Orqaga"
    if request_text == "🔙 Orqaga":
        # Возвращаемся в главное меню, если нажата "Orqaga"
        go_back(message)
    else:
        # Отправляем заявку админу
        bot.send_message(ADMIN_ID,
                         f"📝 Murojaat:\n\n{request_text}\n\nUser ID: {user_id}")

        # Подтверждение пользователю
        bot.send_message(
            message.chat.id,
            "Sizning murojaatingiz yuborildi. Tez orada javob olasiz.",
            reply_markup=create_main_menu())

# Обработчик кнопки "Orqaga"
@bot.message_handler(func=lambda message: message.text == "🔙 Orqaga")
def go_back(message):
    bot.send_message(
        message.chat.id,
        "Asosiy menyu:",
        reply_markup=create_main_menu(message.from_user.id)  # Передаем user_id
    )

# обработчик кнопки "Pul ishlash" 
@bot.message_handler(func=lambda message: message.text == "💸 Pul ishlash")
def send_unique_link(message):
    user_id = message.from_user.id
    unique_link = f"https://t.me/refefefef_bot?start={user_id}"  # Замените на username вашего бота
    photo_path = "photo_2024-11-12_13-56-24.jpg"  # Укажите путь к вашему фото
    
    # Создаем кнопку "Ulashish"
    keyboard = InlineKeyboardMarkup()
    share_button = InlineKeyboardButton(
        text="Ulashish", 
        switch_inline_query=unique_link  # Это позволит поделиться сообщением
    )
    keyboard.add(share_button)
    
    # Отправляем фото с сообщением и кнопкой
    with open(photo_path, "rb") as photo:
        bot.send_photo(
            message.chat.id,
            photo,
            caption=(
                "🔗 Sizning taklif havolangiz:\n\n"
                f"{unique_link}\n\n"
                "Yuqoridagi taklif havolangizni do'stlaringizga tarqating va har bir to'liq ro'yxatdan o'tgan "
                "taklifingiz uchun 500 so'm hisobingizga qo'shiladi."
            ),
            reply_markup=keyboard
        )


@bot.message_handler(func=lambda message: message.text == "🏆 Top reyting")
def show_top_users(message):
    # Получаем топ пользователей из базы данных
    top_users = get_top_users(limit=10)
    
    # Формируем сообщение с топом пользователей на узбекском
    if top_users:
        ranking_text = "🏆 Eng yuqori balansga ega 10 foydalanuvchi:\n\n"
        for index, user in enumerate(top_users, start=1):
            ranking_text += f"{index}. ID: {user['user_id']}, Balans: {user['balance']} so'm\n"
    else:
        ranking_text = "Top foydalanuvchilar ro'yxati bo'sh."

    # Отправляем сообщение с топом
    bot.send_message(message.chat.id, ranking_text)


# Обработчик кнопки "Hisobim"
@bot.message_handler(func=lambda message: message.text == "💰 Hisobim")
def show_account_info(message):
    user_id = message.from_user.id
    user_info = user_data.get(user_id, {'balance': 0, 'invites': 0})

    # Сообщение с балансом, ID и количеством приглашений
    account_info = (f"🔑 Sizning ID raqamingiz: {user_id}\n"
                    f"💸 Balansingiz: {user_info['balance']} so'm\n"
                    f"👤 Taklif qilganlar soni: {user_info['invites']} ta")

    # Клавиатура с кнопкой для вывода денег
    keyboard = types.InlineKeyboardMarkup()
    withdraw_button = types.InlineKeyboardButton("💵 Pul chiqarish (Ton)",
                                                 callback_data="withdraw")
    keyboard.add(withdraw_button)

    bot.send_message(message.chat.id, account_info, reply_markup=keyboard)


# Обработчик кнопки "Pul chiqarish"
@bot.callback_query_handler(func=lambda call: call.data == "withdraw")
def callback_withdraw_start(call):
    user_id = call.from_user.id
    user_balance = user_data.get(user_id, {}).get('balance', 0)

    if user_balance < MIN_WITHDRAW_AMOUNT:
        bot.send_message(
            call.message.chat.id,
            f"Sizning balansingiz yechib olish uchun kamida {MIN_WITHDRAW_AMOUNT} so'm bo'lishi kerak.")
    else:
        bot.send_message(call.message.chat.id, "Yechib olish uchun summani kiriting:")
        bot.register_next_step_handler(call.message, handle_withdraw_amount)

def handle_withdraw_amount(message):
    user_id = message.from_user.id
    try:
        amount = int(message.text)
        user_balance = user_data.get(user_id, {}).get('balance', 0)

        if amount < MIN_WITHDRAW_AMOUNT:
            bot.send_message(
                message.chat.id,
                f"Minimal yechib olish summasi {MIN_WITHDRAW_AMOUNT} so'm. Iltimos, katta miqdor kiriting.")
        elif amount > user_balance:
            bot.send_message(
                message.chat.id,
                "Sizning balansingizda yetarli mablag' yo'q. Iltimos, qaytadan urining.")
        else:
            user_data[user_id]['withdraw_amount'] = amount
            bot.send_message(message.chat.id, "TON manzilingizni kiriting:")
            bot.register_next_step_handler(message, handle_withdraw_address)
    except ValueError:
        bot.send_message(message.chat.id, "Iltimos, faqat raqam kiriting.")


def handle_withdraw_address(message):
    user_id = message.from_user.id
    ton_address = message.text

    # Сохраняем TON адрес
    user_data[user_id]['ton_address'] = ton_address
    amount = user_data[user_id].get('withdraw_amount', 0)

    # Отправляем уведомление админу
    bot.send_message(
        ADMIN_ID,
        f"📝 Foydalanuvchi @{message.from_user.username} ({user_id}) pul chiqarishni so'radi:\n"
        f"💵 Miqdori: {amount} so'm\n"
        f"🏦 TON manzili: {ton_address}")

    # Обнуляем баланс и подтверждаем заявку пользователю
    user_data[user_id]['balance'] -= amount
    bot.send_message(
        message.chat.id,
        "Sizning yechib olish so'rovingiz qabul qilindi. Tez orada amalga oshiriladi."
    )


# Запуск бота
bot.polling(none_stop=True)
