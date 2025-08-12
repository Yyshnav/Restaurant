# management/commands/deactivate_expired_coupons.py

from django.core.management.base import BaseCommand
from Accountapp.models import CouponTable
from datetime import date, datetime

class Command(BaseCommand):
    help = 'Deactivate expired coupons'

    def handle(self, *args, **kwargs):
        today = date.today()
        coupons = CouponTable.objects.all()
        for coupon in coupons:
            try:
                if coupon.valid_to:
                    valid_to_date = datetime.strptime(coupon.valid_to, "%Y-%m-%d").date()
                    if today > valid_to_date and coupon.is_active:
                        coupon.is_active = False
                        coupon.save()
                        self.stdout.write(f"Deactivated expired coupon: {coupon.code}")
            except Exception as e:
                self.stdout.write(f"Error for coupon {coupon.code}: {e}")
