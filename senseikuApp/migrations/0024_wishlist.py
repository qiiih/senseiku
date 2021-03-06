# Generated by Django 3.2.7 on 2021-11-16 13:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('senseikuApp', '0023_auto_20211109_1732'),
    ]

    operations = [
        migrations.CreateModel(
            name='Wishlist',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('course_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='senseikuApp.course')),
                ('student_username', models.ForeignKey(db_column='username', default='', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='username')),
            ],
        ),
    ]
