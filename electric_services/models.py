from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
import re

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True, default='profile_pics/default.jpg')
    phone_number = models.CharField(max_length=20, blank=True, null=True, unique=True)
    
    # Address Fields
    address_line_1 = models.CharField(max_length=255, blank=True, null=True)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state_province_region = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        if self.phone_number:
            # Clean phone number (remove spaces, dashes, etc.)
            cleaned_phone = re.sub(r'[\s\-\(\)]', '', str(self.phone_number))
            if len(cleaned_phone) < 10:
                raise ValidationError({'phone_number': 'Phone number must be at least 10 digits.'})
            
            # Check if phone number already exists (excluding current instance)
            if UserProfile.objects.filter(phone_number=self.phone_number).exclude(pk=self.pk).exists():
                raise ValidationError({'phone_number': 'This phone number is already registered.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class ServiceCategory(models.Model):
    """Categories for services that VoltFix provides"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='services/', blank=True, null=True, help_text="Service category image")
    icon = models.CharField(max_length=50, help_text="FontAwesome icon class")
    color = models.CharField(max_length=7, default="#007bff", help_text="Hex color code")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Service Categories"

    def __str__(self):
        return self.name

class ElectricService(models.Model):
    """Individual services that VoltFix provides"""
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services')
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Service price")
    duration = models.CharField(max_length=50, help_text="Estimated service duration")
    image = models.ImageField(upload_to='services/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ProductCategory(models.Model):
    """Categories for products that VoltFix sells"""
    GST_RATE_CHOICES = [
        (5, '5% - EV chargers, solar/wind energy devices'),
        (12, '12% - Mobile phones, solar water heaters'),
        (18, '18% - Fans, microwaves, laptops, cables'),
        (28, '28% - ACs, large TVs (>32"), premium audio'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='product_categories/', blank=True, null=True)
    icon = models.CharField(max_length=50, help_text="FontAwesome icon class")
    color = models.CharField(max_length=7, default="#28a745", help_text="Hex color code")
    gst_rate = models.IntegerField(choices=GST_RATE_CHOICES, default=18, help_text="GST rate for this category")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Product Categories"

    def __str__(self):
        return self.name

class ElectricProduct(models.Model):
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('used', 'Used'),
        ('refurbished', 'Refurbished'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='products/')
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='products')
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='new')
    stock_quantity = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, 
                                validators=[MinValueValidator(0), MaxValueValidator(5)])
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def discount_percentage(self):
        if self.original_price and self.original_price > self.price:
            return int(((self.original_price - self.price) / self.original_price) * 100)
        return 0

class ProductReview(models.Model):
    product = models.ForeignKey(ElectricProduct, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['product', 'user']

    def __str__(self):
        return f"{self.user.username}'s review on {self.product.name}"

class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Cart"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def item_count(self):
        return sum(item.quantity for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(ShoppingCart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(ElectricProduct, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['cart', 'product']

    def __str__(self):
        return f"{self.quantity}x {self.product.name} in {self.cart.user.username}'s cart"

    @property
    def total_price(self):
        return self.product.price * self.quantity

class ServiceBooking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Credit/Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('online_payment', 'Online Payment'),
        ('check', 'Check'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low Priority'),
        ('normal', 'Normal Priority'),
        ('high', 'High Priority'),
        ('emergency', 'Emergency'),
    ]
    
    # Basic booking info
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    service = models.ForeignKey(ElectricService, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')
    
    # Location details
    address_line_1 = models.CharField(max_length=255, default='Jaipur')
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, default='Jaipur')
    state_province = models.CharField(max_length=100, default='Rajasthan')
    postal_code = models.CharField(max_length=20, default = '302001')
    country = models.CharField(max_length=100, default='India')
    
    # Contact information
    contact_phone = models.CharField(max_length=20, default = '9829000000')
    contact_email = models.EmailField(default = 'test@test.com')
    alternate_phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Scheduling
    preferred_date = models.DateField(default = timezone.now())
    preferred_time_slot = models.CharField(max_length=50, choices=[
        ('morning', 'Morning (8 AM - 12 PM)'),
        ('afternoon', 'Afternoon (12 PM - 4 PM)'),
        ('evening', 'Evening (4 PM - 8 PM)'),
        ('flexible', 'Flexible'),
    ], default = 'flexible')
    
    # Pricing and payment
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    final_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='card')
    payment_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('partial', 'Partial Payment'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    ], default='pending')
    
    # Service details
    service_description = models.TextField(help_text="Detailed description of the service needed", default = 'test')
    special_requirements = models.TextField(blank=True, null=True, help_text="Any special requirements or notes")
    property_type = models.CharField(max_length=50, choices=[
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('industrial', 'Industrial'),
        ('other', 'Other'),
    ], default='residential')
    
    # Timestamps
    booked_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    scheduled_date = models.DateTimeField(blank=True, null=True)
    completed_date = models.DateTimeField(blank=True, null=True)
    
    # Admin fields
    admin_notes = models.TextField(blank=True, null=True)
    assigned_technician = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True, 
        related_name='assigned_bookings'
    )
    
    def __str__(self):
        return f"{self.user.username} - {self.service.name} ({self.status}) - {self.preferred_date}"
    
    class Meta:
        ordering = ['-booked_at']
        verbose_name = "Service Booking"
        verbose_name_plural = "Service Bookings"
    
    @property
    def full_address(self):
        address_parts = [self.address_line_1]
        if self.address_line_2:
            address_parts.append(self.address_line_2)
        address_parts.extend([self.city, self.state_province, self.postal_code, self.country])
        return ', '.join(address_parts)
    
    @property
    def is_emergency(self):
        return self.priority == 'emergency'
    
    @property
    def is_overdue(self):
        if self.scheduled_date and self.status in ['confirmed', 'in_progress']:
            return self.scheduled_date < timezone.now()
        return False

    def get_status_color(self):
        """Return Bootstrap color class for status"""
        status_colors = {
            'pending': 'warning',
            'confirmed': 'info',
            'in_progress': 'primary',
            'completed': 'success',
            'cancelled': 'danger',
        }
        return status_colors.get(self.status, 'secondary')

    def get_status_display(self):
        """Return human-readable status"""
        status_display = {
            'pending': 'Pending',
            'confirmed': 'Confirmed',
            'in_progress': 'In Progress',
            'completed': 'Completed',
            'cancelled': 'Cancelled',
        }
        return status_display.get(self.status, self.status.title())

    def get_preferred_time_slot_display(self):
        """Return human-readable time slot"""
        time_slot_display = {
            'morning': 'Morning (8 AM - 12 PM)',
            'afternoon': 'Afternoon (12 PM - 4 PM)',
            'evening': 'Evening (4 PM - 8 PM)',
            'flexible': 'Flexible',
        }
        return time_slot_display.get(self.preferred_time_slot, self.preferred_time_slot.title())

    def get_payment_status_display(self):
        """Return human-readable payment status"""
        payment_status_display = {
            'pending': 'Pending',
            'partial': 'Partial Payment',
            'paid': 'Paid',
            'refunded': 'Refunded',
        }
        return payment_status_display.get(self.payment_status, self.payment_status.title())

class QuoteRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('quoted', 'Quoted'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    SERVICE_CHOICES = [
        ('electrical-repair', 'Electrical Repair'),
        ('installation', 'New Installation'),
        ('maintenance', 'Maintenance'),
        ('emergency', 'Emergency Service'),
        ('smart-home', 'Smart Home Setup'),
        ('inspection', 'Inspection & Testing'),
        ('other', 'Other'),
    ]
    
    # Contact Information
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Quote Details
    service_type = models.CharField(max_length=50, choices=SERVICE_CHOICES)
    message = models.TextField(blank=True, null=True)
    
    # Status and Timestamps
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Admin fields
    admin_notes = models.TextField(blank=True, null=True, help_text="Internal notes for admin use")
    estimated_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    def __str__(self):
        return f"Quote Request from {self.name} - {self.service_type} ({self.status})"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Quote Request"
        verbose_name_plural = "Quote Requests"
