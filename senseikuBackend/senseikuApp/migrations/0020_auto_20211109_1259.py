# Generated by Django 3.2.8 on 2021-11-09 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('senseikuApp', '0019_transaction_gopay'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedule',
            name='course_id',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='schedule',
            name='finish',
            field=models.BooleanField(default=False),
        ),
    ]