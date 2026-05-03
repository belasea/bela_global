from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseRedirect
from django.db import transaction
from django.utils import timezone
from django.urls import reverse
from django.contrib import messages
from decimal import Decimal
from django.db.models import F, Sum, Q
from carts.models import Cart, CartItem
from accounts.models import User
from addresses.models import Address
from products.models import Product
from addresses.forms import BillingForm, shippingForm
from orders.models import Order, CancelledOrder, ReturnedOrder
from inventory.models import Inventory, InventoryStock, InventoryTransaction
from django.template.loader import get_template
from xhtml2pdf import pisa
import csv


def cart_checkout(request):
    if not request.user.is_authenticated:
        messages.info(request, "Please login to continue to checkout.")
        return redirect('login')

    cart_obj, new_obj = Cart.objects.new_or_get(request)
    if new_obj or cart_obj.cart_items.count() == 0:
        return redirect("cart-list")

    user_address = Address.objects.filter(user=request.user, address_type='shipping').first()

    if request.method == 'POST':
        billing_form = BillingForm(request.POST, instance=request.user)
        shipping_form = shippingForm(request.POST, instance=user_address)

        if billing_form.is_valid() and shipping_form.is_valid():
            # 1. Start a Transaction to ensure all or nothing happens
            with transaction.atomic():
                # Save forms
                billing_form.save()
                shipping_instance = shipping_form.save(commit=False)
                shipping_instance.user = request.user
                shipping_instance.address_type = 'shipping'
                shipping_instance.save()
                
                user_notes = request.POST.get('notes') 
                selected_country = shipping_instance.country
                
                # Process each cart item
                for cart_item in cart_obj.cart_items.all():
                    product = cart_item.product
                    
                    # 2. Get Country-Specific Stock Total (InventoryStock)
                    # We filter by both product and country
                    try:
                        inventory_entry = InventoryStock.objects.select_for_update().get(
                            pro_id=product, 
                            country=selected_country
                        )
                    except InventoryStock.DoesNotExist:
                        messages.warning(request, f"{product.title} is not available for {selected_country}.")
                        return redirect('cart-list')

                    if inventory_entry.stock_quantity < cart_item.quantity:
                        messages.warning(request, f"Insufficient stock for {product.title} in {selected_country}.")
                        return redirect('cart-list')

                    # Deduct from aggregated Country Stock
                    inventory_entry.stock_quantity = F('stock_quantity') - cart_item.quantity
                    inventory_entry.save()

                    # 3. Deduct from specific Inventory Batches for this country (FIFO)
                    remain_quantity = cart_item.quantity
                    product_inventory_list = Inventory.objects.filter(
                        pro_id=product, 
                        country=selected_country, # Country specific batches
                        stock_quantity__gt=0,
                        is_cancelled=False
                    ).order_by('purchase_date')

                    seller_names = []
                    quantity_costs = []
                    selling_quantities = []

                    for inventory in product_inventory_list:
                        if remain_quantity <= 0:
                            break
                        
                        if inventory.stock_quantity >= remain_quantity:
                            quantity_decreased = remain_quantity
                            inventory.stock_quantity -= remain_quantity
                            remain_quantity = 0
                        else:
                            quantity_decreased = inventory.stock_quantity
                            remain_quantity -= inventory.stock_quantity
                            inventory.stock_quantity = 0

                        seller_names.append(str(inventory.seller))
                        quantity_costs.append(str(inventory.quantity_cost))
                        selling_quantities.append(str(quantity_decreased))

                        # Log country-specific transaction
                        InventoryTransaction.objects.create(
                            inventory=inventory,
                            product=product,
                            quantity=-quantity_decreased,
                            reason='sale',
                            ref_id=cart_obj.id
                        )
                        inventory.save()

                    # Save batch details to the cart item
                    cart_item.seller_name = ", ".join(seller_names)
                    cart_item.purchase_quantity_cost = ", ".join(quantity_costs)
                    cart_item.selling_quantity = ", ".join(selling_quantities)
                    cart_item.save()

                # Clean up empty batches
                Inventory.objects.filter(Q(is_cancelled=True) & Q(stock_quantity=0)).delete()

                # 4. Finalize Order
                order_obj, _ = Order.objects.new_or_get(request, shipping_instance, cart_obj)
                order_obj.total_product_price = cart_obj.get_total()
                order_obj.total_cost = cart_obj.get_total()
                order_obj.due = cart_obj.get_total()
                order_obj.voucher = cart_obj.get_coupon_discount_percentage()
                order_obj.country = selected_country
                order_obj.notes = user_notes
                order_obj.save()

                # Clear session
                request.session['cart_items'] = 0
                if 'cart_id' in request.session:
                    del request.session['cart_id']

            messages.success(request, "Your order is successfully completed")
            return redirect('checkout-done', slug=order_obj.slug)
            
    else:
        billing_form = BillingForm(instance=request.user)
        initial_shipping = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'contact_number': request.user.contact_number,
            'country': request.user.country,
        }
        shipping_form = shippingForm(instance=user_address, initial=initial_shipping)

    context = {
        "cart": cart_obj,
        "billing_form": billing_form,
        "form": shipping_form,
        "errors": billing_form.errors or shipping_form.errors,
    }
    return render(request, "orders/checkout/checkout.html", context)


