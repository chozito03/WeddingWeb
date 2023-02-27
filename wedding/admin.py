from django.contrib import admin

from wedding.models import City, Family, InvitedGuests, Song, Requests, Gifts, New, \
    MealCourse, DrinksCourse, Meal, Drinks, UserProfile

# Register your models here.
admin.site.register(City)
admin.site.register(Family)
admin.site.register(InvitedGuests)
admin.site.register(Song)
admin.site.register(Requests)
admin.site.register(Gifts)
admin.site.register(New)
admin.site.register(MealCourse)
admin.site.register(DrinksCourse)
admin.site.register(Meal)
admin.site.register(Drinks)
admin.site.register(UserProfile)