# Generated by Django 4.2.13 on 2024-06-15 11:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0021_remove_customer_shoe_size_us"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Seller",
        ),
    ]