# Checkout Done ======================================================
def checkout_done_view(request, slug):
    order = get_object_or_404(Order, slug=slug)
    context = {'order': order}
    return render(request, "orders/checkout/checkout-done.html", context)


# Crete PDF View ======================================================
def pdf_report_create(request, slug):
    obj = get_object_or_404(Order, slug=slug)
    template_path = 'orders/order_pdf/order_pdf.html'
    context = {'order': obj}
    
    # 1. Initialize the response object with the correct PDF mime-type
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="order.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    # 2. pisa.CreatePDF writes the PDF data directly into the 'response' object
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse(f'We had some errors with code {pisa_status.err}')
    
    # 3. Return the completed response object to the browser
    return response


def order_pdf_list(request):
    query = request.GET.get('q', '').strip()
    page = request.GET.get('page', 1)
    per_page = 10

    # 1. Authentication Check
    if not request.user.is_authenticated:
        return render(request, 'orders/order_list/order_list.html', {'error': 'Login required'})

    # 2. Get User's Country
    # Ensure your User profile model actually has a 'country' attribute
    user_country = getattr(request.user, 'country', None)
    
    # 3. Base Queryset
    # We use .all() initially. Note: select_related is not needed if using .values()
    queryset = Order.objects.all()

    # 4. Filter by Country (Directly on the Order table)
    if user_country:
        # This matches the 'country' field in your Order model
        queryset = queryset.filter(country__iexact=user_country)
    else:
        # If user has no country, they see no orders (Privacy/Security measure)
        queryset = queryset.none()
    
    # 5. Apply Search Filter
    if query:
        queryset = queryset.filter(Q(slug__icontains=query) | Q(order_id__icontains=query))

    # 6. Select Specific Fields & Order
    # values() makes the query faster by not fetching every column
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

    return render(request, 'orders/order_list/order_list.html', context)


def download_order(request):
   
    queryset = Order.objects.all()
    response = HttpResponse(content_type="text/csv")
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Order ID', 'Slug', 'User', 'Addresses', 'Cart', 'Total product price', 'Due', 'Received',
        'Delivery Charge', 'Voucher',  'Cancelled', 'Returned', 'Notes',
    ])

    for order in queryset:
        row = []
        row.extend([
           order.id, order.order_id, order.slug, order.user, order.shipping_address.first_name, 
           order.total_product_price, order.due, order.received, order.delivery_charge, order.voucher,
           order.returned,

        ])
        writer.writerow(row[:])
    response['Content-Disposition'] = f'attachment; filename="order.csv"'
    return response


def order_csv_by_date(request):
    try:
        if request.method == "POST":
            start_date = request.POST.get('start-date')
            end_date = request.POST.get('end-date', None)
            queryset = Order.objects.order_download_by_date(start_date, end_date)
            response = HttpResponse(content_type='text/csv')
            writer = csv.writer(response)
            writer.writerow([
                'ID', 'Order ID', 'Slug', 'User', 'Addresses', 'Cart', 'Total product price', 'Due', 'Received',
                'Delivery Charge', 'Voucher',  'Cancelled', 'Returned', 'Notes',
            ])

            for order in queryset:
                row = []
                row.extend([
                    order.id, order.order_id, order.slug, order.user, order.shipping_address.first_name, 
                    order.total_product_price, order.due, order.received, order.delivery_charge, order.voucher,
                    order.returned,
                ])
                writer.writerow(row[:])
            response['Content-Disposition'] = f'attachment; filename="order.csv"'
            return response
    except:
        messages.add_message(request, messages.SUCCESS, "Oops you forgot select start date to end date.")
        return redirect('order-pdf-list')


