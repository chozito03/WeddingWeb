from django.contrib.auth.models import User
from django.db.models import Model, CharField, ForeignKey, CASCADE, IntegerField, ManyToManyField


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
    surname = CharField(max_length=64, null=False)
    email = CharField(max_length=64, null=True)
    phone_number = IntegerField(null=True)
    family_name = ForeignKey(Family, null=False, on_delete=CASCADE)

    class Meta:
        ordering = ['surname']

    def __str__(self):
        return self.surname + " " + self.first_name
