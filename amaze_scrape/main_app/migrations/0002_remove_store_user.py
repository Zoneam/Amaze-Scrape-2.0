# Generated by Django 4.0.6 on 2023-01-20 02:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='store',
            name='user',
        ),
    ]