# Crete PDF View ==========================================================
def pdf_report_create(request, slug):
    obj = get_object_or_404(Order, slug=slug)
    template_path = 'orders/order_pdf/order_pdf.html'
    context = {'order': obj}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="order.pdf"'  # Open in browser

    template = get_template(template_path)
    html = template.render(context)

    # Create a PDF
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse(f'We had some errors with code {pisa_status.err}')
    
    return response


# Update Detail view ================================================================
def order_details_view(request, slug):
   
    object_list = get_object_or_404(Order, slug=slug)
    context = {
        'object_list': object_list
    }
    return render(request, 'orders/order_details/order_details.html', context)


# Update Order View =================================================================
def update_order_view(request, slug):
    order_instance = get_object_or_404(Order, slug=slug)
    products = Product.objects.filter(active=True)

    address = order_instance.shipping_address
    form = AddressForm(request.POST or None, instance=address)

    delivery_charge = order_instance.delivery_charge if order_instance.delivery_charge else ''
    delivery_method = order_instance.delivery_method if order_instance.delivery_method else ''
    voucher = order_instance.voucher if order_instance.voucher else ''
    received = order_instance.received if order_instance.received else ''
    
    # Prepopulate product
    cart_items = order_instance.cart.cart_items.all()
    product_list = [item.product.id for item in cart_items if item.product]
    normal_quantities = [str(item.quantity) for item in cart_items if item.product]
   

    if form.is_valid():
        form.save()

    if request.method == 'POST':
        product_list = request.POST.getlist('products')
    
        # Get quantities for normal products, combo products, and BOGO products
        normal_quantities = request.POST.get('normal_quantities', '').split(',')

        # Handle normal products
        count = 0
        for product_id in product_list:
            product_obj = Product.objects.get(id=int(product_id))
            product_inventory_list = InventoryStock.objects.get(pro_id=product_obj)
            if product_inventory_list.stock_quantity - int(normal_quantities[count]) < 2:
                return HttpResponse(f'Stock is not available for {product_obj}')
            count += 1

        entry_set = order_instance.cart.cart_items.all()
        entry_product_list = [entry.product for entry in entry_set]

        count = 0
        for product_id in product_list:
            product_obj = Product.objects.get(id=int(product_id))
            if product_obj in entry_product_list:
                entry_filter = CartItem.objects.get(product=product_obj, cart=order_instance.cart)
                entry_filter.quantity = int(normal_quantities[count])
                entry_filter.save()
            else:
                product_inventory_list = Inventory.objects.filter(pro_id=product_obj)
                purchase_total = sum(inventory.purchase_quantity * inventory.quantity_cost for inventory in product_inventory_list)
                purchase_quantity = sum(inventory.purchase_quantity for inventory in product_inventory_list)

                try:
                    weight_avg_cost = Decimal(purchase_total / purchase_quantity)
                except ZeroDivisionError:
                    return HttpResponse(f"Check Inventory of {product_obj.title}. Purchase Quantity or Quantity Cost value Missing.")

                CartItem.objects.create(
                    cart=order_instance.cart,
                    product=product_obj,
                    quantity=int(normal_quantities[count]),
                    price=product_obj.price,
                    weight_avg_cost=weight_avg_cost,
                    last_purchase_price=Decimal(product_inventory_list.first().quantity_cost)
                )

            # Update inventory for normal products
            remain_quantity = int(normal_quantities[count])
            product_inventory_list = Inventory.objects.filter(
                pro_id=product_obj, stock_quantity__gt=0
            ).order_by('purchase_date')

            seller_names = []
            quantity_costs = []
            selling_quantity = []
            inventory_remain_quantity = []

            while True:
                inventory = product_inventory_list.first()
                if not inventory:
                    break  # Exit if no inventory is found

                if inventory.stock_quantity >= remain_quantity:
                    quantity_decreased = remain_quantity
                    inventory.stock_quantity -= remain_quantity
                    remain_quantity_for_inventory = inventory.stock_quantity
                    inventory_remain_quantity.append(str(remain_quantity_for_inventory))
                    seller_names.append(inventory.seller)
                    quantity_costs.append(str(inventory.quantity_cost))
                    selling_quantity.append(str(quantity_decreased))
                    inventory.save()
                    break
                else:
                    quantity_decreased = inventory.stock_quantity
                    remain_quantity -= inventory.stock_quantity
                    inventory.stock_quantity = 0
                    remain_quantity_for_inventory = inventory.stock_quantity
                    inventory_remain_quantity.append(str(remain_quantity_for_inventory))
                    seller_names.append(inventory.seller)
                    quantity_costs.append(str(inventory.quantity_cost))
                    selling_quantity.append(str(quantity_decreased))
                    inventory.save()

            # Update the CartItem with seller names, quantity costs, and selling quantities
            item = CartItem.objects.get(cart=order_instance.cart, product=product_obj)
            item.seller_name = ", ".join(seller_names)
            item.purchase_quantity_cost = ", ".join(quantity_costs)
            item.selling_quantity = ", ".join(selling_quantity)
            item.save()

            count += 1

        # Update order details
        delivery_charge = request.POST.get('delivery_charge', None) or False
        delivery_method = request.POST.get('delivery_method', None) or False
        voucher = request.POST.get('voucher', None) or False
        received = request.POST.get('received', None) or False

        if delivery_charge != '':
            order_instance.voucher = Decimal(voucher)
            order_instance.received = Decimal(received)
            order_instance.total_product_price = order_instance.cart.get_total()
            order_instance.total_cost = order_instance.cart.get_total() + Decimal(delivery_charge) - Decimal(voucher)
            order_instance.delivery_charge = Decimal(delivery_charge)
            order_instance.due = order_instance.total_cost
        order_instance.delivery_method = delivery_method
        
        notes = request.POST.get('notes', None)
        
        # Country 
        order_instance.country = address.country
        
        if notes != '':
            order_instance.notes = notes
        order_instance.save()
        messages.success(request, 'Order successfully updated!')
        return redirect('order-details', slug=order_instance.slug)

    context = {
        'order': order_instance,
        'products': products,
        'form': form,
        'product_list': product_list, 
        'normal_quantities': normal_quantities, 
        'delivery_charge': delivery_charge,
        'delivery_method': delivery_method,
        'voucher': voucher,
        'received': received,
    }

    return render(request, "orders/update_order/update_order.html", context)


