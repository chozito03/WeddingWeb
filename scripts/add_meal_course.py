from wedding.models import *
import csv
import time
def run():
    MealCourse.objects.all().delete()
    Meal.objects.all().delete()


    count_meal = 0
    with open('data/Meal_Course.csv', encoding="UTF-8") as file:
        reader = csv.reader(file, delimiter=';')  # otevřeme csv soubor

        header = next(reader)  # první řádek je hlavička tabulky

        for row in reader:     # pro další řádky
            name = row[0].strip()
            weight = row[1].strip()
            food_type = row[2].strip()
            for_vegetarian = row[3].strip()

            food_type_set = MealCourse.objects.filter(name=food_type)
            if not food_type_set:
                new_food_type = MealCourse.objects.create(
                    name=food_type
                )
                print(f"Do tabulky MealCourse vložen nový druh jídla '{name}'")
                new_food_type.save

            new_meal = Meal.objects.create(
                name=name,
                weight=weight,
                food_type=MealCourse.objects.get(name=row[2].strip()),
                for_vegetarian=for_vegetarian
            )
            print(f"Do tabulky Meal vloženo nové jídlo '{name}'")
            count_meal += 1
            new_meal.save()
    print(f"Konec skriptu 'add_meal_course', bylo přidáno {count_meal} nových jídel.")