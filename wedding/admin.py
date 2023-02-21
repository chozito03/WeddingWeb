from django.contrib import admin

from wedding.models import City, Family, InvitedGuests, Song, Requests, Gifts, New

# Register your models here.
admin.site.register(City)
admin.site.register(Family)
admin.site.register(InvitedGuests)
admin.site.register(Song)
admin.site.register(Requests)
admin.site.register(Gifts)
admin.site.register(New)
