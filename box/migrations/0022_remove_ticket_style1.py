# In your migration file
from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('box', '0021_alter_ticket_style2'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ticket',
            name='style1',
        ),
    ]
