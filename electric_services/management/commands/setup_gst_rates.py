from django.core.management.base import BaseCommand
from electric_services.models import ProductCategory

class Command(BaseCommand):
    help = 'Set up GST rates for existing product categories'

    def handle(self, *args, **options):
        # Define GST rates for different categories
        gst_mapping = {
            # 5% GST categories
            'ev_chargers': 5,
            'solar_devices': 5,
            'wind_energy': 5,
            'renewable_energy': 5,
            
            # 12% GST categories
            'mobile_phones': 12,
            'smartphones': 12,
            'solar_water_heaters': 12,
            'water_heaters': 12,
            
            # 18% GST categories (default)
            'fans': 18,
            'microwaves': 18,
            'laptops': 18,
            'cables': 18,
            'wires': 18,
            'switches': 18,
            'sockets': 18,
            'lighting': 18,
            'bulbs': 18,
            'led_lights': 18,
            'electrical_tools': 18,
            'safety_equipment': 18,
            
            # 28% GST categories
            'air_conditioners': 28,
            'ac': 28,
            'large_tvs': 28,
            'televisions': 28,
            'premium_audio': 28,
            'speakers': 28,
            'home_theater': 28,
        }
        
        updated_count = 0
        
        for category in ProductCategory.objects.all():
            category_name_lower = category.name.lower()
            gst_rate = 18  # Default rate
            
            # Check if category name matches any of our mappings
            for key, rate in gst_mapping.items():
                if key in category_name_lower:
                    gst_rate = rate
                    break
            
            # Update the category if GST rate is different
            if category.gst_rate != gst_rate:
                category.gst_rate = gst_rate
                category.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Updated "{category.name}" GST rate from {category.gst_rate}% to {gst_rate}%'
                    )
                )
                updated_count += 1
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'Category "{category.name}" already has correct GST rate: {gst_rate}%'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully updated {updated_count} product categories with GST rates'
            )
        ) 