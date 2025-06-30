from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Sum, Avg
from django.contrib.admin import SimpleListFilter
from .models import UserProfile, ServiceCategory, ElectricService, ProductCategory, ElectricProduct, ProductReview, ShoppingCart, CartItem, ServiceBooking, QuoteRequest
from django.utils import timezone

# Custom Admin Site Configuration
admin.site.site_header = "VoltFix Admin Panel"
admin.site.site_title = "VoltFix Administration"
admin.site.index_title = "Welcome to VoltFix Admin Panel"

class StockFilter(SimpleListFilter):
    title = 'Stock Status'
    parameter_name = 'stock_status'

    def lookups(self, request, model_admin):
        return (
            ('in_stock', 'In Stock'),
            ('low_stock', 'Low Stock (< 10)'),
            ('out_of_stock', 'Out of Stock'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'in_stock':
            return queryset.filter(stock_quantity__gt=10)
        if self.value() == 'low_stock':
            return queryset.filter(stock_quantity__lte=10, stock_quantity__gt=0)
        if self.value() == 'out_of_stock':
            return queryset.filter(stock_quantity=0)

class RatingFilter(SimpleListFilter):
    title = 'Rating'
    parameter_name = 'rating'

    def lookups(self, request, model_admin):
        return (
            ('5', '5 Stars'),
            ('4', '4+ Stars'),
            ('3', '3+ Stars'),
            ('2', '2+ Stars'),
            ('1', '1+ Stars'),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(rating__gte=float(self.value()))

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'created_at', 'profile_picture_display']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name', 'phone_number']
    list_filter = ['created_at', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']
    
    def profile_picture_display(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover;" />', obj.profile_picture.url)
        return format_html('<div style="width: 50px; height: 50px; background: #f0f0f0; border-radius: 50%; display: flex; align-items: center; justify-content: center;"><i class="fas fa-user"></i></div>')
    profile_picture_display.short_description = 'Profile Picture'

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'image_display', 'icon_display', 'color_display', 'service_count', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['created_at']
    prepopulated_fields = {'name': ('name',)}
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description')
        }),
        ('Visual Elements', {
            'fields': ('image', 'icon', 'color')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at']
    
    def image_display(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;" />', obj.image.url)
        return format_html('<div style="width: 50px; height: 50px; background: #f0f0f0; border-radius: 5px; display: flex; align-items: center; justify-content: center;"><i class="fas fa-image"></i></div>')
    image_display.short_description = 'Image'
    
    def icon_display(self, obj):
        return format_html('<i class="{}" style="font-size: 1.5rem; color: {};"></i>', obj.icon, obj.color)
    icon_display.short_description = 'Icon'
    
    def color_display(self, obj):
        return format_html('<div style="width: 30px; height: 30px; background: {}; border-radius: 5px;"></div>', obj.color)
    color_display.short_description = 'Color'
    
    def service_count(self, obj):
        count = obj.services.count()
        return format_html('<span class="badge bg-primary">{}</span>', count)
    service_count.short_description = 'Services'

@admin.register(ElectricService)
class ElectricServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price_display', 'duration', 'is_active', 'image_display']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'category__name']
    list_editable = ['is_active']
    readonly_fields = ['created_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'category')
        }),
        ('Service Details', {
            'fields': ('price', 'duration')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Settings', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def price_display(self, obj):
        return format_html('<span style="color: #28a745; font-weight: bold;">${}</span>', obj.price)
    price_display.short_description = 'Price'
    
    def image_display(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;" />', obj.image.url)
        return format_html('<div style="width: 50px; height: 50px; background: #f0f0f0; border-radius: 5px; display: flex; align-items: center; justify-content: center;"><i class="fas fa-image"></i></div>')
    image_display.short_description = 'Image'

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'gst_rate_display', 'image_display', 'icon_display', 'color_display', 'product_count', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['gst_rate', 'created_at']
    prepopulated_fields = {'name': ('name',)}
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description')
        }),
        ('Visual Elements', {
            'fields': ('image', 'icon', 'color')
        }),
        ('Tax Configuration', {
            'fields': ('gst_rate',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at']
    
    def gst_rate_display(self, obj):
        return format_html('<span class="badge bg-info">{}</span>', f"{obj.gst_rate}%")
    gst_rate_display.short_description = 'GST Rate'
    
    def image_display(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;" />', obj.image.url)
        return format_html('<div style="width: 50px; height: 50px; background: #f0f0f0; border-radius: 5px; display: flex; align-items: center; justify-content: center;"><i class="fas fa-image"></i></div>')
    image_display.short_description = 'Image'
    
    def icon_display(self, obj):
        return format_html('<i class="{}" style="font-size: 1.5rem; color: {};"></i>', obj.icon, obj.color)
    icon_display.short_description = 'Icon'
    
    def color_display(self, obj):
        return format_html('<div style="width: 30px; height: 30px; background: {}; border-radius: 5px;"></div>', obj.color)
    color_display.short_description = 'Color'
    
    def product_count(self, obj):
        count = obj.products.count()
        return format_html('<span class="badge bg-success">{}</span>', count)
    product_count.short_description = 'Products'

@admin.register(ElectricProduct)
class ElectricProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price_display', 'stock_status', 'rating_display', 'is_featured', 'is_active', 'image_display']
    list_filter = [StockFilter, RatingFilter, 'category', 'condition', 'is_featured', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'category__name']
    list_editable = ['is_featured', 'is_active']
    prepopulated_fields = {'name': ('name',)}
    readonly_fields = ['rating', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'category', 'condition')
        }),
        ('Pricing', {
            'fields': ('price', 'original_price')
        }),
        ('Inventory', {
            'fields': ('stock_quantity', 'is_active')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Settings', {
            'fields': ('is_featured', 'rating')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def price_display(self, obj):
        if obj.original_price and obj.original_price > obj.price:
            return format_html('<span style="color: #dc3545; text-decoration: line-through;">${}</span><br><span style="color: #28a745; font-weight: bold;">${}</span>', 
                             obj.original_price, obj.price)
        return format_html('<span style="color: #28a745; font-weight: bold;">${}</span>', obj.price)
    price_display.short_description = 'Price'
    
    def stock_status(self, obj):
        if obj.stock_quantity == 0:
            return format_html('<span class="badge bg-danger">Out of Stock</span>')
        elif obj.stock_quantity <= 10:
            return format_html('<span class="badge bg-warning">Low Stock ({})</span>', obj.stock_quantity)
        else:
            return format_html('<span class="badge bg-success">In Stock ({})</span>', obj.stock_quantity)
    stock_status.short_description = 'Stock'
    
    def rating_display(self, obj):
        stars = ''
        for i in range(5):
            if i < int(obj.rating):
                stars += '★'
            else:
                stars += '☆'
        return format_html('<span style="color: #ffc107;">{}</span> ({})', stars, obj.rating)
    rating_display.short_description = 'Rating'
    
    def image_display(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;" />', obj.image.url)
        return format_html('<div style="width: 50px; height: 50px; background: #f0f0f0; border-radius: 5px; display: flex; align-items: center; justify-content: center;"><i class="fas fa-image"></i></div>')
    image_display.short_description = 'Image'

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating_display', 'comment_preview', 'created_at']
    list_filter = ['rating', 'created_at', 'product__category']
    search_fields = ['product__name', 'user__username', 'user__email', 'comment']
    readonly_fields = ['created_at']
    
    def rating_display(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span style="color: #ffc107;">{}</span>', stars)
    rating_display.short_description = 'Rating'
    
    def comment_preview(self, obj):
        return obj.comment[:100] + '...' if len(obj.comment) > 100 else obj.comment
    comment_preview.short_description = 'Comment'

@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ['user', 'item_count', 'total_price_display', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at']
    
    def total_price_display(self, obj):
        return format_html('<span style="color: #28a745; font-weight: bold;">${}</span>', obj.total_price)
    total_price_display.short_description = 'Total Price'
    
    def item_count(self, obj):
        return format_html('<span class="badge bg-primary">{}</span>', obj.item_count)
    item_count.short_description = 'Items'

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'quantity', 'total_price_display', 'added_at']
    list_filter = ['added_at', 'product__category']
    search_fields = ['cart__user__username', 'product__name']
    readonly_fields = ['added_at']
    
    def total_price_display(self, obj):
        return format_html('<span style="color: #28a745; font-weight: bold;">₹{}</span>', obj.total_price)
    total_price_display.short_description = 'Total Price'

@admin.register(QuoteRequest)
class QuoteRequestAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'service_type', 'status', 'created_at']
    list_filter = ['status', 'service_type', 'created_at']
    search_fields = ['name', 'email', 'message']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 20
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Quote Details', {
            'fields': ('service_type', 'message')
        }),
        ('Status & Management', {
            'fields': ('status', 'estimated_price', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_reviewed', 'mark_as_quoted', 'mark_as_accepted', 'mark_as_rejected']
    
    def mark_as_reviewed(self, request, queryset):
        queryset.update(status='reviewed')
    mark_as_reviewed.short_description = "Mark selected quotes as reviewed"
    
    def mark_as_quoted(self, request, queryset):
        queryset.update(status='quoted')
    mark_as_quoted.short_description = "Mark selected quotes as quoted"
    
    def mark_as_accepted(self, request, queryset):
        queryset.update(status='accepted')
    mark_as_accepted.short_description = "Mark selected quotes as accepted"
    
    def mark_as_rejected(self, request, queryset):
        queryset.update(status='rejected')
    mark_as_rejected.short_description = "Mark selected quotes as rejected"

# Custom Admin Actions
@admin.action(description="Mark selected products as featured")
def make_featured(modeladmin, request, queryset):
    queryset.update(is_featured=True)
make_featured.short_description = "Mark selected products as featured"

@admin.action(description="Mark selected products as not featured")
def make_not_featured(modeladmin, request, queryset):
    queryset.update(is_featured=False)
make_not_featured.short_description = "Mark selected products as not featured"

@admin.action(description="Activate selected products")
def activate_products(modeladmin, request, queryset):
    queryset.update(is_active=True)
activate_products.short_description = "Activate selected products"

@admin.action(description="Deactivate selected products")
def deactivate_products(modeladmin, request, queryset):
    queryset.update(is_active=False)
deactivate_products.short_description = "Deactivate selected products"

# Add actions to ElectricProductAdmin
ElectricProductAdmin.actions = [make_featured, make_not_featured, activate_products, deactivate_products]

@admin.register(ServiceBooking)
class ServiceBookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'service', 'status', 'priority', 'preferred_date', 'contact_phone', 'city', 'estimated_cost']
    list_filter = ['status', 'priority', 'property_type', 'payment_method', 'payment_status', 'preferred_date', 'booked_at']
    search_fields = ['user__username', 'user__email', 'contact_phone', 'contact_email', 'address_line_1', 'city', 'service_description']
    readonly_fields = ['booked_at', 'updated_at']
    list_per_page = 20
    date_hierarchy = 'booked_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'service', 'status', 'priority')
        }),
        ('Location Details', {
            'fields': ('address_line_1', 'address_line_2', 'city', 'state_province', 'postal_code', 'country')
        }),
        ('Contact Information', {
            'fields': ('contact_phone', 'contact_email', 'alternate_phone')
        }),
        ('Scheduling', {
            'fields': ('preferred_date', 'preferred_time_slot', 'scheduled_date', 'completed_date')
        }),
        ('Service Details', {
            'fields': ('property_type', 'service_description', 'special_requirements')
        }),
        ('Pricing & Payment', {
            'fields': ('estimated_cost', 'final_cost', 'payment_method', 'payment_status')
        }),
        ('Administration', {
            'fields': ('assigned_technician', 'admin_notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('booked_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'mark_as_pending', 'mark_as_confirmed', 'mark_as_in_progress', 
        'mark_as_completed', 'mark_as_cancelled', 'mark_as_paid'
    ]
    
    def mark_as_pending(self, request, queryset):
        queryset.update(status='pending')
    mark_as_pending.short_description = "Mark selected bookings as pending"
    
    def mark_as_confirmed(self, request, queryset):
        queryset.update(status='confirmed')
    mark_as_confirmed.short_description = "Mark selected bookings as confirmed"
    
    def mark_as_in_progress(self, request, queryset):
        queryset.update(status='in_progress')
    mark_as_in_progress.short_description = "Mark selected bookings as in progress"
    
    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed', completed_date=timezone.now())
    mark_as_completed.short_description = "Mark selected bookings as completed"
    
    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
    mark_as_cancelled.short_description = "Mark selected bookings as cancelled"
    
    def mark_as_paid(self, request, queryset):
        queryset.update(payment_status='paid')
    mark_as_paid.short_description = "Mark selected bookings as paid"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'service', 'assigned_technician')
    
    def full_address(self, obj):
        return obj.full_address
    full_address.short_description = 'Full Address'
    
    def is_emergency(self, obj):
        return obj.is_emergency
    is_emergency.boolean = True
    is_emergency.short_description = 'Emergency'
    
    def is_overdue(self, obj):
        return obj.is_overdue
    is_overdue.boolean = True
    is_overdue.short_description = 'Overdue'
