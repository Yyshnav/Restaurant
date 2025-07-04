# Generated by Django 5.2.3 on 2025-07-02 08:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accountapp', '0008_alter_branchtable_manager'),
    ]

    operations = [
        migrations.AddField(
            model_name='carouseltable',
            name='enddate',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='carouseltable',
            name='startdate',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='carouseltable',
            name='offer_percentage',
            field=models.FloatField(blank=True, default=0.0, null=True),
        ),
        migrations.AlterField(
            model_name='offertable',
            name='enddate',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='offertable',
            name='startdate',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
