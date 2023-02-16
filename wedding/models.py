from django.contrib.auth.models import User
from django.db.models import Model, CharField, ForeignKey, CASCADE, IntegerField, ManyToManyField, DateTimeField



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
    image_url = CharField(max_length=256, null=True, blank=True)

    def __str__(self):
        return f'{self.name} {self.artist}'

