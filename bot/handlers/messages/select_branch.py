from telegram import Update
from telegram.ext import ContextTypes
from bot.handlers.buttons.start import menu_buttons


async def select_branch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    branch_name = text.replace("🏢", "").strip()

    branches = context.bot_data.get("branches", [])
    selected_branch = next(
        (b for b in branches if b.get("name") == branch_name),
        None
    )

    if selected_branch:
        context.user_data["branche_data"] = {
            "id": selected_branch.get("id"),
            "name": selected_branch.get("name"),
        }
    else:
        context.user_data["branche_data"] = {
            "id": None,
            "name": branch_name,
        }
    
    print(context.user_data)
    await update.message.reply_text(
        f"✅ <b>{branch_name}</b> filiali tanlandi!\n\nKerakli bo‘limni tanlang:",
        reply_markup=menu_buttons(),
        parse_mode="HTML",
    )
