from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.db.models.functions import ExtractMonth, ExtractYear
from django.http import StreamingHttpResponse
import csv
from decimal import Decimal
from django.utils import timezone
from datetime import datetime, timedelta
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.db.models import Prefetch, Q, Sum, Count
from addresses.models import Address
from products.models import Product
from orders.models import Order
from carts.models import Cart
from .models import CustomerReport
from carts.models import Cart
from .forms import CustomerReportForm
from bella_global.countries import get_country_dropdown_data


# Customer =========================================================
def customer_report(request):
    # Fetch the customer data with related invoice and address data
    posts_list = CustomerReport.objects.select_related('order')

    # Handle search query
    query = request.GET.get('q')
    if query:
        query = query.strip()
        name_filters = Q()
        if ' ' in query:
            firstname, lastname = query.split(' ', 1)
            name_filters = Q(order__shipping_address__first_name__icontains=firstname) & Q(order__shipping_address__last_name__icontains=lastname)
        else:
            name_filters = Q(order__shipping_address__first_name__icontains=query) | Q(order__shipping_address__last_name__icontains=query)

        posts_list = posts_list.filter(
            name_filters |
            Q(order__shipping_address__contact_number__icontains=query) |
            Q(order__shipping_address__address__icontains=query) |
            Q(shipping_method__icontains=query) |
            Q(notes__icontains=query) |
            Q(order__slug__icontains=query) |
            Q(order__cart__cart_items__product__title__icontains=query)
        ).distinct()

    # Optimize related data fetching
    posts_list = posts_list.prefetch_related(
        Prefetch('order__shipping_address', queryset=Address.objects.only('first_name', 'last_name', 'contact_number', 'address')),
        Prefetch('order__cart__cart_items__product', queryset=Product.objects.only('title'))
    )

    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(posts_list, 8)  # 10 posts per page
    
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
    return render(request, "report/customer_report/customer_list.html", context)


def update_customer_report(request, id):
    page = request.GET.get('page', '1')
    obj = get_object_or_404(CustomerReport, pk=id)
    form = CustomerReportForm(request.POST or None, request.FILES or None, instance=obj)
    
    if form.is_valid():
        form.save()
        messages.success(request, 'Customer successfully Updated')
        
        # 1. Reverse the LIST view name (customer-report)
        # 2. Append the page number to the query string
        url = f"{reverse('customer-report')}?page={page}"
        
        return redirect(url)
    
    context = {
        'form': form,
        'obj': obj
    }
    return render(request, 'report/customer_report/update_customer.html', context)


def delete_customer_report(request, id):
    if request.user.is_superuser:
        obj = get_object_or_404(CustomerReport, id=id)
        context = {
            'obj': obj
        }
        if request.method == "POST":
            obj.delete()
            messages.add_message(request, messages.WARNING, 'Successfully Delete Customer')
            return redirect("customer-report")
        return render(request, "report/customer_report/deleteCustomer.html", context)
    else:
        messages.add_message(request, messages.WARNING, "Sorry you can't access this")
        return redirect("customer-report")
    

class Echo:
    def write(self, value):
        return value

def customer_report_csv(request):
    if not request.user.is_authenticated:
        messages.error(request, "Access denied.")
        return redirect('customer-report')

    if request.method == "POST":
        try:
            start_date_str = request.POST.get('start-date')
            end_date_str = request.POST.get('end-date')
            user_country = getattr(request.user, 'country', None)

            if not start_date_str or not user_country:
                messages.error(request, "Missing date or country profile.")
                return redirect('customer-report')

            # 1. Optimize Queryset
            # select_related for 1-to-1/ForeignKey, prefetch_related for M2M
            queryset = CustomerReport.objects.filter(
                country__iexact=user_country
            ).select_related(
                'order', 
                'order__shipping_address', 
                'order__cart__owner'
            ).order_by('-timestamp')

            # 2. Date Filtering (on the Report's timestamp)
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            if end_date_str:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                queryset = queryset.filter(timestamp__date__range=[start_date, end_date])
            else:
                queryset = queryset.filter(timestamp__date=start_date)

            # 3. Row Generator
            def row_generator():
                pseudo_buffer = Echo()
                writer = csv.writer(pseudo_buffer)
                
                # Header Row
                yield writer.writerow([
                    'Report ID', 'Order ID', 'Conf Date', 'Country', 
                    'Customer Name', 'Contact', 'Status', 'Customer Type', 
                    'Total Price', 'Notes'
                ])

                for report in queryset.iterator(chunk_size=1000):
                    order = report.order
                    shipping = order.shipping_address if order else None
                    
                    yield writer.writerow([
                        report.id,
                        order.order_id if order else "N/A",
                        report.order_conf_date,
                        report.country,
                        shipping.first_name if shipping else "N/A",
                        shipping.contact_number if shipping else "N/A",
                        report.delivery_conformations,
                        report.customer_type,
                        order.total_product_price if order else 0,
                        report.notes,
                    ])

            # 4. Return Streamed Response
            filename = f"customer_reports_{user_country}_{start_date_str}.csv"
            response = StreamingHttpResponse(row_generator(), content_type="text/csv")
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response

        except Exception as e:
            messages.error(request, f"Export failed: {str(e)}")
            return redirect('customer-report')

    return redirect('customer-report')



