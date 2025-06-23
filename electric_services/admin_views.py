from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta
from .models import ElectricProduct, ServiceCategory, UserProfile, ShoppingCart, ProductReview

@staff_member_required
def admin_dashboard(request):
    """Custom admin dashboard with analytics and insights"""
    
    # Get date ranges
    today = timezone.now().date()
    last_week = today - timedelta(days=7)
    last_month = today - timedelta(days=30)
    
    # Product statistics
    total_products = ElectricProduct.objects.count()
    active_products = ElectricProduct.objects.filter(is_active=True).count()
    featured_products = ElectricProduct.objects.filter(is_featured=True).count()
    out_of_stock = ElectricProduct.objects.filter(stock_quantity=0).count()
    low_stock = ElectricProduct.objects.filter(stock_quantity__lte=10, stock_quantity__gt=0).count()
    
    # Category statistics
    categories = ServiceCategory.objects.annotate(
        product_count=Count('electricproduct')
    ).order_by('-product_count')[:5]
    
    # Top rated products
    top_products = ElectricProduct.objects.filter(
        rating__gt=0
    ).order_by('-rating')[:5]
    
    # Recent reviews
    recent_reviews = ProductReview.objects.select_related(
        'product', 'user'
    ).order_by('-created_at')[:5]
    
    # User statistics
    total_users = UserProfile.objects.count()
    recent_users = UserProfile.objects.filter(
        created_at__date__gte=last_week
    ).count()
    
    # Cart statistics
    active_carts = ShoppingCart.objects.filter(
        updated_at__date__gte=last_week
    ).count()
    
    # Sales analytics (mock data for now)
    total_sales = 0  # This would be calculated from orders
    avg_order_value = 0  # This would be calculated from orders
    
    context = {
        'total_products': total_products,
        'active_products': active_products,
        'featured_products': featured_products,
        'out_of_stock': out_of_stock,
        'low_stock': low_stock,
        'categories': categories,
        'top_products': top_products,
        'recent_reviews': recent_reviews,
        'total_users': total_users,
        'recent_users': recent_users,
        'active_carts': active_carts,
        'total_sales': total_sales,
        'avg_order_value': avg_order_value,
    }
    
    return render(request, 'admin/dashboard.html', context)

@staff_member_required
def inventory_management(request):
    """Inventory management view"""
    
    # Stock alerts
    out_of_stock = ElectricProduct.objects.filter(stock_quantity=0)
    low_stock = ElectricProduct.objects.filter(
        stock_quantity__lte=10, 
        stock_quantity__gt=0
    )
    
    # Category-wise inventory
    category_inventory = ServiceCategory.objects.annotate(
        total_products=Count('electricproduct'),
        active_products=Count('electricproduct', filter=Q(electricproduct__is_active=True)),
        out_of_stock=Count('electricproduct', filter=Q(electricproduct__stock_quantity=0)),
        low_stock=Count('electricproduct', filter=Q(electricproduct__stock_quantity__lte=10, electricproduct__stock_quantity__gt=0))
    )
    
    context = {
        'out_of_stock': out_of_stock,
        'low_stock': low_stock,
        'category_inventory': category_inventory,
    }
    
    return render(request, 'admin/inventory.html', context)

@staff_member_required
def user_analytics(request):
    """User analytics and insights"""
    
    # User growth
    today = timezone.now().date()
    last_week = today - timedelta(days=7)
    last_month = today - timedelta(days=30)
    
    recent_users = UserProfile.objects.filter(
        created_at__date__gte=last_week
    ).count()
    
    monthly_users = UserProfile.objects.filter(
        created_at__date__gte=last_month
    ).count()
    
    # Top users by cart activity
    top_users = ShoppingCart.objects.annotate(
        total_items=Sum('items__quantity')
    ).order_by('-total_items')[:10]
    
    # User engagement (users with recent cart activity)
    engaged_users = ShoppingCart.objects.filter(
        updated_at__date__gte=last_week
    ).values('user').distinct().count()
    
    context = {
        'recent_users': recent_users,
        'monthly_users': monthly_users,
        'top_users': top_users,
        'engaged_users': engaged_users,
    }
    
    return render(request, 'admin/user_analytics.html', context) 