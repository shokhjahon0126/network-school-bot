from telegram import Update
from telegram.ext import ContextTypes

from bot.models import User
from bot.services import fetch_markaz_data
from bot.handlers.buttons.start import menu_buttons, branches_buttons


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await User.objects.aget_or_create(
        chat_id=user.id,
        username=user.username,
        full_name=user.full_name
    )

    data = fetch_markaz_data()
    branches = data.get('branches', [])
    courses = data.get('courses', [])

    if branches:
        context.bot_data["branches"] = branches
    if courses:
        context.bot_data["courses"] = courses

    cached_branches = context.bot_data.get("branches", [])
    reply_markup = branches_buttons(cached_branches) if cached_branches else menu_buttons()

    await update.message.reply_text(
        "👋 Salom, botga xush kelibsiz!\n\n🏢 Iltimos, filiallardan birini tanlang:",
        reply_markup=reply_markup
    )


