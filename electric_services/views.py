from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Avg
from django.core.paginator import Paginator
from .models import UserProfile, ServiceCategory, ElectricProduct, ProductReview, ShoppingCart, CartItem, ProductCategory, ServiceBooking, ElectricService, QuoteRequest
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserUpdateForm, ProfileUpdateForm, ProductSearchForm, ProductReviewForm, QuoteRequestForm, ServiceBookingForm
from django.views.decorators.http import require_POST
from decimal import Decimal

def welcome(request):
    """Welcome page with modern electrifying design"""
    featured_products = ElectricProduct.objects.filter(is_featured=True, is_active=True)[:6]
    categories = ServiceCategory.objects.all()[:8]
    
    context = {
        'featured_products': featured_products,
        'categories': categories,
    }
    return render(request, 'electric_services/welcome.html', context)

def register(request):
    """User registration page"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome to VoltFix!')
            return redirect('welcome')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'electric_services/register.html', {'form': form})

def user_login(request):
    """User login page"""
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name}!')
                return redirect('welcome')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'electric_services/login.html', {'form': form})

@login_required
def user_logout(request):
    """Logout confirmation page"""
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'You have been successfully logged out.')
        return redirect('welcome')
    
    return render(request, 'electric_services/logout_confirm.html')

@login_required
def profile(request):
    """User profile page"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=user_profile, user=request.user)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=user_profile, user=request.user)
    
    # Get recent bookings for the user
    recent_bookings = ServiceBooking.objects.filter(user=request.user).order_by('-booked_at')[:4]
    
    # Get booking statistics
    total_bookings = ServiceBooking.objects.filter(user=request.user).count()
    completed_bookings = ServiceBooking.objects.filter(user=request.user, status='completed').count()
    pending_bookings = ServiceBooking.objects.filter(user=request.user, status='pending').count()
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'user_profile': user_profile,
        'recent_bookings': recent_bookings,
        'total_bookings': total_bookings,
        'completed_bookings': completed_bookings,
        'pending_bookings': pending_bookings,
    }
    return render(request, 'electric_services/profile.html', context)

def services_overview(request):
    """Services overview page with category filtering"""
    categories = ServiceCategory.objects.all()
    selected_category = request.GET.get('category')
    
    # Get actual services instead of categories
    services = ElectricService.objects.filter(is_active=True)
    if selected_category:
        services = services.filter(category_id=selected_category)
    
    featured_products = ElectricProduct.objects.filter(is_featured=True, is_active=True)[:8]
    context = {
        'categories': categories,
        'services': services,  # Changed from filtered_categories to services
        'featured_products': featured_products,
        'selected_category': selected_category,
    }
    return render(request, 'electric_services/services_overview.html', context)

def products(request):
    """Electric products page with filtering and sorting"""
    products_list = ElectricProduct.objects.filter(is_active=True)
    
    # Search and filtering
    form = ProductSearchForm(request.GET)
    if form.is_valid():
        search = form.cleaned_data.get('search')
        category = form.cleaned_data.get('category')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        condition = form.cleaned_data.get('condition')
        
        if search:
            products_list = products_list.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        
        if category:
            products_list = products_list.filter(category_id=category)
        
        if min_price:
            products_list = products_list.filter(price__gte=min_price)
        
        if max_price:
            products_list = products_list.filter(price__lte=max_price)
        
        if condition:
            products_list = products_list.filter(condition=condition)
    
    # Sorting
    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'price_low':
        products_list = products_list.order_by('price')
    elif sort_by == 'price_high':
        products_list = products_list.order_by('-price')
    elif sort_by == 'rating':
        products_list = products_list.order_by('-rating')
    elif sort_by == 'newest':
        products_list = products_list.order_by('-created_at')
    else:
        products_list = products_list.order_by('name')
    
    # Pagination
    paginator = Paginator(products_list, 12)
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)
    
    categories = ProductCategory.objects.all()
    
    context = {
        'products': products_page,
        'form': form,
        'sort_by': sort_by,
        'categories': categories,
    }
    return render(request, 'electric_services/products.html', context)

def product_detail(request, product_id):
    """Product detail page"""
    product = get_object_or_404(ElectricProduct, id=product_id, is_active=True)
    reviews = product.reviews.all().order_by('-created_at')
    can_review = False
    if request.user.is_authenticated:
        can_review = CartItem.objects.filter(cart__user=request.user, product=product).exists()
    if request.method == 'POST' and request.user.is_authenticated and can_review:
        review_form = ProductReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            # Update product rating
            avg_rating = product.reviews.aggregate(Avg('rating'))['rating__avg']
            product.rating = avg_rating or 0
            product.save()
            messages.success(request, 'Review submitted successfully!')
            return redirect('product_detail', product_id=product_id)
    else:
        review_form = ProductReviewForm()
    context = {
        'product': product,
        'reviews': reviews,
        'review_form': review_form,
        'can_review': can_review,
    }
    return render(request, 'electric_services/product_detail.html', context)

@login_required
def add_to_cart(request, product_id):
    """Add product to shopping cart"""
    if request.method == 'POST':
        product = get_object_or_404(ElectricProduct, id=product_id, is_active=True)
        quantity = int(request.POST.get('quantity', 1))
        
        cart, created = ShoppingCart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        
        cart_item.save()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'{product.name} added to cart!',
                'cart_count': cart.item_count
            })
        
        messages.success(request, f'{product.name} added to cart!')
        return redirect('products')
    
    return redirect('products')

