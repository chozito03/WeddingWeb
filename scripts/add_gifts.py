from django.db import models
from wedding.models import *
import csv
import time
def run():
    Gifts.objects.all().delete()

    count_gifts = 0
    with open('data/Gifts.csv', encoding="UTF-8") as file:
        reader = csv.reader(file, delimiter=';')  # otevřeme csv soubor

        header = next(reader)  # první řádek je hlavička tabulky

        for row in reader:     # pro další řádky
            name = row[0].strip()
            image_url = row[1].strip()
            description = row[2].strip()
            link = row[3].strip()

            new_gift = Gifts.objects.create(
                name=name,
                image_url=image_url,
                description=description,
                link=link
            )
            print(f"Do tabulky Gifts vložen nový dárek '{name}'")
            count_gifts += 1
            new_gift.save()
    print(f"Konec skriptu 'add_gifts', bylo přidáno {count_gifts} nových darů.")