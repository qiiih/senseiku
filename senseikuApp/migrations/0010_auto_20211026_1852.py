# Generated by Django 3.1.3 on 2021-10-26 11:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('senseikuApp', '0009_auto_20211024_2145'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='num_meetings',
        ),
        migrations.AlterField(
            model_name='tracker',
            name='username',
            field=models.ForeignKey(db_column='username', default='guest', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='username'),
        ),
    ]
