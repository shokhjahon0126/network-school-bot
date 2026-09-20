from telegram import Update
from telegram.ext import ContextTypes


async def qobilyat(u: Update, c: ContextTypes.DEFAULT_TYPE):
    await u.message.reply_text(
        text=(
            "🧠 <b>Sizning qobiliyatingiz</b>\n\n"
            "🎯 Sizga mos yo‘nalish:\n"
            "💻 Dasturlash\n\n"
            "📊 Natija:\n"
            "Dasturlash — 82%\n"
            "Ingliz tili — 64%\n"
            "Dizayn — 41%\n\n"
            "📝 Batafsil test tez orada qo‘shiladi."
        ),
        parse_mode="HTML"
    )