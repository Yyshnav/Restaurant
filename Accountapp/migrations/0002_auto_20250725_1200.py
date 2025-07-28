# Accountapp/migrations/0002_create_chatmessage.py
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('Accountapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender_type', models.CharField(choices=[('USER', 'User'), ('DELIVERYBOY', 'DeliveryBoy')], max_length=20)),
                ('message_type', models.CharField(choices=[('TEXT', 'Text'), ('IMAGE', 'Image'), ('AUDIO', 'Audio')], default='TEXT', max_length=10)),
                ('text', models.TextField(blank=True, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='chat/images/')),
                ('audio', models.FileField(blank=True, null=True, upload_to='chat/audio/')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('delivery_boy', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Accountapp.deliveryboytable')),
                ('order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Accountapp.ordertable')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Accountapp.profiletable')),
            ],
            options={
                'db_table': 'Accountapp_chatmessage',
            },
        ),]