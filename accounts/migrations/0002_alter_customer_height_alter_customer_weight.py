# Generated by Django 4.2.13 on 2024-05-15 06:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customer",
            name="height",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="customer",
            name="weight",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
