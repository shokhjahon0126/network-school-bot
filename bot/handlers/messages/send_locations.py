from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import ContextTypes
from decouple import config

async def locations(update: Update, context: ContextTypes.DEFAULT_TYPE):



    google_maps_url = (
        f"https://www.google.com/maps?q={config('latitude')},{config('longitude')}"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📍 Xaritada ochish",
                url=google_maps_url
            )
        ]
    ])

    await update.message.reply_text(
        "🏫 *Bizning o‘quv markazimiz*\n\n"
        "📍 Sizni markazimizda kutib qolamiz!\n\n"
        "Quyidagi lokatsiya orqali bizni osongina topishingiz mumkin.\n\n"
        "🎓 Sizga qulay va sifatli ta’lim berish uchun "
        "har doim xizmatingizdamiz. 😊",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

    # await update.message.reply_location(
    #     latitude=latitude,
    #     longitude=longitude
    # )