# Generated by Django 3.2.8 on 2021-11-09 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('senseikuApp', '0021_alter_phone_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='checked_out',
            field=models.BooleanField(default=False),
        ),
    ]
