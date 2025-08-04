from django.core.management.base import BaseCommand
from django.utils.timezone import now
from Accountapp.models import OfferTable

class Command(BaseCommand):
    help = "Auto-updates offer is_active status based on start and end times."

    def handle(self, *args, **kwargs):
        self.stdout.write("\n=== Offer Auto-Update Started ===")

        current_time = now()  # timezone-aware
        self.stdout.write(f"Current Time (UTC): {current_time}")

        offers = OfferTable.objects.all()
        for offer in offers:
            is_active_now = offer.startdate <= current_time <= offer.enddate

            if offer.is_active != is_active_now:
                offer.is_active = is_active_now
                offer.save()
                status_str = "✅ Activated" if is_active_now else "🛑 Deactivated"
                self.stdout.write(f"{status_str}: '{offer.name}' is_active = {is_active_now}")
            else:
                self.stdout.write(f"No change: '{offer.name}' remains is_active = {offer.is_active}")
