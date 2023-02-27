from django.contrib.auth.models import User
from django.db.models import Model, CharField, ForeignKey, CASCADE, IntegerField, ManyToManyField, DateTimeField, \
    BooleanField, PositiveSmallIntegerField, TextField, DateField, SET_NULL, OneToOneField
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model


from django.utils import timezone
from datetime import datetime



class City(Model):
    city = CharField(primary_key=True, max_length=64, null=False)
    postcode = IntegerField(null=True)

    class Meta:
        ordering = ['city']

    def __str__(self):
        return self.city


class Family(Model):
    family_name = CharField(primary_key=True, max_length=64, null=False)
    street_name = CharField(max_length=64, null=True)
    city = ForeignKey(City, null=False, on_delete=CASCADE, related_name="city_family")

    class Meta:
        ordering = ['family_name']

    def __str__(self):
        return self.family_name


class InvitedGuests(Model):
    username = CharField(unique=True, max_length=64, null=True)
    first_name = CharField(max_length=64, null=False)
    last_name = CharField(max_length=64, null=False)
    email = CharField(max_length=64, null=True)
    phone_number = IntegerField(null=True)
    family_name = ForeignKey(Family, null=False, on_delete=CASCADE)

    class Meta:
        ordering = ['last_name']

    def __str__(self):
        return self.last_name + " " + self.first_name


class Song(Model):
    name = CharField(max_length=200)
    artist = CharField(max_length=200)
    album = CharField(max_length=200)
    spotify_id = CharField(max_length=200)
    preview_url = CharField(max_length=256, null=True, blank=True)
    external_urls = CharField(max_length=256, null=True, blank=True)
    image_url = CharField(max_length=256, null=True, blank=True)
    created = DateTimeField(auto_now_add=True)
    user = ForeignKey(User, on_delete=CASCADE, null=True, blank=True, related_name='user_song')

    def __str__(self):
        return f'{self.name} {self.artist} {self.created.strftime("%Y-%m-%d %H:%M:%S")}'


class Requests(Model):
    username = ForeignKey(User, null=False, on_delete=CASCADE)
    age = PositiveSmallIntegerField(null=True)
    hotel = BooleanField()
    kids = BooleanField()
    vegetarian_food = BooleanField(null=True)
    takeaway_to_restaurant = BooleanField()
    takeaway_to_home = BooleanField()
    completed = BooleanField(default=False)

    def __str__(self):
        return self.username.username


class Gifts(Model):
    name = CharField(max_length=200)
    image_url = CharField(max_length=200, null=True, blank=True)
    description = TextField(null=True)
    link = CharField(max_length=200)
    sorted_by = ForeignKey(User, on_delete=CASCADE, null=True, blank=True)
    selected = BooleanField(default=False)

    class Meta:
        ordering = ['name']
    def __str__(self):
        return f'{self.name}'


class New(Model):
    name = CharField(max_length=200)
    date = DateField(null=True, blank=True)
    description = TextField(null=True)
    likes = IntegerField(default=0)
    created = DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name}'

"""
class FilledSurvey(Model):
    user = ForeignKey(User, on_delete=CASCADE)
    survey = ForeignKey('Requests', on_delete=CASCADE)

    class Meta:
        unique_together = ('user', 'survey')
"""

class MealCourse(Model):
    name = CharField(max_length=32, null=False, unique=True)

    def __str__(self):
        return f'{self.name}'

class DrinksCourse(Model):
    name = CharField(max_length=32, null=False, unique=True)


    def __str__(self):
        return f'{self.name}'

class Meal(Model):
    name = CharField(max_length=200)
    weight = CharField(max_length=200, null=True, blank=True)
    food_type = ForeignKey(MealCourse, on_delete=CASCADE, null=True, blank=True)
    for_vegetarian = BooleanField(default=False)

    def __str__(self):
        return f'{self.name}'

class Drinks(Model):
    name = CharField(max_length=200)
    volume = CharField(max_length=200, null=True, blank=True)
    drink_type = ForeignKey(DrinksCourse, on_delete=CASCADE, null=True, blank=True)
    only_for_adult = BooleanField(default=False)

    def __str__(self):
        return f'{self.name}'

class UserProfile(Model):
    user = OneToOneField(User, on_delete=CASCADE)
    chosen_drink_1 = ForeignKey(Drinks, null=True, on_delete=CASCADE, blank=True, related_name='drink1')
    chosen_drink_2 = ForeignKey(Drinks, null=True, on_delete=CASCADE, blank=True, related_name='drink2')
    chosen_meal_1 = ForeignKey(Meal, null=True, on_delete=CASCADE, blank=True, related_name='meal1')
    chosen_meal_2 = ForeignKey(Meal, null=True, on_delete=CASCADE, blank=True, related_name='meal2')
    chosen_meal_3 = ForeignKey(Meal,  null=True, on_delete=CASCADE, blank=True, related_name='meal3')
    completed = BooleanField(default=False)

    def __str__(self):
        return f'{self.user}'

