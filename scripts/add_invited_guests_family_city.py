from django.db import models
from wedding.models import *
import csv
import time
def run():
    InvitedGuests.objects.all().delete()
    Family.objects.all().delete()
    City.objects.all().delete()

    count_guests = 0
    with open('data/InvitedGuests.csv', encoding="UTF-8") as file:
        reader = csv.reader(file, delimiter=';')  # otevřeme csv soubor

        header = next(reader)  # první řádek je hlavička tabulky

        for row in reader:     # pro další řádky
            username = row[0].strip()
            first_name = row[1].strip()
            last_name = row[2].strip()
            email = row[3].strip()
            phone_number = row[4].strip()
            family_name = row[5].strip()
            street_name = row[6].strip()
            city = row[7].strip()
            postcode = row[8].strip()

            city_set = City.objects.filter(city=city)
            if not city_set:
                new_city = City.objects.create(
                    city=city,
                    postcode=postcode
                )
                print(f"Do tabulky City vloženo nové město '{city}'")
                new_city.save

            family_set = Family.objects.filter(family_name=family_name)
            if not family_set:
                new_family = Family.objects.create(
                    family_name=family_name,
                    street_name=street_name,
                    city=City.objects.get(city=row[7].strip()),
                )
                print(f"Do tabulky Family vložena nová rodina '{family_name}'")
                new_family.save

            new_guest = InvitedGuests.objects.create(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=phone_number,
                family_name=Family.objects.get(family_name=row[5].strip()),
            )
            print(f"Do tabulky InvitedGuests vložen nový host '{username}'")
            count_guests += 1
            new_guest.save()
    print(f"Konec skriptu 'add_invited_guests_family_city', bylo přidáno {count_guests} nových hostů.")