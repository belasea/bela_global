# # Checkout ===========================================================
# def cart_checkout(request):
#     cart_obj, new_obj = Cart.objects.new_or_get(request)

#     # Redirect if cart is new or empty
#     if new_obj or cart_obj.cart_items.count() == 0:
#         return redirect("cart-list")

#     # --- Load existing address if user is authenticated ---
#     if request.user.is_authenticated:
#         # Try to get existing shipping address
#         user_address = Address.objects.filter(user=request.user, address_type='shipping').first()
        
#         if request.method == 'POST':
#             # Bind POST data to form for validation and saving
#             form = AddressForm(request.POST, instance=user_address)
#         else:
#             # Pre-populate form for GET request
#             initial_data = {
#                 'first_name': user_address.first_name if user_address else request.user.first_name,
#                 'last_name': user_address.last_name if user_address else request.user.last_name,
#                 'email': user_address.email if user_address else request.user.email,
#                 'contact_number': user_address.contact_number if user_address else request.user.contact_number,
#                 'address': user_address.address if user_address else '',
#                 'city': user_address.city if user_address else '',
#                 'location': user_address.location if user_address else '',
#                 'country': user_address.country if user_address else '',
#             }
#             form = AddressForm(instance=user_address, initial=initial_data)
#     else:
#         form = AddressForm(request.POST or None)

#     errors = None

#     if form.is_valid():
#         instance = form.save(commit=False)
#         instance.address_type = request.POST.get('address_type', 'shipping')
#         notes = request.POST.get('notes') or None

#         # Link address to user if logged in
#         if request.user.is_authenticated:
#             instance.user = request.user

#         instance.save()

#         # Process each cart item
#         for cart_item in cart_obj.cart_items.all():
#             product_list = []
#             if cart_item.product:
#                 product_list.append(cart_item.product)
            
#             seller_names = []
#             quantity_costs = []
#             selling_quantities = []

#             for product in product_list:
#                 inventory_entry = InventoryStock.objects.get(pro_id=product.id)

#                 if inventory_entry.stock_quantity <= 0:
#                     messages.warning(
#                         request, f"{inventory_entry.pro_id.title} is sold out. Remove it from the cart."
#                     )
#                     return HttpResponseRedirect(reverse('cart-list'))

#                 # Deduct stock
#                 InventoryStock.objects.filter(pro_id=product.id).update(
#                     stock_quantity=F('stock_quantity') - cart_item.quantity
#                 )

#                 remain_quantity = cart_item.quantity
#                 product_inventory_list = Inventory.objects.filter(
#                     pro_id=product.id, stock_quantity__gt=0
#                 ).order_by('purchase_date')

#                 while remain_quantity > 0:
#                     inventory = product_inventory_list.first()
#                     if not inventory:
#                         break
#                     if inventory.stock_quantity >= remain_quantity:
#                         quantity_decreased = remain_quantity
#                         inventory.stock_quantity -= remain_quantity
#                         remain_quantity = 0
#                     else:
#                         quantity_decreased = inventory.stock_quantity
#                         remain_quantity -= inventory.stock_quantity
#                         inventory.stock_quantity = 0

#                     seller_names.append(str(inventory.seller))
#                     quantity_costs.append(str(inventory.quantity_cost))
#                     selling_quantities.append(str(quantity_decreased))

#                     # Log transaction
#                     InventoryTransaction.objects.create(
#                         inventory=inventory,
#                         product=product,
#                         quantity=-quantity_decreased,
#                         reason='sale',
#                         ref_id=cart_obj.id
#                     )
#                     inventory.save()

#             # Save seller and cost details in cart item
#             cart_item.seller_name = (
#                 cart_item.seller_name + ", " + ", ".join(seller_names)
#                 if cart_item.seller_name else ", ".join(seller_names)
#             )
#             cart_item.purchase_quantity_cost = (
#                 cart_item.purchase_quantity_cost + ", " + ", ".join(quantity_costs)
#                 if cart_item.purchase_quantity_cost else ", ".join(quantity_costs)
#             )
#             cart_item.selling_quantity = (
#                 cart_item.selling_quantity + ", " + ", ".join(selling_quantities)
#                 if cart_item.selling_quantity else ", ".join(selling_quantities)
#             )

