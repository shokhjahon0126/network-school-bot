from django.core.management.base import BaseCommand
from ...handlers.main import main

class Command(BaseCommand):
    def handle(self, *args, **options):
        main()
        self.stdout.write("Bot to'xtadi!")