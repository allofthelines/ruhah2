# Generated by Django 4.2.13 on 2024-05-12 06:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("studio", "0002_item_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="item",
            name="itemid",
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AlterField(
            model_name="item",
            name="name",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
