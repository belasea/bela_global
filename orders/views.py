from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseRedirect
from django.db import transaction
from django.urls import reverse
from django.contrib import messages
from decimal import Decimal
from django.db.models import F, Sum, Q
from carts.models import Cart, CartItem
from addresses.models import Address
from addresses.forms import AddressForm
from orders.models import Order
from inventory.models import Inventory, InventoryStock, InventoryTransaction
from django.template.loader import get_template
from xhtml2pdf import pisa


def cart_checkout(request):
    cart_obj, new_obj = Cart.objects.new_or_get(request)

    # Redirect if cart is new or empty
    if new_obj or cart_obj.cart_items.count() == 0:
        return redirect("cart-list")

    # --- Load existing address if user is authenticated ---
    if request.user.is_authenticated:
        # Try to get existing shipping address
        user_address = Address.objects.filter(user=request.user, address_type='shipping').first()
        
        if request.method == 'POST':
            # Bind POST data to form for validation and saving
            form = AddressForm(request.POST, instance=user_address)
        else:
            # Pre-populate form for GET request
            initial_data = {
                'first_name': user_address.first_name if user_address else request.user.first_name,
                'last_name': user_address.last_name if user_address else request.user.last_name,
                'email': user_address.email if user_address else request.user.email,
                'contact_number': user_address.contact_number if user_address else request.user.contact_number,
                'address': user_address.address if user_address else '',
                'city': user_address.city if user_address else '',
                'location': user_address.location if user_address else '',
                'country': user_address.country if user_address else '',
            }
            form = AddressForm(instance=user_address, initial=initial_data)
    else:
        form = AddressForm(request.POST or None)

    errors = None

    if form.is_valid():
        instance = form.save(commit=False)
        instance.address_type = request.POST.get('address_type', 'shipping')
        notes = request.POST.get('notes') or None

        # Link address to user if logged in
        if request.user.is_authenticated:
            instance.user = request.user

        instance.save()

        # Process each cart item
        for cart_item in cart_obj.cart_items.all():
            product_list = []
            if cart_item.product:
                product_list.append(cart_item.product)
            
            seller_names = []
            quantity_costs = []
            selling_quantities = []

            for product in product_list:
                inventory_entry = InventoryStock.objects.get(pro_id=product.id)

                if inventory_entry.stock_quantity <= 0:
                    messages.warning(
                        request, f"{inventory_entry.pro_id.title} is sold out. Remove it from the cart."
                    )
                    return HttpResponseRedirect(reverse('cart-list'))

                # Deduct stock
                InventoryStock.objects.filter(pro_id=product.id).update(
                    stock_quantity=F('stock_quantity') - cart_item.quantity
                )

                remain_quantity = cart_item.quantity
                product_inventory_list = Inventory.objects.filter(
                    pro_id=product.id, stock_quantity__gt=0
                ).order_by('purchase_date')

                while remain_quantity > 0:
                    inventory = product_inventory_list.first()
                    if not inventory:
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

                    # Log transaction
                    InventoryTransaction.objects.create(
                        inventory=inventory,
                        product=product,
                        quantity=-quantity_decreased,
                        reason='sale',
                        ref_id=cart_obj.id
                    )
                    inventory.save()

            # Save seller and cost details in cart item
            cart_item.seller_name = (
                cart_item.seller_name + ", " + ", ".join(seller_names)
                if cart_item.seller_name else ", ".join(seller_names)
            )
            cart_item.purchase_quantity_cost = (
                cart_item.purchase_quantity_cost + ", " + ", ".join(quantity_costs)
                if cart_item.purchase_quantity_cost else ", ".join(quantity_costs)
            )
            cart_item.selling_quantity = (
                cart_item.selling_quantity + ", " + ", ".join(selling_quantities)
                if cart_item.selling_quantity else ", ".join(selling_quantities)
            )

            # Weighted average cost
            purchase_total = sum(inv.stock_quantity * inv.quantity_cost for inv in product_inventory_list)
            purchase_quantity = sum(inv.stock_quantity for inv in product_inventory_list)

            cart_item.weight_avg_cost = Decimal(purchase_total / purchase_quantity) if purchase_quantity > 0 else 0
            cart_item.last_purchase_price = Decimal(product_inventory_list[0].quantity_cost) if product_inventory_list.exists() else 0
            cart_item.save()

        # Remove cancelled inventory with zero stock
        Inventory.objects.filter(Q(is_cancelled=True) & Q(stock_quantity=0)).delete()

        # Create or get order
        order_obj, _ = Order.objects.new_or_get(request, instance, cart_obj)
        order_obj.total_product_price = cart_obj.get_total()
        # order_obj.delivery_charge = delivery_charge
        # order_obj.total_cost = cart_obj.get_total() + delivery_charge
        # order_obj.due = cart_obj.get_total() + delivery_charge
        
        # Without Delivery Charge
        order_obj.total_cost = cart_obj.get_total()
        order_obj.due = cart_obj.get_total()
        # order_obj.delivery_method = delivery_method
        if notes:
            order_obj.notes = notes
        order_obj.save()

        # Generate customer report
        # CustomerReport.objects.create(order=order_obj)

        # Clear cart session
        request.session['cart_items'] = 0
        if 'cart_id' in request.session:
            del request.session['cart_id']

        messages.success(request, "Your order is successfully completed")
        return redirect('checkout-done', slug=order_obj.slug)

    if form.errors:
        errors = form.errors

    # Delivery charges for template
    # inside_dhaka_charges = DeliveryCharge.objects.filter(delivery_location='inside_dhaka')
    # outside_dhaka_charges = DeliveryCharge.objects.filter(delivery_location='outside_dhaka')

    context = {
        "cart": cart_obj,
        "form": form,
        'address_type': 'shipping',
        'address': False,
        'errors': errors,
    }

    return render(request, "orders/checkout/checkout.html", context)


# Checkout Done ===========================================================
def checkout_done_view(request, slug):
    order = get_object_or_404(Order, slug=slug)
    context = {'order': order}
    return render(request, "orders/checkout/checkout-done.html", context)



# # Crete PDF View ==========================================================
# def pdf_report_create(request, slug):
#     obj = get_object_or_404(Order, slug=slug)
#     template_path = 'orders/order_pdf/order_pdf.html'
#     context = {'order': obj}
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = 'inline; filename="order.pdf"'  # Open in browser

#     template = get_template(template_path)
#     html = template.render(context)

#     # Create a PDF
#     pisa_status = pisa.CreatePDF(html, dest=response)
    
#     if pisa_status.err:
#         return HttpResponse(f'We had some errors with code {pisa_status.err}')
    
#     return response