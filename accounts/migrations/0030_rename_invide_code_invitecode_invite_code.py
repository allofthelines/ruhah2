# Generated by Django 4.2.13 on 2024-07-05 00:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0029_invitecode"),
    ]

    operations = [
        migrations.RenameField(
            model_name="invitecode",
            old_name="invide_code",
            new_name="invite_code",
        ),
    ]
