# Generated by Django 3.2.8 on 2021-11-09 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('senseikuApp', '0014_auto_20211109_1513'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='total_course_price',
            field=models.IntegerField(default=0),
        ),
    ]
