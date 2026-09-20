from telegram import Update
from telegram.ext import ContextTypes
from bot.models import User

from bot.handlers.buttons.start import menu_buttons

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    user = update.effective_user
    await User.objects.aget_or_create(
        chat_id = user.id,
        username = user.username,
        full_name = user.full_name
    )

    await update.message.reply_text(
        "Salom botga xush kelibsiz!",
        reply_markup=menu_buttons()
    )

