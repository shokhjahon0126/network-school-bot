

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from decouple import config


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)


def build_application() -> Application:
    """Build and configure the Application."""
    application = Application.builder().token(config("TOKEN")).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    return application


def main() -> None:
    """Start the bot in polling mode."""
    application = build_application()
    application.run_polling(allowed_updates=Update.ALL_TYPES)


def run_webhook(
    listen: str | None = None,
    port: int | None = None,
    url_path: str | None = None,
    webhook_url: str | None = None,
    secret_token: str | None = None,
) -> None:
    """Start the bot in webhook mode."""
    application = build_application()

    listen_addr = listen or config("WEBHOOK_LISTEN", default="0.0.0.0")
    port_num = int(port or config("WEBHOOK_PORT", default=8000))
    path_str = url_path or config("WEBHOOK_PATH", default="webhook")
    full_webhook_url = webhook_url or config("WEBHOOK_URL", default="")
    sec_token = secret_token or config("WEBHOOK_SECRET_TOKEN", default=None)

    webhook_kwargs = {
        "listen": listen_addr,
        "port": port_num,
        "url_path": path_str,
        "allowed_updates": Update.ALL_TYPES,
    }
    if full_webhook_url:
        webhook_kwargs["webhook_url"] = full_webhook_url
    if sec_token:
        webhook_kwargs["secret_token"] = sec_token

    application.run_webhook(**webhook_kwargs)