# =========================================================
# Restock Cancelled Orders / Inventory (FIFO restore)
# =========================================================
def add_product_inventory(request):
    if request.method != "POST":
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    products = request.POST.get('products', '').strip().split(';')
    for product_name in products:
        product = Product.objects.filter(title__iexact=product_name).first()
        if not product:
            messages.warning(request, f"Product '{product_name}' not found.")
            continue

        with transaction.atomic():
            total_restored = 0

            # -------------------------------------
            #  Mark CancelledOrder as processed
            # --------------------------------------
            cancelled_orders = CancelledOrder.objects.filter(
                product=product,
                added=False
            )
            for cancel_order in cancelled_orders:
                cancel_order.added = True
                cancel_order.save()

            # --------------------------------------------------------
            # Restore from InventoryTransaction (sale cancellations)
            # --------------------------------------------------------
            cancelled_transactions = InventoryTransaction.objects.filter(
                product=product,
                reason='sale',
                is_restored=False
            ).order_by('inventory__purchase_date')  # FIFO

            for t in cancelled_transactions:
                inv = t.inventory
                qty_to_restore = abs(t.quantity)
                inv.stock_quantity += qty_to_restore
                inv.save()

                # Log restored transaction
                InventoryTransaction.objects.create(
                    inventory=inv,
                    product=product,
                    quantity=qty_to_restore,
                    reason='cancel',
                    ref_id=cancel_order.order.order_id,
                    is_restored=True
                )

                t.is_restored = True
                t.save()

                total_restored += qty_to_restore

            # --------------------------
            # Update InventoryStock table
            # --------------------------
            total_stock = Inventory.objects.filter(pro_id=product).aggregate(
                total=Sum('stock_quantity')
            )['total'] or 0

            InventoryStock.objects.update_or_create(
                pro_id=product,
                defaults={'stock_quantity': total_stock}
            )

            # Set Product active/inactive
            product.active = total_stock > 0
            product.save()

            if total_restored > 0:
                messages.success(request, f"{product} successfully restocked with {total_restored} items!")
            else:
                messages.info(request, f"No items needed restocking for {product}.")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# Remove product ==============================================================
