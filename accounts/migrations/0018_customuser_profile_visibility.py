# Generated by Django 4.2.13 on 2024-06-13 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0017_useritemcart"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="profile_visibility",
            field=models.CharField(
                choices=[("public", "Public"), ("private", "Private"), ("followers", "Followers")],
                default="public",
                max_length=20,
            ),
        ),
    ]