def sales_report(request):
    ITEMS_PER_PAGE = 10
    query = request.GET.get('q', '')
    
    orders = Order.objects.filter(cancelled=False).order_by('-timestamp')
    if query:
        orders = orders.filter(
            Q(order_id__icontains=query) |
            Q(shipping_address__first_name__icontains=query) |
            Q(shipping_address__email__icontains=query) |
            Q(shipping_address__contact_number__icontains=query) |
            Q(shipping_address__address__icontains=query) |
            Q(shipping_address__city__icontains=query) |
            Q(shipping_address__location__icontains=query)
        ).distinct()
    
    processed_invoices = []
    for order in orders:
        
        for entry in order.cart.cart_items.all():
            sellers = entry.seller_name.split(',') if entry.seller_name else ["No Seller"]
            selling_quantities = [Decimal(q) for q in entry.selling_quantity.split(',')] if entry.selling_quantity else [Decimal('0.00')]
            purchase_costs = [Decimal(c) for c in entry.purchase_quantity_cost.split(',')] if entry.purchase_quantity_cost else [Decimal('0.00')]
            
            unit_price = Decimal(entry.price or 0)
            product_prices = [q * unit_price for q in selling_quantities]
            product_costs = [q * c for q, c in zip(selling_quantities, purchase_costs)]
            single_profits = [p - c for p, c in zip(product_prices, product_costs)]
            
            for seller, quantity, product_price, purchase_cost, product_cost, single_profit in zip(
                sellers, selling_quantities, product_prices, purchase_costs, product_costs, single_profits
            ):
                
                product_type, product_name, product_brand = "Normal", "Unknown", None
    
                if entry.product:
                    product_type = "Normal"
                    product_name = entry.product.title
                processed_invoices.append({
                    'order_id': order.order_id,
                    'timestamp': order.timestamp,
                    'status': order.status,
                    'product_type': product_type,
                    'product_name': product_name,
                    'quantity': quantity,
                    'seller': seller,
                    'purchase_cost': purchase_cost,
                    'parcel_price': order.parcel_price,
                    'delivery_charge': order.delivery_charge,
                    'due_calculation': order.due_calculation,
                    'received': order.received,
                    'voucher': order.voucher,
                    'total_product_price': entry.cart.get_total(),
                    'total_quantity_cost': order.total_quantity_cost,
                    'total_profit_invoice': order.entry_total_profit,
                    'product_weight': entry.product,
                    'price': entry.price,
                    'product_price': product_price,
                    'product_cost': product_cost,
                    'single_profit': single_profit,
                    'customer_name': order.shipping_address.first_name,
                    'email': order.shipping_address.email,
                    'contact_number': order.shipping_address.contact_number,
                    'address': order.shipping_address.address,
                    'city': order.shipping_address.city,
                    'location': order.shipping_address.location,
                })
    
    paginator = Paginator(processed_invoices, ITEMS_PER_PAGE)
    page = request.GET.get('page', 1)
    invoices_page = paginator.get_page(page)
    context = {
        'processed_invoices': invoices_page, 
        'paginator': paginator,
    }
    return render(request, 'report/sales_report/sales_report.html', context)


class Echo:
    """An object that implements just the write method of the file-like interface."""
    def write(self, value):
        return value

def generate_csv(processed_invoices):
    """Generator function to yield CSV rows."""
    echo = Echo()
    writer = csv.writer(echo)
    
    # Write header row
    headers = [
        'SN', 'Order ID', 'Date', 'Status', 'Product Type', 'Product Name', 'Quantity',
        'Seller', 'Parcel Price', 'Delivery Charge', 'Due', 'Received', 'Voucher',
        'Total Product Price', 'Total Quantity Cost', 'Total Profit', 'Weight', 'Unit Price',
        'Purchase Cost', 'Product Price', 'Product Cost', 'Profit', 'Customer Name',
        'Email', 'Contact Number', 'Address', 'City', 'Location'
    ]
    yield writer.writerow(headers)

    # Process each invoice
    for index, item in enumerate(processed_invoices, start=1):
        yield writer.writerow([
            index,
            item['order_id'],
            item['timestamp'],
            item['status'],
            item['product_type'],
            item['product_name'],
            item['quantity'],
            item['seller'],
            item['parcel_price'],
            item['delivery_charge'],
            item['due_calculation'],
            item['received'],
            item['voucher'],
            item['total_product_price'],
            item['total_quantity_cost'],
            item['total_profit_invoice'],
            item['product_weight'],
            item['price'],
            item['purchase_cost'],
            item['product_price'],
            item['product_cost'],
            item['single_profit'],
            item['customer_name'],
            item['email'],
            item['contact_number'],
            item['address'],
            item['city'],
            item['location'],
        ])

