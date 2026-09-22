from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup


def courses_inline_markup(courses: list) -> InlineKeyboardMarkup:
    """Kurslar ro'yxatini inline tugmalar ko'rinishida shakllantirish."""
    keyboard = []
    for course in courses:
        course_id = course.get("id")
        course_name = course.get("name", "Kurs")
        keyboard.append([
            InlineKeyboardButton(
                text=f"📘 {course_name}",
                callback_data=f"course_info_{course_id}"
            )
        ])
    return InlineKeyboardMarkup(keyboard)


def course_detail_markup(course_id: str) -> InlineKeyboardMarkup:
    """Tanlangan kurs ma'lumoti ostidagi tugmalar."""
    keyboard = [
        [
            InlineKeyboardButton(
                text="📝 Kursga yozilish",
                callback_data=f"enroll_course_{course_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="⬅️ Barcha kurslar",
                callback_data="courses_list"
            )
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def phone_share_markup() -> ReplyKeyboardMarkup:
    """Telefon raqam ulashish klaviaturasi."""
    keyboard = [
        [
            KeyboardButton("📱 Telefon raqamni ulashish", request_contact=True)
        ],
        [
            KeyboardButton("❌ Bekor qilish")
        ]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )


def cancel_markup() -> ReplyKeyboardMarkup:
    """Bekor qilish tugmasi."""
    keyboard = [
        [
            KeyboardButton("❌ Bekor qilish")
        ]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )
