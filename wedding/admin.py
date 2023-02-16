from django.contrib import admin

from wedding.models import City, Family, InvitedGuests, Song

# Register your models here.
admin.site.register(City)
admin.site.register(Family)
admin.site.register(InvitedGuests)
admin.site.register(Song)
