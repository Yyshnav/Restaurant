# Generated by Django 5.2.3 on 2025-07-02 10:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Accountapp', '0011_remove_itemtable_voice_description'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='VoiceDescription',
            new_name='VoiceDescriptionTable',
        ),
    ]
