# Generated by Django 4.2.13 on 2024-06-16 20:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("studio", "0033_sizeshoeeucategory_item_sizes_shoe_eu"),
    ]

    operations = [
        migrations.CreateModel(
            name="Style",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("style_name", models.CharField(blank=True, max_length=100)),
            ],
        ),
    ]
