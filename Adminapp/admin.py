from django.contrib import admin
from django.utils.timezone import now
from pytz import timezone
from Accountapp.models import OfferTable

class OfferAdmin(admin.ModelAdmin):
    list_display = ('name', 'startdate', 'enddate', 'is_active')
    readonly_fields = ('is_active',)  # Make field visible but not editable

    def save_model(self, request, obj, form, change):
        current_time = now()
        obj.is_active = obj.startdate <= current_time <= obj.enddate
        super().save_model(request, obj, form, change)

try:
    admin.site.unregister(OfferTable)
except admin.sites.NotRegistered:
    pass

admin.site.register(OfferTable, OfferAdmin)
