from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from electric_services.models import UserProfile


class Command(BaseCommand):
    help = 'Create a test user for testing purposes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='testuser',
            help='Username for the test user',
        )
        parser.add_argument(
            '--email',
            type=str,
            default='test@example.com',
            help='Email for the test user',
        )
        parser.add_argument(
            '--password',
            type=str,
            default='testpass123',
            help='Password for the test user',
        )

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'User "{username}" already exists')
            )
            return

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name='Test',
            last_name='User'
        )

        # Create user profile
        UserProfile.objects.create(
            user=user,
            phone_number='+1234567890',
            address_line_1='123 Test Street',
            city='Test City',
            state_province_region='Test State',
            postal_code='12345',
            country='Test Country'
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created test user:\n'
                f'Username: {username}\n'
                f'Email: {email}\n'
                f'Password: {password}\n'
                f'You can now login and test the booking functionality!'
            )
        ) 