def remove_product_order_list(request):
    if request.method == 'POST':
        invoice = request.POST.get('invoice')
        entry = request.POST.get('entry')

        # Use get_object_or_404 to handle DoesNotExist exceptions
        invoice_obj = get_object_or_404(Order, slug=invoice)
        entry_obj = get_object_or_404(CartItem, id=entry)

        current_product_inventory = Inventory.objects.filter(
            pro_id=entry_obj.product,
            stock_quantity__gt=0
        ).order_by('timestamp')

        next_ = True
        remain_quantity = entry_obj.quantity

        for product in current_product_inventory:
            if next_:
                sum_ = product.stock_quantity + remain_quantity
                if product.purchase_quantity >= sum_:
                    product.stock_quantity += remain_quantity
                    product.save()
                    next_ = False
                else:
                    tmp_remain_quantity = sum_ - product.purchase_quantity
                    product.stock_quantity += abs(remain_quantity - tmp_remain_quantity)
                    product.save()
                    remain_quantity = tmp_remain_quantity
                    next_ = True

        InventoryStock.objects.filter(pro_id=entry_obj.product).update(
            stock_quantity=F('stock_quantity') + entry_obj.quantity)

        entry_obj.delete()

        total = invoice_obj.cart.get_total()
        invoice_obj.total_product_price = invoice_obj.cart.get_total()
        invoice_obj.due = Decimal(total) + Decimal(invoice_obj.delivery_charge) - Decimal(invoice_obj.received)
        invoice_obj.total_cost = Decimal(total) + invoice_obj.delivery_charge
        invoice_obj.save()

        messages.success(request, 'Product removed successfully!')
        return redirect('order-details', invoice_obj.slug)
   

# Remove Order Item =======================================================================
def order_remove_item(request, order_id):  # Match the parameter name
    """
    View to remove an order, its associated CartItems, and the ShoppingCart.
    Only accessible by staff or superusers.
    """
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, "You do not have permission to delete orders.")
        return redirect("order-pdf-list")

    # Get the order using order_id
    order = get_object_or_404(Order, pk=order_id)

    cart = order.cart
    cart_items = CartItem.objects.filter(cart=cart)

    try:

        # Delete all CartItems associated with this cart
        cart_items.delete()
        # Check if the cart is empty and delete it
        if not CartItem.objects.filter(cart=cart).exists():
            print(f"Deleting Cart: {cart.id}")
            cart.delete()

        # Delete the order
        order.delete()
        messages.success(request, f"Order {order} and associated cart have been successfully deleted.")

    except Exception as e:
        messages.error(request, f"An error occurred while deleting the order: {e}")
        print(f"Error deleting order {order}: {e}")
    return redirect(reverse("order-pdf-list"))


# Cancelled Orders list ======================================================
def cancelled_orders_list(request):
    now = timezone.now()  
    
    queryset = CancelledOrder.objects.filter(added=False).select_related('order', 'product').order_by('-timestamp')
    query = request.GET.get('q')
    if query:
        query = query.strip()
        queryset = queryset.filter(
            Q(order__slug__icontains=query) |
            Q(order__slug__startswith=query) |
            Q(product__title__icontains=query) 
        ).distinct()

    page = request.GET.get('page')
    paginator = Paginator(queryset, 10)  # 10 items per page

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    # Today and total Invoice Cancel
    today_cancelled_orders = CancelledOrder.objects.filter(added=True, timestamp__date=now.date())
    total_cancelled_orders = CancelledOrder.objects.filter(added=True)

    context = {
        'object_list': posts,
        'page': page,
        'query':query,
        'today_cancelled_orders': today_cancelled_orders.count(),
        'total_cancelled_orders': total_cancelled_orders.count(),
    }

    return render(request, 'orders/cancel_order/cancel_order.html', context)


