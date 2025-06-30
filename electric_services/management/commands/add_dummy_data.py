from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from electric_services.models import ServiceCategory, ElectricService, ProductCategory, ElectricProduct
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Add dummy data for testing (services, products, categories)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before adding dummy data',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            ElectricProduct.objects.all().delete()
            ElectricService.objects.all().delete()
            ProductCategory.objects.all().delete()
            ServiceCategory.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing data cleared'))

        # Create Service Categories
        service_categories_data = [
            {
                'name': 'Electrical Installation',
                'description': 'Professional electrical installation services for homes and businesses',
                'icon': 'fas fa-plug',
                'color': '#28a745'
            },
            {
                'name': 'Maintenance & Repair',
                'description': 'Reliable maintenance and repair services to keep your electrical systems running smoothly',
                'icon': 'fas fa-tools',
                'color': '#dc3545'
            },
            {
                'name': 'Emergency Services',
                'description': '24/7 emergency electrical services for urgent situations',
                'icon': 'fas fa-exclamation-triangle',
                'color': '#ffc107'
            },
            {
                'name': 'Inspection & Testing',
                'description': 'Comprehensive electrical inspection and testing services',
                'icon': 'fas fa-clipboard-check',
                'color': '#17a2b8'
            },
            {
                'name': 'Smart Home Setup',
                'description': 'Modern smart home electrical installation and configuration',
                'icon': 'fas fa-home',
                'color': '#6f42c1'
            }
        ]

        service_categories = []
        for cat_data in service_categories_data:
            category, created = ServiceCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            service_categories.append(category)
            if created:
                self.stdout.write(f'Created service category: {category.name}')

        # Create Electric Services
        services_data = [
            {
                'name': 'Complete Home Wiring',
                'description': 'Full electrical wiring installation for new homes or renovations',
                'category': 'Electrical Installation',
                'price': Decimal('2500.00'),
                'duration': '3-5 days'
            },
            {
                'name': 'Circuit Breaker Installation',
                'description': 'Professional circuit breaker panel installation and upgrade',
                'category': 'Electrical Installation',
                'price': Decimal('800.00'),
                'duration': '1-2 days'
            },
            {
                'name': 'Outlet & Switch Installation',
                'description': 'Installation of new electrical outlets and switches',
                'category': 'Electrical Installation',
                'price': Decimal('150.00'),
                'duration': '2-4 hours'
            },
            {
                'name': 'Electrical Troubleshooting',
                'description': 'Diagnose and fix electrical problems in your home or business',
                'category': 'Maintenance & Repair',
                'price': Decimal('120.00'),
                'duration': '2-6 hours'
            },
            {
                'name': 'Light Fixture Installation',
                'description': 'Installation of ceiling fans, chandeliers, and other light fixtures',
                'category': 'Maintenance & Repair',
                'price': Decimal('200.00'),
                'duration': '2-4 hours'
            },
            {
                'name': 'Emergency Power Restoration',
                'description': 'Immediate response for power outages and electrical emergencies',
                'category': 'Emergency Services',
                'price': Decimal('300.00'),
                'duration': '1-4 hours'
            },
            {
                'name': 'Electrical Safety Inspection',
                'description': 'Comprehensive electrical safety inspection and report',
                'category': 'Inspection & Testing',
                'price': Decimal('180.00'),
                'duration': '2-3 hours'
            },
            {
                'name': 'Smart Thermostat Installation',
                'description': 'Installation and setup of smart thermostats and controls',
                'category': 'Smart Home Setup',
                'price': Decimal('250.00'),
                'duration': '2-3 hours'
            }
        ]

        for service_data in services_data:
            category = next(cat for cat in service_categories if cat.name == service_data['category'])
            service, created = ElectricService.objects.get_or_create(
                name=service_data['name'],
                defaults={
                    'description': service_data['description'],
                    'category': category,
                    'price': service_data['price'],
                    'duration': service_data['duration'],
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'Created service: {service.name}')

        # Create Product Categories
        product_categories_data = [
            {
                'name': 'Lighting',
                'description': 'Energy-efficient LED lighting solutions for every space',
                'icon': 'fas fa-lightbulb',
                'color': '#ffc107'
            },
            {
                'name': 'Switches & Outlets',
                'description': 'High-quality electrical switches and outlets for safety and convenience',
                'icon': 'fas fa-toggle-on',
                'color': '#6c757d'
            },
            {
                'name': 'Circuit Protection',
                'description': 'Circuit breakers, fuses, and surge protectors for electrical safety',
                'icon': 'fas fa-shield-alt',
                'color': '#dc3545'
            },
            {
                'name': 'Smart Home',
                'description': 'Smart home devices and automation solutions',
                'icon': 'fas fa-mobile-alt',
                'color': '#17a2b8'
            },
            {
                'name': 'Tools & Equipment',
                'description': 'Professional electrical tools and testing equipment',
                'icon': 'fas fa-wrench',
                'color': '#28a745'
            }
        ]

        product_categories = []
        for cat_data in product_categories_data:
            category, created = ProductCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            product_categories.append(category)
            if created:
                self.stdout.write(f'Created product category: {category.name}')

        # Create Electric Products
        products_data = [
            {
                'name': 'LED Ceiling Light',
                'description': 'Modern 12W LED ceiling light with warm white color temperature',
                'category': 'Lighting',
                'price': Decimal('45.99'),
                'original_price': Decimal('59.99'),
                'condition': 'new',
                'stock_quantity': 50,
                'rating': Decimal('4.5'),
                'is_featured': True
            },
            {
                'name': 'Smart LED Bulb Pack',
                'description': 'Pack of 4 smart LED bulbs with WiFi connectivity and app control',
                'category': 'Lighting',
                'price': Decimal('89.99'),
                'original_price': Decimal('120.00'),
                'condition': 'new',
                'stock_quantity': 25,
                'rating': Decimal('4.8'),
                'is_featured': True
            },
            {
                'name': 'USB Outlet',
                'description': 'Dual USB charging outlet with 2.4A fast charging capability',
                'category': 'Switches & Outlets',
                'price': Decimal('24.99'),
                'condition': 'new',
                'stock_quantity': 100,
                'rating': Decimal('4.3'),
                'is_featured': False
            },
            {
                'name': 'GFCI Outlet',
                'description': 'Ground Fault Circuit Interrupter outlet for bathroom and kitchen safety',
                'category': 'Switches & Outlets',
                'price': Decimal('18.50'),
                'condition': 'new',
                'stock_quantity': 75,
                'rating': Decimal('4.6'),
                'is_featured': False
            },
            {
                'name': 'Circuit Breaker',
                'description': '20A single pole circuit breaker for residential electrical panels',
                'category': 'Circuit Protection',
                'price': Decimal('12.99'),
                'condition': 'new',
                'stock_quantity': 200,
                'rating': Decimal('4.4'),
                'is_featured': False
            },
            {
                'name': 'Surge Protector Strip',
                'description': '8-outlet surge protector with USB ports and 2000 joule protection',
                'category': 'Circuit Protection',
                'price': Decimal('34.99'),
                'original_price': Decimal('45.00'),
                'condition': 'new',
                'stock_quantity': 60,
                'rating': Decimal('4.7'),
                'is_featured': True
            },
            {
                'name': 'Smart Thermostat',
                'description': 'WiFi-enabled smart thermostat with energy saving features',
                'category': 'Smart Home',
                'price': Decimal('199.99'),
                'original_price': Decimal('249.99'),
                'condition': 'new',
                'stock_quantity': 30,
                'rating': Decimal('4.9'),
                'is_featured': True
            },
            {
                'name': 'Smart Door Lock',
                'description': 'Keyless smart door lock with fingerprint and app access',
                'category': 'Smart Home',
                'price': Decimal('299.99'),
                'condition': 'new',
                'stock_quantity': 20,
                'rating': Decimal('4.6'),
                'is_featured': False
            },
            {
                'name': 'Multimeter',
                'description': 'Digital multimeter for voltage, current, and resistance testing',
                'category': 'Tools & Equipment',
                'price': Decimal('89.99'),
                'condition': 'new',
                'stock_quantity': 40,
                'rating': Decimal('4.5'),
                'is_featured': False
            },
            {
                'name': 'Wire Stripper Set',
                'description': 'Professional wire stripper set with multiple gauge sizes',
                'category': 'Tools & Equipment',
                'price': Decimal('29.99'),
                'condition': 'new',
                'stock_quantity': 80,
                'rating': Decimal('4.2'),
                'is_featured': False
            }
        ]

        for product_data in products_data:
            category = next(cat for cat in product_categories if cat.name == product_data['category'])
            product, created = ElectricProduct.objects.get_or_create(
                name=product_data['name'],
                defaults={
                    'description': product_data['description'],
                    'category': category,
                    'price': product_data['price'],
                    'original_price': product_data.get('original_price'),
                    'condition': product_data['condition'],
                    'stock_quantity': product_data['stock_quantity'],
                    'rating': product_data['rating'],
                    'is_featured': product_data['is_featured'],
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'Created product: {product.name}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully added dummy data:\n'
                f'- {len(service_categories)} service categories\n'
                f'- {ElectricService.objects.count()} services\n'
                f'- {len(product_categories)} product categories\n'
                f'- {ElectricProduct.objects.count()} products'
            )
        ) 