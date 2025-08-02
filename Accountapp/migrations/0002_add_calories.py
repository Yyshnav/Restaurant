# Accountapp/migrations/0002_add_calories.py
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('Accountapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ItemTable',
            name='calories',
            field=models.IntegerField(blank=True, null=True),  # Adjust based on model
        ),
    ]