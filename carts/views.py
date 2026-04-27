from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib import messages
from products.models import Product
from inventory.models import InventoryStock
from offers.models import Coupon
from offers.forms import CouponApplyForm
from .models import Cart, CartItem
from django.db.models import Sum, F


def cart_list(request):
    cart_obj, new_obj = Cart.objects.new_or_get(request)
    cart_items = cart_obj.cart_items.all()
    coupon_apply_form = CouponApplyForm()
    active_coupon = Coupon.objects.filter(active=True)

    normal_products = []

    for cart_item in cart_items:
        if cart_item.product:
            normal_products.append(cart_item)

    is_cart_empty = len(cart_items) == 0

    context = {
        'cart_obj': cart_obj,
        'normal_products': normal_products,
        'cart_total': cart_obj.get_total(),
        'total_weight': cart_obj.total_weight(),
        'active_coupon': active_coupon,
        'coupon_apply_form': coupon_apply_form,
        'is_cart_empty': is_cart_empty,
    }

    return render(request, "carts/cart_list.html", context)


def add_to_cart(request):
    try:
        cart_obj, new_obj = Cart.objects.new_or_get(request)
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 0))
       
        if not (product_id) or quantity <= 0:
            messages.warning(request, "Invalid selection or quantity.")
            return redirect(request.META.get('HTTP_REFERER', '/'))
        
        # Handling Normal Products
        product_obj = get_object_or_404(Product, id=product_id)
        stock = get_object_or_404(InventoryStock, pro_id=product_obj)

        if stock.stock_quantity <= 0:
            messages.warning(request, "Item is out of stock!")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        cart_items = CartItem.objects.filter(cart=cart_obj, product=product_obj)

        total_quantity = cart_items.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
        limit = 1 if product_obj.limit_buy else 10

        if total_quantity + quantity > limit:
            messages.warning(request, f"You cannot add more than {limit} per product.")
        else:
            if cart_items.exists():
                cart_items.update(quantity=F('quantity') + quantity)
            else:
                CartItem.objects.create(
                    cart=cart_obj,
                    product=product_obj,
                    quantity=quantity,
                    price=product_obj.price,
                )
            messages.success(request, f"'{product_obj.title}' added to cart successfully.")

    except (Product.DoesNotExist, InventoryStock.DoesNotExist) as e:
        messages.error(request, f"An error occurred: {str(e)}")

    request.session['cart_items'] = cart_obj.get_count()
    return redirect(request.META.get('HTTP_REFERER', '/'))



def increase_quantity(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)

    # Check if the stock is sufficient for normal products
    if cart_item.product:
        stock = get_object_or_404(InventoryStock, pro_id=cart_item.product)
        if stock.stock_quantity <= 0:
            return JsonResponse({'error': 'Item is Stock Out!!!'})

    # Check if the quantity is already at the maximum (e.g., 10)
    if cart_item.quantity >= 10:
        return JsonResponse({'error': 'You can not add more than ten same products in cart.'})

    # Increment the quantity
    cart_item.quantity += 1
    cart_item.save()

    request.session['cart_items'] = cart_item.cart.get_count()
    return JsonResponse({'message': 'Quantity increased successfully'})


def decrease_quantity(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
        request.session['cart_items'] = cart_item.cart.get_count()
        return JsonResponse({'message': 'Quantity decreased successfully'})
    else:
        # Optionally, you can remove the item from the cart if the quantity becomes zero
        cart_item.delete()
        request.session['cart_items'] = cart_item.cart.get_count()
        return JsonResponse({'message': 'Item removed from cart'})


@require_POST
def remove_cart_item(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    cart = cart_item.cart
    cart_item.delete()
    request.session['cart_items'] = cart.get_count()
    return redirect(request.META.get('HTTP_REFERER', '/'))