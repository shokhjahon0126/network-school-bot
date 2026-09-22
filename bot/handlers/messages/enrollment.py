import logging
import re
import warnings
from telegram import Update
from telegram.warnings import PTBUserWarning
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

# PTBUserWarning ni e'tiborsiz qoldirish (ConversationHandler da CallbackQueryHandler va MessageHandler birga ishlatilganda paydo bo'ladigan xavfsiz ogohlantirish)
warnings.filterwarnings("ignore", category=PTBUserWarning)

from bot.services import get_all_courses, get_course_by_id, submit_lead
from bot.handlers.buttons.courses import (
    phone_share_markup,
    cancel_markup,
    courses_inline_markup,
)
from bot.handlers.buttons.start import menu_buttons

logger = logging.getLogger(__name__)

# Holatlar
FULL_NAME, PHONE_NUMBER = range(2)



def clean_phone_number(raw_phone: str) -> str | None:
    """Telefon raqamini tekshirish va standart formatga keltirish (+998...)."""
    digits = re.sub(r"\D", "", raw_phone)
    if len(digits) == 9:
        return f"+998{digits}"
    elif len(digits) == 12 and digits.startswith("998"):
        return f"+{digits}"
    elif len(digits) >= 10:
        return f"+{digits}"
    return None


async def start_enrollment_from_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Inline '📝 Kursga yozilish' tugmasi bosilganda yozilish jarayonini boshlash."""
    query = update.callback_query
    await query.answer()

    course_id = query.data.replace("enroll_course_", "").strip()
    context.user_data["enroll_course_id"] = course_id

    course = get_course_by_id(course_id, context)
    course_name = course.get("name", "Kurs") if course else "Kurs"

    text = (
        f"📝 <b>'{course_name}' kursiga yozilish</b>\n\n"
        "Iltimos, to‘liq ism va familiyangizni kiriting:\n"
        "<i>(Masalan: Jasur Saidov)</i>"
    )

    # Agar inline xabar bo'lsa, xabarga yangi xabar yuboramiz va reply keyboard chiqaramiz
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=cancel_markup(),
        parse_mode="HTML"
    )
    return FULL_NAME


async def start_enrollment_from_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Asosiy menyudagi '📝 Kursga yozilish' tugmasi bosilganda."""
    courses = get_all_courses(context)

    if courses:
        text = (
            "📝 <b>Kursga yozilish</b>\n\n"
            "Iltimos, qaysi kursga yozilmoqchi ekanligingizni tanlang:"
        )
        markup = courses_inline_markup(courses)
        await update.message.reply_text(
            text=text,
            reply_markup=markup,
            parse_mode="HTML"
        )
        return ConversationHandler.END

    # Agar kurslar topilmasa, to'g'ridan-to'g'ri ism-familiya so'raymiz
    context.user_data["enroll_course_id"] = None
    text = (
        "📝 <b>Kursga yozilish</b>\n\n"
        "Iltimos, to‘liq ism va familiyangizni kiriting:\n"
        "<i>(Masalan: Jasur Saidov)</i>"
    )
    await update.message.reply_text(
        text=text,
        reply_markup=cancel_markup(),
        parse_mode="HTML"
    )
    return FULL_NAME


