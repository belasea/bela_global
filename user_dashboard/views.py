from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import F, Sum, Q
from accounts.models import User
from orders.models import Order
from carts.models import Cart


def user_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')

    # --- EXISTING ORDER LOGIC ---
    query = request.GET.get('q', '').strip()
    base_queryset = Order.objects.filter(user=request.user)
    
    if query:
        base_queryset = base_queryset.filter(
            Q(order_id__icontains=query) | Q(slug__icontains=query)
        )

    stats = base_queryset.aggregate(
        total_spent=Sum('total_product_price')
    )
    total_orders = base_queryset.count()
    total_spent = stats['total_spent'] or 0.00
    total_cancelled = base_queryset.filter(cancelled=True).count()
    latest_five_orders = base_queryset.order_by('-timestamp')[:5]

    cart_obj, new_obj = Cart.objects.new_or_get(request)
    cart_items_count = cart_obj.get_count() if cart_obj else 0

    # --- PAGINATION ---
    page = request.GET.get('page', 1)
    paginator = Paginator(base_queryset.order_by('-timestamp'), 5)
    orders = paginator.get_page(page)

    context = {
        'orders': orders,
        'latest_five_orders': latest_five_orders,
        'total_orders': total_orders,
        'total_spent': total_spent,
        'cart_items_count': cart_items_count,
        'query': query,
        'total_cancelled': total_cancelled
    }
    return render(request, "user_dashboard/user_dashboard.html", context)