@login_required
def view_cart(request):
    """View shopping cart"""
    cart, created = ShoppingCart.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        action = request.POST.get('action')
        
        if item_id and action:
            try:
                cart_item = CartItem.objects.get(id=item_id, cart=cart)
                if action == 'remove':
                    cart_item.delete()
                    messages.success(request, 'Item removed from cart.')
                elif action == 'update':
                    quantity = int(request.POST.get('quantity', 1))
                    if quantity > 0:
                        cart_item.quantity = quantity
                        cart_item.save()
                    else:
                        cart_item.delete()
                        messages.success(request, 'Item removed from cart.')
            except CartItem.DoesNotExist:
                pass
    
    # Calculate GST and final price
    subtotal = cart.total_price
    
    # Calculate GST for each item based on its category
    gst_details = {}
    total_gst = Decimal('0.00')
    
    for item in cart.items.all():
        category_name = item.product.category.name
        gst_rate = item.product.category.gst_rate
        item_gst = (item.total_price * Decimal(str(gst_rate))) / Decimal('100')
        
        if category_name not in gst_details:
            gst_details[category_name] = {
                'rate': gst_rate,
                'amount': Decimal('0.00'),
                'items': []
            }
        
        gst_details[category_name]['amount'] += item_gst
        gst_details[category_name]['items'].append({
            'product': item.product.name,
            'quantity': item.quantity,
            'price': item.product.price,
            'gst_amount': item_gst
        })
        total_gst += item_gst
    
    final_price = subtotal + total_gst
    
    context = {
        'cart': cart,
        'cart_items': cart.items.all(),
        'total_price': subtotal,
        'gst_details': gst_details,
        'total_gst': total_gst,
        'final_price': final_price,
    }
    return render(request, 'electric_services/cart.html', context)

@login_required
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    try:
        cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
        product_name = cart_item.product.name
        cart_item.delete()
        messages.success(request, f'{product_name} removed from cart.')
    except CartItem.DoesNotExist:
        messages.error(request, 'Item not found in cart.')
    
    return redirect('cart')

@login_required
def update_cart_item(request, item_id):
    """Update cart item quantity via AJAX"""
    if request.method == 'POST':
        try:
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
            quantity = int(request.POST.get('quantity', 1))
            
            if quantity > 0:
                cart_item.quantity = quantity
                cart_item.save()
            else:
                cart_item.delete()
            
            return JsonResponse({
                'success': True,
                'total_price': cart_item.cart.total_price,
                'item_count': cart_item.cart.item_count
            })
        except CartItem.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Item not found'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def about_us(request):
    """About Us page view"""
    context = {
        'page_title': 'About Us - VoltFix',
        'company_stats': {
            'projects_completed': 500,
            'response_time': 24,
            'years_experience': 15,
            'team_members': 50,
            'happy_customers': 1500,
            'satisfaction_rate': 98,
        }
    }
    return render(request, 'electric_services/about_us.html', context)

def contact_us(request):
    """Contact Us page view"""
    context = {
        'page_title': 'Contact Us - VoltFix',
        'contact_info': {
            'phone': '+1 (555) 123-4567',
            'email': 'info@voltfix.com',
            'address': '123 Electric Avenue, Power City, PC 12345',
            'hours': 'Monday - Friday: 8:00 AM - 6:00 PM\nSaturday: 9:00 AM - 4:00 PM\nSunday: Emergency Service Only',
        }
    }
    return render(request, 'electric_services/contact_us.html', context)

@require_POST
@login_required
def book_service(request):
    service_id = request.POST.get('service_id')
    service = get_object_or_404(ElectricService, id=service_id, is_active=True)
    
    form = ServiceBookingForm(request.POST, user=request.user)
    if form.is_valid():
        booking = form.save(commit=False)
        booking.user = request.user
        booking.service = service
        
        # Calculate estimated cost with 18% GST for services
        service_price = service.price
        gst_amount = (service_price * Decimal('18')) / Decimal('100')
        booking.estimated_cost = service_price + gst_amount
        
        booking.save()
        
        messages.success(request, f'Your booking for {service.name} has been submitted successfully! We will contact you within 24 hours to confirm your appointment.')
        return redirect('booking_history')
    else:
        # If form is invalid, we'll handle this in the template
        messages.error(request, 'Please correct the errors below and try again.')
        return redirect('services_overview')

@require_POST
def submit_quote_request(request):
    form = QuoteRequestForm(request.POST)
    if form.is_valid():
        quote_request = form.save()
        messages.success(request, 'Thank you! Your quote request has been submitted successfully. We will contact you within 24 hours.')
        return redirect('welcome')
    else:
        # If form is invalid, we'll handle this in the template
        messages.error(request, 'Please correct the errors below and try again.')
        return redirect('welcome')

@login_required
def user_booking_history(request):
    """User's booking history page"""
    bookings = ServiceBooking.objects.filter(user=request.user).order_by('-booked_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    
    context = {
        'bookings': bookings,
        'status_filter': status_filter,
        'total_bookings': bookings.count(),
        'pending_bookings': bookings.filter(status='pending').count(),
        'confirmed_bookings': bookings.filter(status='confirmed').count(),
        'completed_bookings': bookings.filter(status='completed').count(),
    }
    return render(request, 'electric_services/booking_history.html', context)