async def receive_full_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Foydalanuvchi kiritgan ism-familiyani qabul qilish."""
    text = update.message.text.strip()

    if text in ["❌ Bekor qilish", "/cancel"]:
        return await cancel_enrollment(update, context)

    if len(text) < 3:
        await update.message.reply_text(
            "⚠️ Iltimos, haqiqiy ism va familiyangizni kiriting:\n<i>(Masalan: Jasur Saidov)</i>",
            reply_markup=cancel_markup(),
            parse_mode="HTML"
        )
        return FULL_NAME

    context.user_data["enroll_full_name"] = text

    reply_text = (
        f"Rahmat, <b>{text}</b>!\n\n"
        "📱 Endi telefon raqamingizni yuboring:\n"
        "Pastdagi <b>'📱 Telefon raqamni ulashish'</b> tugmasini bosing yoki raqamingizni qo‘lda yozing:"
    )

    await update.message.reply_text(
        text=reply_text,
        reply_markup=phone_share_markup(),
        parse_mode="HTML"
    )
    return PHONE_NUMBER


async def receive_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Foydalanuvchi kiritgan yoki ulashgan telefon raqamini qabul qilish va arizani yuborish."""
    phone_number = None

    if update.message.contact:
        phone_number = update.message.contact.phone_number
        if not phone_number.startswith("+"):
            phone_number = f"+{phone_number}"
    elif update.message.text:
        text = update.message.text.strip()
        if text in ["❌ Bekor qilish", "/cancel"]:
            return await cancel_enrollment(update, context)
        phone_number = clean_phone_number(text)

    if not phone_number:
        await update.message.reply_text(
            "⚠️ Noto‘g‘ri telefon raqami kiritildi.\n\n"
            "Iltimos, pastdagi <b>'📱 Telefon raqamni ulashish'</b> tugmasini bosing "
            "yoki raqamingizni to‘g‘ri formatda yozing (masalan: +998901234567):",
            reply_markup=phone_share_markup(),
            parse_mode="HTML"
        )
        return PHONE_NUMBER

    context.user_data["enroll_phone"] = phone_number

    # Barcha ma'lumotlarni olish
    full_name = context.user_data.get("enroll_full_name", "")
    course_id = context.user_data.get("enroll_course_id")
    branch_data = context.user_data.get("branche_data", {})
    branch_id = branch_data.get("id")
    branch_name = branch_data.get("name", "Tanlanmagan")

    course = get_course_by_id(course_id, context) if course_id else None
    course_name = course.get("name", "Umumiy ariza") if course else "Umumiy ariza"

    username = update.effective_user.username
    note = f"Telegram bot orqali ariza. Username: @{username}" if username else "Telegram bot orqali ariza"

    # API ga POST qilish
    course_ids = [course_id] if course_id else None
    success, message = submit_lead(
        name=full_name,
        phone=phone_number,
        branch_id=branch_id,
        course_ids=course_ids,
        note=note
    )

    if success:
        success_text = (
            "✅ <b>Arizangiz muvaffaqiyatli qabul qilindi!</b>\n\n"
            f"👤 <b>Ism:</b> {full_name}\n"
            f"📞 <b>Telefon:</b> {phone_number}\n"
            f"📚 <b>Kurs:</b> {course_name}\n"
            f"🏢 <b>Filial:</b> {branch_name}\n\n"
            "Tez orada mutaxassislarimiz siz bilan bog‘lanishadi. Rahmat! 😊"
        )
    else:
        logger.warning(f"Lead submit warning: {message}")
        success_text = (
            "✅ <b>Arizangiz qabul qilindi!</b>\n\n"
            f"👤 <b>Ism:</b> {full_name}\n"
            f"📞 <b>Telefon:</b> {phone_number}\n"
            f"📚 <b>Kurs:</b> {course_name}\n\n"
            "Tez orada mutaxassislarimiz siz bilan bog‘lanishadi. Rahmat! 😊"
        )

    # Tozalash
    context.user_data.pop("enroll_course_id", None)
    context.user_data.pop("enroll_full_name", None)
    context.user_data.pop("enroll_phone", None)

    await update.message.reply_text(
        text=success_text,
        reply_markup=menu_buttons(),
        parse_mode="HTML"
    )
    return ConversationHandler.END


async def cancel_enrollment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Arizani bekor qilish."""
    context.user_data.pop("enroll_course_id", None)
    context.user_data.pop("enroll_full_name", None)
    context.user_data.pop("enroll_phone", None)

    await update.message.reply_text(
        "❌ <b>Ariza berish bekor qilindi.</b>",
        reply_markup=menu_buttons(),
        parse_mode="HTML"
    )
    return ConversationHandler.END


def get_enrollment_conversation_handler() -> ConversationHandler:
    """Kursga yozilish uchun ConversationHandler yaratish."""
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_enrollment_from_callback, pattern=r"^enroll_course_"),
            MessageHandler(filters.Text("📝 Kursga yozilish"), start_enrollment_from_menu),
        ],
        states={
            FULL_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_full_name),
            ],
            PHONE_NUMBER: [
                MessageHandler(filters.CONTACT, receive_phone),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_phone),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_enrollment),
            MessageHandler(filters.Text("❌ Bekor qilish"), cancel_enrollment),
        ],
        allow_reentry=True,
        per_message=False,
    )

