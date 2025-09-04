from django.urls import path
from . import views
from . import admin_views

urlpatterns = [
    # Main pages
    path('', views.welcome, name='welcome'),
    path('services/', views.services_overview, name='services_overview'),
    path('products/', views.products, name='products'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # User profile
    path('profile/', views.profile, name='profile'),
    path('bookings/', views.user_booking_history, name='booking_history'),
    
    # Shopping cart
    path('cart/', views.view_cart, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart-item/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    # Service booking
    path('book-service/', views.book_service, name='book_service'),
    
    # Quote requests
    path('submit-quote/', views.submit_quote_request, name='submit_quote_request'),
    
    # Admin dashboard
    path('admin/dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('admin/inventory/', admin_views.inventory_management, name='admin_inventory'),
    path('admin/analytics/', admin_views.user_analytics, name='admin_analytics'),

    # New URL patterns for About Us and Contact Us pages
    path('about/', views.about_us, name='about_us'),
    path('contact/', views.contact_us, name='contact_us'),

    # Payment URLs
    path('create-payment-order/', views.create_payment_order, name='create_payment_order'),
    path('create-service-payment-order/', views.create_service_payment_order, name='create_service_payment_order'),
    path('payment-callback/', views.payment_callback, name='payment_callback'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-failure/', views.payment_failure, name='payment_failure'),
] 