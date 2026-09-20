from telegram import ReplyKeyboardMarkup,KeyboardButton

from telegram import KeyboardButton, ReplyKeyboardMarkup


def menu_buttons():
    keyboard = [
        [
            KeyboardButton("📍 Manzil"),
            KeyboardButton("📚 Kurslar"),
        ],
        [
            KeyboardButton("👨‍🏫 O‘qituvchilar"),
            KeyboardButton("🧠 Qobiliyatimni aniqlash"),
        ],
        [
            KeyboardButton("📝 Kursga yozilish"),
        ],
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        # is_persistent=True,
        input_field_placeholder="Kerakli bo‘limni tanlang..."
    )