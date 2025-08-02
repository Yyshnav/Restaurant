# app_name/management/commands/unset_newest.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from Accountapp.models import ItemTable

class Command(BaseCommand):
    help = 'Unset newest flag for items older than 3 days'

    def handle(self, *args, **kwargs):
        threshold_date = timezone.now() - timedelta(days=3)
        updated = ItemTable.objects.filter(created_at__lt=threshold_date, newest=True).update(newest=False)
        self.stdout.write(f"{updated} items updated to newest=False")
