from django.core.management.base import BaseCommand
from handlers.main import run_webhook


class Command(BaseCommand):
    help = "Run the Telegram bot in Webhook mode"

    def add_arguments(self, parser):
        parser.add_argument(
            "--listen",
            type=str,
            help="IP address to listen on (e.g. 0.0.0.0 or 127.0.0.1)",
        )
        parser.add_argument(
            "--port",
            type=int,
            help="Port to listen on (e.g. 8000)",
        )
        parser.add_argument(
            "--url-path",
            type=str,
            help="URL path for webhook endpoint (e.g. webhook)",
        )
        parser.add_argument(
            "--webhook-url",
            type=str,
            help="Full Webhook URL (e.g. https://yourdomain.com/webhook)",
        )
        parser.add_argument(
            "--secret-token",
            type=str,
            help="Secret token for verifying Telegram updates",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting bot in webhook mode..."))
        run_webhook(
            listen=options.get("listen"),
            port=options.get("port"),
            url_path=options.get("url_path"),
            webhook_url=options.get("webhook_url"),
            secret_token=options.get("secret_token"),
        )
