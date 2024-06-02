import subprocess
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Runs the scripts 1_create_item.py, 2_item_image.py, and 3_item_tags.py in order'

    def handle(self, *args, **kwargs):
        commands_to_run = [
            '1_create_item',
            '2_item_image',
            '3_item_tags'
        ]

        for command in commands_to_run:
            self.run_management_command(command)

    def run_management_command(self, command_name):
        result = subprocess.run(['python', 'manage.py', command_name], capture_output=True, text=True)
        self.stdout.write(self.style.SUCCESS(f"Running manage.py {command_name}:\n{result.stdout}"))
        if result.stderr:
            self.stderr.write(self.style.ERROR(result.stderr))
