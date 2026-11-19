from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import getpass

class Command(BaseCommand):
    help = 'Safely initializes or prompts for an administrator superuser account without hardcoded insecure credentials.'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default='admin', help='Superuser username (default: admin)')
        parser.add_argument('--email', type=str, default='admin@marketdatabank.local', help='Superuser email')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f"User '{username}' already exists."))
            return

        self.stdout.write(f"Creating superuser '{username}' ({email})...")
        self.stdout.write("Please run 'python manage.py createsuperuser' or enter a secure password now:")
        
        # In non-interactive environments, we set an unusable password and instruct to use changepassword
        user = User.objects.create_superuser(
            username=username,
            email=email
        )
        user.set_unusable_password()
        user.save()
        self.stdout.write(self.style.SUCCESS(
            f"Superuser '{username}' created with an initial locked password for security.\n"
            f"To set your personal password, run:\n"
            f"  python manage.py changepassword {username}"
        ))