# Cancelled Order Details =====================================================
def cancelled_order_details(request):
    queryset = CancelledOrder.objects.order_by('-timestamp')
    # queryset = Order.objects.order_by('-timestamp')

    query = request.GET.get('q')
    if query:
        query = query.strip()
        queryset = queryset.filter(
            Q(slug__icontains=query)
        ).distinct()

    page = request.GET.get('page')
    paginator = Paginator(queryset, 10)  # 10 posts per page
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    context = {
        'object_list': posts,
        'page': page,
        'query': query
    }
    return render(request, 'orders/cancel_order/details_cancel_order.html', context)


# Cancelled Order Details CSV =====================================================
def cancelled_order_details_csv(request):
    try:
        if request.method == "POST":
            start_date = request.POST.get('start-date')
            end_date = request.POST.get('end-date')
            
            if not start_date:
                messages.add_message(request, messages.SUCCESS, "Oops you forgot to select the start date.")
                return redirect('cancelled-order-details')

            queryset = CancelledOrder.objects.filter(timestamp__range=(start_date, end_date))
            
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="cancelled-order-details.csv"'
            
            writer = csv.writer(response)
            writer.writerow(
                ['ID', 'Cancelled Invoice', 'Invoice NO', 'Date', "Due Amount", "Delivery Charge"]
            )

            for q in queryset:
                row = [
                    q.id, q.slug, q.order.slug, q.timestamp, q.order.due,
                    q.order.delivery_charge
                ]
                writer.writerow(row)

            return response
    except Exception as e:
        messages.add_message(request, messages.ERROR, f"An error occurred: {e}")
        return redirect('cancelled-order-details')
    

def cancelled_order_view(request, order_slug):
    order = get_object_or_404(Order, slug=order_slug)

    for item in order.cart.cart_items.all():
        product = item.product

        if product:
            product_obj = get_object_or_404(Product, id=product.id)
            CancelledOrder.objects.create(
                order=order, 
                product=product_obj, 
                quantity=item.quantity
            )
    # Mark the order as cancelled
    order.cancelled = True
    order.save()

    messages.success(request, f"Successfully cancelled the order {order}.")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# ReturnedOrder  ==========================================================================
def create_returned_order(request, slug):
    try:
        order = get_object_or_404(Order, slug=slug)
        loss = Decimal(0)
        if order.delivery_method == 1:
            loss = Decimal(105)

        returned_order = ReturnedOrder.objects.create(order=order, loss=loss)
        messages.success(request, f"Successfully Returned the Order: {order}")

        order.returned = True
        order.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    except Exception as e:
        # Print exception to console for debugging purposes
        print(f"Error creating returned order: {e}")
        messages.error(request, f"Error creating returned order: {e}")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def returned_order_list_view(request):
    queryset = ReturnedOrder.objects.order_by('-timestamp')
    query = request.GET.get('q')
    if query:
        # Using strip method to remove extra white space
        query = query.strip()
        queryset = ReturnedOrder.objects.filter(
            Q(order__slug__icontains=query) |
            Q(returned_id__icontains=query)
        ).distinct()
    # print(query)
    page = request.GET.get('page')
    paginator = Paginator(queryset, 10)  # 10 posts per page
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    context = {
        'object_list': posts,
        'page': page,
        'query': query
    }

    return render(request, 'orders/return-order/return-order.html', context)


def returned_order_details_csv(request):
    try:
        if request.method == "POST":
            start_date = request.POST.get('start-date')
            end_date = request.POST.get('end-date')
            
            if not start_date:
                messages.add_message(request, messages.SUCCESS, "Oops you forgot to select the start date.")
                return redirect('returned-order-list')
            queryset = ReturnedOrder.objects.filter(timestamp__range=(start_date, end_date))
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="returned-order.csv"'
            
            writer = csv.writer(response)
            writer.writerow(
                ["ID", "Return ID", "Order ID", "Loss",]
            )
            for r in queryset:
                row = [
                    r.id, r.returned_id, r.order, r.loss
                ]
                writer.writerow(row)
            return response
    except Exception as e:
        messages.add_message(request, messages.ERROR, f"An error occurred: {e}")
        return redirect('returned-order-list')