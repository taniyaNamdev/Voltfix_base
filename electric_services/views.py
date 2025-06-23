from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Avg
from django.core.paginator import Paginator
from .models import UserProfile, ServiceCategory, ElectricProduct, ProductReview, ShoppingCart, CartItem
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserUpdateForm, ProfileUpdateForm, ProductSearchForm, ProductReviewForm

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
    """User profile page with proper form handling"""
    # Ensure a profile exists for the user
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
            
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)
        
    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'electric_services/profile.html', context)

def services_overview(request):
    """Services overview page"""
    categories = ServiceCategory.objects.all()
    featured_products = ElectricProduct.objects.filter(is_featured=True, is_active=True)[:8]
    
    context = {
        'categories': categories,
        'featured_products': featured_products,
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
    
    context = {
        'products': products_page,
        'form': form,
        'sort_by': sort_by,
    }
    return render(request, 'electric_services/products.html', context)

def product_detail(request, product_id):
    """Product detail page"""
    product = get_object_or_404(ElectricProduct, id=product_id, is_active=True)
    reviews = product.reviews.all().order_by('-created_at')
    
    if request.method == 'POST' and request.user.is_authenticated:
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
    
    context = {
        'cart': cart,
    }
    return render(request, 'electric_services/cart.html', context)

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
