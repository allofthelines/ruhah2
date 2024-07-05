from django.core.management.base import BaseCommand
from accounts.models import InviteCode
import random

class Command(BaseCommand):
    help = 'Generate new invite codes'

    def add_arguments(self, parser):
        parser.add_argument('num_codes', type=int, help='Number of invite codes to generate')

    def handle(self, *args, **kwargs):
        num_codes = kwargs['num_codes']
        for _ in range(num_codes):
            code = ''.join(random.choices('0123456789', k=10))
            InviteCode.objects.create(invite_code=code)
            self.stdout.write(self.style.SUCCESS(f'Invite code {code} generated'))
