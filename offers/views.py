from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils import timezone
from carts.models import Cart

from .forms import (
    CouponApplyForm, 
)
from .models import (
    Coupon, 
)


@require_POST
def coupon_apply(request):
    now = timezone.now()
    form = CouponApplyForm(request.POST)
    if form.is_valid():
        code = form.cleaned_data['code']
        try:
            coupon = Coupon.objects.get(
                code__iexact=code,
                valid_from__lte=now,
                valid_to__gte=now,
                active=True
            )

            # Assuming the cart is associated with the current user or guest user
            user = request.user if request.user.is_authenticated else None

            # Get the most recent cart associated with the user
            cart = Cart.objects.filter(owner=user).order_by('-timestamp').first()

            if cart:
                # Update the cart with the applied coupon
                cart.coupon = coupon
                cart.save()

                request.session['coupon_id'] = coupon.id
                messages.success(request, "Your coupon code was successfully applied to your cart.")
            else:
                messages.error(request, "No cart found for the user.")
        except Coupon.DoesNotExist:
            request.session['coupon_id'] = None
            messages.error(request, "Invalid or expired coupon code.")
    return redirect(request.META.get('HTTP_REFERER', '/'))


def coupon_remove(request):
    # Using your existing Manager method to find the active cart
    cart_obj, new_obj = Cart.objects.new_or_get(request)
    
    if cart_obj.coupon:
        cart_obj.coupon = None
        cart_obj.save()
        
        # Also clear the session variable if you're using it elsewhere
        if 'coupon_id' in request.session:
            del request.session['coupon_id']
            
        messages.success(request, "Coupon removed successfully.")
    else:
        messages.info(request, "No active coupon found in your cart.")
        
    return redirect(request.META.get('HTTP_REFERER', '/'))