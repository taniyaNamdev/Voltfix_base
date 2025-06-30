from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from electric_services.models import ServiceBooking, ElectricService
import random

class Command(BaseCommand):
    help = 'Add sample bookings for testing the booking history page'

    def handle(self, *args, **options):
        # Get or create test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Created test user: {user.username}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Using existing test user: {user.username}'))
        
        # Get all active services
        services = ElectricService.objects.filter(is_active=True)
        
        if not services.exists():
            self.stdout.write(self.style.ERROR('No active services found. Please run add_dummy_data first.'))
            return
        
        # Sample booking data
        sample_bookings = [
            {
                'service': services[0],
                'status': 'pending',
                'priority': 'normal',
                'address_line_1': '123 Main Street',
                'city': 'Jaipur',
                'state_province': 'Rajasthan',
                'postal_code': '302001',
                'country': 'India',
                'contact_phone': '9829000001',
                'contact_email': 'test@example.com',
                'preferred_date': timezone.now().date() + timedelta(days=7),
                'preferred_time_slot': 'morning',
                'service_description': 'Need electrical repair for my home wiring',
                'property_type': 'residential',
                'payment_method': 'cash',
                'payment_status': 'pending',
                'estimated_cost': 1500.00,
                'booked_at': timezone.now() - timedelta(days=2)
            },
            {
                'service': services[1] if len(services) > 1 else services[0],
                'status': 'confirmed',
                'priority': 'high',
                'address_line_1': '456 Park Avenue',
                'city': 'Jaipur',
                'state_province': 'Rajasthan',
                'postal_code': '302002',
                'country': 'India',
                'contact_phone': '9829000002',
                'contact_email': 'test@example.com',
                'preferred_date': timezone.now().date() + timedelta(days=3),
                'preferred_time_slot': 'afternoon',
                'service_description': 'Emergency electrical installation needed',
                'property_type': 'commercial',
                'payment_method': 'card',
                'payment_status': 'paid',
                'estimated_cost': 2500.00,
                'final_cost': 2400.00,
                'scheduled_date': timezone.now().date() + timedelta(days=3),
                'booked_at': timezone.now() - timedelta(days=5)
            },
            {
                'service': services[2] if len(services) > 2 else services[0],
                'status': 'in_progress',
                'priority': 'normal',
                'address_line_1': '789 Business Center',
                'city': 'Jaipur',
                'state_province': 'Rajasthan',
                'postal_code': '302003',
                'country': 'India',
                'contact_phone': '9829000003',
                'contact_email': 'test@example.com',
                'preferred_date': timezone.now().date() + timedelta(days=1),
                'preferred_time_slot': 'evening',
                'service_description': 'Regular maintenance and inspection',
                'property_type': 'industrial',
                'payment_method': 'bank_transfer',
                'payment_status': 'pending',
                'estimated_cost': 3000.00,
                'scheduled_date': timezone.now().date() + timedelta(days=1),
                'booked_at': timezone.now() - timedelta(days=10)
            },
            {
                'service': services[3] if len(services) > 3 else services[0],
                'status': 'completed',
                'priority': 'normal',
                'address_line_1': '321 Residential Complex',
                'city': 'Jaipur',
                'state_province': 'Rajasthan',
                'postal_code': '302004',
                'country': 'India',
                'contact_phone': '9829000004',
                'contact_email': 'test@example.com',
                'preferred_date': timezone.now().date() - timedelta(days=5),
                'preferred_time_slot': 'morning',
                'service_description': 'Complete electrical system upgrade',
                'property_type': 'residential',
                'payment_method': 'cash',
                'payment_status': 'paid',
                'estimated_cost': 5000.00,
                'final_cost': 4800.00,
                'scheduled_date': timezone.now().date() - timedelta(days=5),
                'completed_date': timezone.now().date() - timedelta(days=3),
                'booked_at': timezone.now() - timedelta(days=15)
            },
            {
                'service': services[4] if len(services) > 4 else services[0],
                'status': 'cancelled',
                'priority': 'normal',
                'address_line_1': '654 Office Building',
                'city': 'Jaipur',
                'state_province': 'Rajasthan',
                'postal_code': '302005',
                'country': 'India',
                'contact_phone': '9829000005',
                'contact_email': 'test@example.com',
                'preferred_date': timezone.now().date() + timedelta(days=14),
                'preferred_time_slot': 'flexible',
                'service_description': 'Lighting installation project',
                'property_type': 'commercial',
                'payment_method': 'card',
                'payment_status': 'refunded',
                'estimated_cost': 1800.00,
                'booked_at': timezone.now() - timedelta(days=20)
            }
        ]
        
        # Create bookings
        created_count = 0
        for booking_data in sample_bookings:
            booking, created = ServiceBooking.objects.get_or_create(
                user=user,
                service=booking_data['service'],
                preferred_date=booking_data['preferred_date'],
                defaults=booking_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'Created booking: {booking.service.name} - {booking.status}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} sample bookings for user {user.username}'
            )
        )
        
        # Show booking statistics
        total_bookings = ServiceBooking.objects.filter(user=user).count()
        pending_bookings = ServiceBooking.objects.filter(user=user, status='pending').count()
        confirmed_bookings = ServiceBooking.objects.filter(user=user, status='confirmed').count()
        completed_bookings = ServiceBooking.objects.filter(user=user, status='completed').count()
        
        self.stdout.write(f'\nBooking Statistics:')
        self.stdout.write(f'- Total Bookings: {total_bookings}')
        self.stdout.write(f'- Pending: {pending_bookings}')
        self.stdout.write(f'- Confirmed: {confirmed_bookings}')
        self.stdout.write(f'- Completed: {completed_bookings}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nYou can now test the booking history page at: http://127.0.0.1:8003/bookings/'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'Login with: username=testuser, password=testpass123'
            )
        ) 