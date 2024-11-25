from django.core.management.base import BaseCommand
from api.mail import send_daily_notification


class Command(BaseCommand):
    def handle(self, *args, **options):
        send_daily_notification()