# Generated by Django 4.2.13 on 2024-05-24 02:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_alter_outfit_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="outfit",
            name="image",
            field=models.ImageField(default="outfits/default_img.jpg", upload_to="outfits/"),
        ),
    ]