#             # Weighted average cost
#             purchase_total = sum(inv.stock_quantity * inv.quantity_cost for inv in product_inventory_list)
#             purchase_quantity = sum(inv.stock_quantity for inv in product_inventory_list)

#             cart_item.weight_avg_cost = Decimal(purchase_total / purchase_quantity) if purchase_quantity > 0 else 0
#             cart_item.last_purchase_price = Decimal(product_inventory_list[0].quantity_cost) if product_inventory_list.exists() else 0
#             cart_item.save()

#         # Remove cancelled inventory with zero stock
#         Inventory.objects.filter(Q(is_cancelled=True) & Q(stock_quantity=0)).delete()

#         # Create or get order
#         order_obj, _ = Order.objects.new_or_get(request, instance, cart_obj)
#         order_obj.total_product_price = cart_obj.get_total()
#         # order_obj.delivery_charge = delivery_charge
#         # order_obj.total_cost = cart_obj.get_total() + delivery_charge
#         # order_obj.due = cart_obj.get_total() + delivery_charge
        
#         # Without Delivery Charge
#         order_obj.total_cost = cart_obj.get_total()
#         order_obj.due = cart_obj.get_total()
#         # order_obj.delivery_method = delivery_method
        
#         # get_coupon_discount_percentage
#         order_obj.voucher = cart_obj.get_coupon_discount_percentage()

#         # Country 
#         order_obj.country = user_address.country
        
#         if notes:
#             order_obj.notes = notes
#         order_obj.save()

#         # Generate customer report
#         # CustomerReport.objects.create(order=order_obj)

#         # Clear cart session
#         request.session['cart_items'] = 0
#         if 'cart_id' in request.session:
#             del request.session['cart_id']

#         messages.success(request, "Your order is successfully completed")
#         return redirect('checkout-done', slug=order_obj.slug)

#     if form.errors:
#         errors = form.errors

#     # Delivery charges for template
#     # inside_dhaka_charges = DeliveryCharge.objects.filter(delivery_location='inside_dhaka')
#     # outside_dhaka_charges = DeliveryCharge.objects.filter(delivery_location='outside_dhaka')

#     context = {
#         "cart": cart_obj,
#         "form": form,
#         'address_type': 'shipping',
#         'address': False,
#         'errors': errors,
#     }

#     return render(request, "orders/checkout/checkout.html", context)



# Checkout ===========================================================
def cart_checkout(request):
    if request.user.is_authenticated:
        country = request.user.country
        # print("country", country)
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
            
            # get_coupon_discount_percentage
            order_obj.voucher = cart_obj.get_coupon_discount_percentage()

            # Country 
            order_obj.country = country
            
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

    else:
        # This part handles unauthenticated users
        messages.info(request, "Please login to continue to checkout.")
        login_url = reverse('login')
        return redirect(f"{login_url}")
        
