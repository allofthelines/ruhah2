# Generated by Django 4.2.13 on 2024-06-30 15:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("box", "0026_remove_ticket_colortype"),
    ]

    operations = [
        migrations.AddField(
            model_name="ticket",
            name="filter_liked",
            field=models.CharField(
                choices=[("no_filter", "no filter"), ("liked_only", "liked only")], default="no_filter", max_length=30
            ),
        ),
    ]