def export_sales_report(request):
    """Handles exporting the sales report as a CSV file."""
    if request.method == "POST":
        # Generate processed_invoices here
        orders = Order.objects.filter(cancelled=False).order_by('-timestamp')
        processed_invoices = []

        for order in orders:
            for entry in order.cart.cart_items.all():
                sellers = entry.seller_name.split(',') if entry.seller_name else ["No Seller"]
                selling_quantities = [Decimal(q) for q in entry.selling_quantity.split(',')] if entry.selling_quantity else [Decimal('0.00')]
                purchase_costs = [Decimal(c) for c in entry.purchase_quantity_cost.split(',')] if entry.purchase_quantity_cost else [Decimal('0.00')]

                unit_price = Decimal(entry.price or 0)
                product_prices = [q * unit_price for q in selling_quantities]
                product_costs = [q * c for q, c in zip(selling_quantities, purchase_costs)]
                single_profits = [p - c for p, c in zip(product_prices, product_costs)]

                for seller, quantity, product_price, purchase_cost, product_cost, single_profit in zip(
                    sellers, selling_quantities, product_prices, purchase_costs, product_costs, single_profits
                ):
                    product_type, product_name = "Normal", "Unknown", None

                    if entry.product:
                        product_type = "Normal"
                        product_name = entry.product.title
        
                    processed_invoices.append({
                        'order_id': order.order_id,
                        'timestamp': order.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        'status': order.status,
                        'product_type': product_type,
                        'product_name': product_name,
                        'quantity': quantity,
                        'seller': seller,
                        'purchase_cost': purchase_cost,
                        'parcel_price': order.parcel_price,
                        'delivery_charge': order.delivery_charge,
                        'due_calculation': order.due_calculation,
                        'received': order.received,
                        'voucher': order.voucher,
                        'total_product_price': entry.cart.get_total(),
                        'total_quantity_cost': order.total_quantity_cost,
                        'total_profit_invoice': order.entry_total_profit,
                        'product_weight': entry.product.weight if entry.product else "Unknown",
                        'price': entry.price,
                        'product_price': product_price,
                        'product_cost': product_cost,
                        'single_profit': single_profit,
                        'customer_name': order.shipping_address.first_name,
                        'email': order.shipping_address.email,
                        'contact_number': order.shipping_address.contact_number,
                        'address': order.shipping_address.address,
                        'city': order.shipping_address.city,
                        'location': order.shipping_address.location,
                    })

        if not processed_invoices:
            return redirect('sales-report')

        response = StreamingHttpResponse(generate_csv(processed_invoices), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'
        return response

    return redirect('sales-report')


def order_annual_sales(request):
    context = {}
    today = timezone.now()
    
    # 1. Initialize variables and get filter options
    selected_country = request.POST.get('country', '')
    context['country_list'] = get_country_dropdown_data(selected_country)

    # 2. Handle POST Request for specific Month + Country filter
    if request.method == 'POST':
        date_input = request.POST.get('salesByMonthYear')
        selected_country = request.POST.get('country')
        
        if date_input and selected_country:
            try:
                year, month = map(int, date_input.split("-"))
                orders = Order.objects.filter(
                    timestamp__year=year,
                    timestamp__month=month,
                    country__iexact=selected_country,
                    cancelled=False
                )
                
                # Calculate Net Sales (Price - Delivery)
                sales_result = orders.aggregate(
                    total=Sum('total_product_price') - Sum('delivery_charge')
                )['total'] or 0

                context.update({
                    'selected_month_sales_price': sales_result,
                    'selected_month': timezone.datetime(year, month, 1).strftime("%B"),
                    'selected_year': year,
                })
            except ValueError:
                messages.warning(request, "Invalid date format.")
    
    # Save selected_country back to context so dropdown stays selected
    context['selected_country'] = selected_country

    # 3. Country-wise Monthly Sales (The aggregated list)
    country_monthly_sales = Order.objects.filter(cancelled=False).values(
        'country', 
        year=ExtractYear('timestamp'), 
        month=ExtractMonth('timestamp')
    ).annotate(
        total_sales=Sum('total_product_price')
    ).order_by('-year', '-month', 'country')

    for item in country_monthly_sales:
        item['month_name'] = timezone.datetime(2000, item['month'], 1).strftime('%B')
    
    context['country_monthly_sales'] = country_monthly_sales

    # 4. Last 7 Days Sales (Filtered by selected_country if exists)
    seven_sales_data = []
    for i in range(7):
        day = today - timedelta(days=i)
        
        day_filters = {
            'timestamp__date': day.date(),
            'cancelled': False
        }
        
        if selected_country:
            day_filters['country__iexact'] = selected_country

        day_sales = Order.objects.filter(**day_filters).aggregate(
            total=Sum('total_product_price') - Sum('delivery_charge')
        )['total'] or 0

        seven_sales_data.append({
            "day_name": day.strftime("%A"),
            "date": day.date(),
            "sales_price": day_sales,
        })
    
    context['seven_sales_data'] = seven_sales_data

    return render(request, 'report/sales_report/annual_sales_summary.html', context)


