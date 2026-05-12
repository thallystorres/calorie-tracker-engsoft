import pgvector.django.vector
from django.db import migrations
from pgvector.django import VectorExtension


class Migration(migrations.Migration):

    dependencies = [
        ('foods', '0004_alter_food_kcal_per_100g'),
    ]

    operations = [
        VectorExtension(),
        migrations.AddField(
            model_name='food',
            name='embedding',
            field=pgvector.django.vector.VectorField(blank=True, dimensions=768, null=True),
        ),
    ]
