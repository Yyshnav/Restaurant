# Accountapp/migrations/0003_add_offer_id.py
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('Accountapp', '0003_alter_itemtable_calories'),
    ]

    operations = [
        migrations.AddField(
            model_name='CarouselTable',
            name='offer_id',
            field=models.ForeignKey(
                to='Accountapp.OfferTable',
                on_delete=models.CASCADE,
                null=True,  # Adjust to null=False if required
            ),
        ),
    ]