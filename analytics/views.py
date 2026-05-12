import csv
import datetime
from django.db.models import Q, Count, Sum
from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import (
    ObjectViewed,
    UserSession
)
from products.models import Product
from orders.models import Order
from carts.models import Cart


class Echo:
    """An object that implements just the write method of the file-like interface."""
    def write(self, value):
        return value
    

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
    total_views = ObjectViewed.objects.count()

    # --- PAGINATION ---
    page = request.GET.get('page', 1)
    paginator = Paginator(base_queryset.order_by('-timestamp'), 5)
    orders = paginator.get_page(page)
    
    # top_products_raw 
    top_products_raw = (
        ObjectViewed.objects
        .values('object_id')
        .annotate(total=Count('id'))
        .order_by('-total')[:5]
    )

    product_ids = [item['object_id'] for item in top_products_raw]

    products = Product.objects.filter(id__in=product_ids)
    product_map = {p.id: p for p in products}

    top_products = []

    for item in top_products_raw:
        product = product_map.get(item['object_id'])
        top_products.append({
            'object_id': item['object_id'],
            'total': item['total'],
            'product': product
        })

    context = {
        'orders': orders,
        'latest_five_orders': latest_five_orders,
        'total_orders': total_orders,
        'total_spent': total_spent,
        'cart_items_count': cart_items_count,
        'query': query,
        'total_cancelled': total_cancelled,
        'total_views': total_views,
        'top_products': top_products
        
    }
    return render(request, "analytics/user_dashboard/user_dashboard.html", context)


def my_orders(request):
    query = request.GET.get('q', '').strip()
    page = request.GET.get('page', 1)
    per_page = 10

    # 1. Authentication Check
    if not request.user.is_authenticated:
        return render(request, 'analytics/my_order/my_order.html', {'error': 'Login required'})
    
    user_country = getattr(request.user, 'country', None)
    queryset = Order.objects.all()

    if user_country:
        queryset = queryset.filter(country__iexact=user_country)
    else:
        queryset = queryset.none()
    
    if query:
        queryset = queryset.filter(Q(slug__icontains=query) | Q(order_id__icontains=query))

    queryset = queryset.values(
        'id', 'order_id', 'slug', 'timestamp', 'returned', 'cancelled', 'status', 'country'
    ).order_by('-timestamp')

    # 7. Pagination
    paginator = Paginator(queryset, per_page)
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)

    context = {
        'object_list': orders,
        'page': page,
        'query': query,
        'user_country': user_country
    }
    return render(request, 'analytics/my_order/my_order.html', context)



def pending_carts(request):
    """
    Return paginated carts without orders, filterable by user and product.
    """
    query = request.GET.get('q', '').strip()

    pending_carts = Cart.objects.annotate(
        items_count=Count('cart_items')
    ).filter(
        items_count__gt=0,
        order__isnull=True
    ).select_related('owner').prefetch_related('cart_items__product')

    # Apply search filter
    if query:
        pending_carts = pending_carts.filter(
            Q(owner__email__icontains=query) |
            Q(owner__first_name__icontains=query) |
            Q(owner__contact_number__icontains=query) |
            Q(cart_items__product__title__icontains=query)
        ).distinct()
    pending_carts = pending_carts.order_by('-update')
    
    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(pending_carts, 8)
    
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    context = {
        'object_list': posts,
        'page': page,
        'query': query,
    }
    return render(request, 'analytics/pending_carts/pending_carts.html', context)


def export_pending_carts(request):
    # Get date filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    carts = Cart.objects.annotate(
        c=Count('cart_items')
    ).filter(
        c__gt=0,
        order__isnull=True
    ).select_related('owner').prefetch_related('cart_items__product')

    # Apply date filter
    if start_date:
        carts = carts.filter(update__date__gte=start_date)
    if end_date:
        carts = carts.filter(update__date__lte=end_date)

    # Generator for streaming
    def generate_rows():
        yield ['Name', 'Email','Contact Number', 'Products', 'Total Potential Value', 'Last Active']

        for cart in carts.iterator(chunk_size=500):
            products = ", ".join(
                f"{i.quantity}x {i.product.title}"
                for i in cart.cart_items.all()
                if i.product
            )

            yield [
                cart.owner.first_name if cart.owner else "Guest",
                cart.owner.email if cart.owner else "Guest",
                cart.owner.contact_number,
                products,
                cart.get_total(),
                cart.update.strftime("%Y-%m-%d")
            ]

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)

    response = StreamingHttpResponse(
        (writer.writerow(row) for row in generate_rows()),
        content_type="text/csv",
    )
    response['Content-Disposition'] = 'attachment; filename="pending_carts.csv"'

    return response


def user_object_view(request):
    queryset = ObjectViewed.objects.all()
    query = request.GET.get('q')
    if query:
        query = query.strip()
        queryset = ObjectViewed.objects.filter(
            Q(ip_address__icontains=query) |
            Q(object_id=query) |
            Q(user__contact_number=query)
        ).distinct()

    page = request.GET.get('page')
    paginator = Paginator(queryset, 10)

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    context = {
        'object_list': posts,
        'page': page
    }
    return render(request, "analytics/view_object/user_object_view.html", context)


def generate_rows(queryset):
    # Header
    yield [
        'ID',
        'IP Address',
        'Email',
        'Contact Number',
        'Content Type',
        'Object ID',
        'Active User'
    ]

    # Data rows
    for obj in queryset.iterator(chunk_size=1000):
        yield [
            obj.id,
            obj.ip_address or "",
            obj.user.email if obj.user else "",
            obj.user.contact_number if obj.user else "",
            str(obj.content_type),
            obj.object_id,
            obj.user.is_active if obj.user else ""
        ]
        
def download_user_object(request):

    queryset = ObjectViewed.objects.select_related('user', 'content_type').all()
    current_month_text = datetime.datetime.now().strftime('%B')
    response = StreamingHttpResponse(
        streaming_content=(
            csv.writer(Echo()).writerow(row)
            for row in generate_rows(queryset)
        ),
        content_type="text/csv"
    )

    response['Content-Disposition'] = f'attachment; filename="{current_month_text}-user-object.csv"'

    return response


def user_session(request):
    queryset = UserSession.objects.all()
    page = request.GET.get('page')
    paginator = Paginator(queryset, 12)  # 10 posts per page

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    context = {
        'object_list': posts,
        'page': page
    }
    return render(request, "analytics/user_session/user_session.html", context)