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


def branches_buttons(branches, row_width=2):
    buttons = [
        KeyboardButton(f"🏢 {branch['name']}")
        for branch in branches
        if isinstance(branch, dict) and "name" in branch
    ]
    keyboard = [
        buttons[i : i + row_width]
        for i in range(0, len(buttons), row_width)
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Filialni tanlang..."
    )