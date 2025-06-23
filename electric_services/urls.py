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
    
    # Shopping cart
    path('cart/', views.view_cart, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart-item/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    
    # Admin dashboard
    path('admin/dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('admin/inventory/', admin_views.inventory_management, name='admin_inventory'),
    path('admin/analytics/', admin_views.user_analytics, name='admin_analytics'),
] 