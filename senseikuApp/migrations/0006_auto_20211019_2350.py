# Generated by Django 3.1.3 on 2021-10-19 16:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('senseikuApp', '0005_auto_20211014_2128'),
    ]

    operations = [
        migrations.RenameField(
            model_name='schedule',
            old_name='hour',
            new_name='hour_start',
        ),
        migrations.AddField(
            model_name='schedule',
            name='hour_finish',
            field=models.CharField(default='7:30', max_length=100),
        ),
    ]
