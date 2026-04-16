from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("foods", "0002_food_allergens_meallog"),
    ]

    operations = [
        migrations.DeleteModel(
            name="MealLog",
        ),
    ]
