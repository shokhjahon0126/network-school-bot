from telegram import Update
from telegram.ext import ContextTypes
import requests
from decouple import config

from bot.models import User

from bot.handlers.buttons.start import menu_buttons, branches_buttons

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    user = update.effective_user
    await User.objects.aget_or_create(
        chat_id = user.id,
        username = user.username,
        full_name = user.full_name
    )

    data = requests.get(
        url=config('MARKAZ_URL')
    )

    branches = []
    if data.status_code == 200:
        branches = data.json().get('branches', [])
        context.bot_data["branches"] = branches

    reply_markup = branches_buttons(branches) if branches else menu_buttons()

    await update.message.reply_text(
        "👋 Salom, botga xush kelibsiz!\n\n🏢 Iltimos, filiallardan birini tanlang:",
        reply_markup=reply_markup
    )

