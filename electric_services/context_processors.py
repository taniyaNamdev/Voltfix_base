from .models import ShoppingCart

def cart_context(request):
    """Add cart information to all templates"""
    context = {}
    
    if request.user.is_authenticated:
        try:
            cart = ShoppingCart.objects.get(user=request.user)
            context['cart'] = cart
        except ShoppingCart.DoesNotExist:
            context['cart'] = None
    else:
        context['cart'] = None
    
    return context 