"""

# def cart_checkout(request):
#     if not request.user.is_authenticated:
#         messages.info(request, "Please login to continue to checkout.")
#         return redirect('login')

#     cart_obj, new_obj = Cart.objects.new_or_get(request)
#     if new_obj or cart_obj.cart_items.count() == 0:
#         return redirect("cart-list")

#     user_address = Address.objects.filter(user=request.user, address_type='shipping').first()

#     if request.method == 'POST':
#         billing_form = BillingForm(request.POST, instance=request.user)
#         shipping_form = shippingForm(request.POST, instance=user_address)

#         if billing_form.is_valid() and shipping_form.is_valid():
#             # 1. Start a Transaction to ensure all or nothing happens
#             with transaction.atomic():
#                 # Save forms
#                 billing_form.save()
#                 shipping_instance = shipping_form.save(commit=False)
#                 shipping_instance.user = request.user
#                 shipping_instance.address_type = 'shipping'
#                 shipping_instance.save()
                
#                 user_notes = request.POST.get('notes') 
#                 selected_country = shipping_instance.country
                
#                 # Process each cart item
#                 for cart_item in cart_obj.cart_items.all():
#                     product = cart_item.product
                    
#                     # 2. Get Country-Specific Stock Total (InventoryStock)
#                     # We filter by both product and country
#                     try:
#                         inventory_entry = InventoryStock.objects.select_for_update().get(
#                             pro_id=product, 
#                             country=selected_country
#                         )
#                     except InventoryStock.DoesNotExist:
#                         messages.warning(request, f"{product.title} is not available for {selected_country}.")
#                         return redirect('cart-list')

#                     if inventory_entry.stock_quantity < cart_item.quantity:
#                         messages.warning(request, f"Insufficient stock for {product.title} in {selected_country}.")
#                         return redirect('cart-list')

#                     # Deduct from aggregated Country Stock
#                     inventory_entry.stock_quantity = F('stock_quantity') - cart_item.quantity
#                     inventory_entry.save()

#                     # 3. Deduct from specific Inventory Batches for this country (FIFO)
#                     remain_quantity = cart_item.quantity
#                     product_inventory_list = Inventory.objects.filter(
#                         pro_id=product, 
#                         country=selected_country, # Country specific batches
#                         stock_quantity__gt=0,
#                         is_cancelled=False
#                     ).order_by('purchase_date')

#                     seller_names = []
#                     quantity_costs = []
#                     selling_quantities = []

#                     for inventory in product_inventory_list:
#                         if remain_quantity <= 0:
#                             break
                        
#                         if inventory.stock_quantity >= remain_quantity:
#                             quantity_decreased = remain_quantity
#                             inventory.stock_quantity -= remain_quantity
#                             remain_quantity = 0
#                         else:
#                             quantity_decreased = inventory.stock_quantity
#                             remain_quantity -= inventory.stock_quantity
#                             inventory.stock_quantity = 0

#                         seller_names.append(str(inventory.seller))
#                         quantity_costs.append(str(inventory.quantity_cost))
#                         selling_quantities.append(str(quantity_decreased))

#                         # Log country-specific transaction
#                         InventoryTransaction.objects.create(
#                             inventory=inventory,
#                             product=product,
#                             quantity=-quantity_decreased,
#                             reason='sale',
#                             ref_id=cart_obj.id
#                         )
#                         inventory.save()

#                     # Save batch details to the cart item
#                     cart_item.seller_name = ", ".join(seller_names)
#                     cart_item.purchase_quantity_cost = ", ".join(quantity_costs)
#                     cart_item.selling_quantity = ", ".join(selling_quantities)
#                     cart_item.save()

#                 # Clean up empty batches
#                 Inventory.objects.filter(Q(is_cancelled=True) & Q(stock_quantity=0)).delete()

#                 # 4. Finalize Order
#                 order_obj, _ = Order.objects.new_or_get(request, shipping_instance, cart_obj)
#                 order_obj.total_product_price = cart_obj.get_total()
#                 order_obj.total_cost = cart_obj.get_total()
#                 order_obj.due = cart_obj.get_total()
#                 order_obj.voucher = cart_obj.get_coupon_discount_percentage()
#                 order_obj.country = selected_country
#                 order_obj.notes = user_notes
#                 order_obj.save()

#                 # Clear session
#                 request.session['cart_items'] = 0
#                 if 'cart_id' in request.session:
#                     del request.session['cart_id']

#             messages.success(request, "Your order is successfully completed")
#             return redirect('checkout-done', slug=order_obj.slug)
            
#     else:
#         billing_form = BillingForm(instance=request.user)
#         initial_shipping = {
#             'first_name': request.user.first_name,
#             'last_name': request.user.last_name,
#             'email': request.user.email,
#             'contact_number': request.user.contact_number,
#             'country': request.user.country,
#         }
#         shipping_form = shippingForm(instance=user_address, initial=initial_shipping)

#     context = {
#         "cart": cart_obj,
#         "billing_form": billing_form,
#         "form": shipping_form,
#         "errors": billing_form.errors or shipping_form.errors,
#     }
#     return render(request, "orders/checkout/checkout.html", context)



"""