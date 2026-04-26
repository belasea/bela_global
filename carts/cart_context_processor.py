from carts.models import Cart
from offers.models import Coupon
from offers.forms import CouponApplyForm


def cart_value_renderer(request):
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
    
    return context


