# Generated by Django 4.1.4 on 2022-12-11 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salon_bot', '0010_salon_services'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='Consent_Of_Personal_Data',
            field=models.BooleanField(default=False),
        ),
    ]
