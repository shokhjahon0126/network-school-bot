import logging
from telegram import Update
from telegram.ext import ContextTypes

from bot.services import get_all_courses, get_course_by_id
from bot.handlers.buttons.courses import courses_inline_markup, course_detail_markup

logger = logging.getLogger(__name__)


async def show_courses(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """'📚 Kurslar' tugmasi bosilganda barcha kurslarni ko'rsatish."""
    courses = get_all_courses(context)

    if not courses:
        await update.message.reply_text(
            "😔 Hozircha mavjud kurslar ro‘yxati topilmadi. Tez orada yangilanadi!",
            parse_mode="HTML"
        )
        return

    text = (
        "📚 <b>Bizning o‘quv markazimiz kurslari</b>\n\n"
        "O‘zingizga qiziq bo‘lgan yo‘nalishni tanlang va batafsil ma’lumotga ega bo‘ling:"
    )
    markup = courses_inline_markup(courses)

    await update.message.reply_text(
        text=text,
        reply_markup=markup,
        parse_mode="HTML"
    )


async def course_detail_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Inline tugmadan tanlangan kurs haqida batafsil ma'lumot berish."""
    query = update.callback_query
    await query.answer()

    course_id = query.data.replace("course_info_", "").strip()
    course = get_course_by_id(course_id, context)

    if not course:
        try:
            await query.edit_message_text(
                "⚠️ Kurs haqida ma’lumot topilmadi.",
                parse_mode="HTML"
            )
        except Exception:
            pass
        return

    course_name = course.get("name", "Kurs")
    text = (
        f"📖 <b>{course_name}</b> kursi\n\n"
        "🎯 <b>Kurs haqida qisqacha:</b>\n"
        "Ushbu kurs zamonaviy talablar asosida tayyorlangan bo‘lib, "
        "sizga sohani chuqur o‘rganish va amaliy ko‘nikmalarga ega bo‘lish imkonini beradi.\n\n"
        "✅ <b>Afzalliklar:</b>\n"
        "• Nazariy va amaliy mashg‘ulotlar\n"
        "• Real loyihalar ustida ishlash va portfolio yaratish\n"
        "• Tajribali mentorlar ko‘magi\n"
        "• Kurs oxirida sertifikat\n\n"
        "Pastdagi <b>'📝 Kursga yozilish'</b> tugmasi orqali hoziroq ro‘yxatdan o‘tishingiz mumkin:"
    )
    markup = course_detail_markup(course_id)

    try:
        await query.edit_message_text(
            text=text,
            reply_markup=markup,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Error in course_detail_callback: {e}")


async def courses_list_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Kurslar ro'yxatiga qaytish callback'i."""
    query = update.callback_query
    await query.answer()

    courses = get_all_courses(context)
    if not courses:
        try:
            await query.edit_message_text(
                "😔 Hozircha mavjud kurslar ro‘yxati topilmadi.",
                parse_mode="HTML"
            )
        except Exception:
            pass
        return

    text = (
        "📚 <b>Bizning o‘quv markazimiz kurslari</b>\n\n"
        "O‘zingizga qiziq bo‘lgan yo‘nalishni tanlang va batafsil ma’lumotga ega bo‘ling:"
    )
    markup = courses_inline_markup(courses)

    try:
        await query.edit_message_text(
            text=text,
            reply_markup=markup,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Error in courses_list_callback: {e}")
