from django.contrib import admin

from wedding.models import City, Family, InvitedGuests

# Register your models here.
admin.site.register(City)
admin.site.register(Family)
admin.site.register(InvitedGuests)
