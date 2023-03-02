from wedding.models import *
import csv
import time
def run():
    DrinksCourse.objects.all().delete()
    Drinks.objects.all().delete()


    count_drink = 0
    with open('data/Drinks_Course.csv', encoding="UTF-8") as file:
        reader = csv.reader(file, delimiter=';')  # otevřeme csv soubor

        header = next(reader)  # první řádek je hlavička tabulky

        for row in reader:     # pro další řádky
            name = row[0].strip()
            volume = row[1].strip()
            drink_type = row[2].strip()
            only_for_adult = row[3].strip()

            drink_type_set = DrinksCourse.objects.filter(name=drink_type)
            if not drink_type_set:
                new_drink_type = DrinksCourse.objects.create(
                    name=drink_type
                )
                print(f"Do tabulky DrinksCourse vložen nový druh pití '{name}'")
                new_drink_type.save

            new_drink = Drinks.objects.create(
                name=name,
                volume=volume,
                drink_type=DrinksCourse.objects.get(name=row[2].strip()),
                only_for_adult=only_for_adult
            )
            print(f"Do tabulky Drinks vloženo nové pití '{name}'")
            count_drink += 1
            new_drink.save()
    print(f"Konec skriptu 'add_drinks_course', bylo přidáno {count_drink} nových pití.")