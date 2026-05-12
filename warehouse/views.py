from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.http import HttpResponse, StreamingHttpResponse
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, Prefetch
import csv
from datetime import datetime, date
from django.shortcuts import redirect
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order
from .models import WarehouseOrderDetail
from .forms import (
    WarehouseOrderDetailForm,
)


"""==========================================
        Warehouse
==========================================="""

def warehouse_list(request):
    
    query = request.GET.get('q', '').strip()
    page = request.GET.get('page', 1)
    per_page = 10

    # 1. Authentication Check
    if not request.user.is_authenticated:
        context = {
            'error': 'Login required'
        }
        return render(request, 'warehouse/warehouse_order/warehouse_order.html', context)
    
    user_country = getattr(request.user, 'country', None)
    queryset = WarehouseOrderDetail.objects.all()

    if user_country:
        queryset = queryset.filter(country__iexact=user_country)
    else:
        queryset = queryset.none()
    
    if query:
        queryset = queryset.filter(
            Q(slug__icontains=query) | 
            Q(order_id__icontains=query) |
            Q(order_number__slug__iexact=query) |
            Q(order_number__slug__icontains=query) |
            Q(order_number__slug__contains=query) |
            Q(order_number__slug__startswith=query)
        ).distinct()
    
    # 7. Pagination
    paginator = Paginator(queryset, per_page)
    try:
        obj = paginator.page(page)
    except PageNotAnInteger:
        obj = paginator.page(1)
    except EmptyPage:
        obj = paginator.page(paginator.num_pages)
        
    context = {
        'object_list': obj,
        'page': page,
        'order_number': Order.objects.values('id', 'slug').order_by('-timestamp')
    }

    return render(request, "warehouse/warehouse_order/warehouse_order.html", context)


def add_warehouse(request):
    errors = None
    if request.method == "POST":
        form = WarehouseOrderDetailForm(request.POST or request.FILES or None)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, 'Successfully added Warehouse.')
            return redirect('warehouse-list')
        if form.errors:
            messages.add_message(request, messages.SUCCESS, 'Invoice Already Exists')
            errors = form.errors
    else:
        form = WarehouseOrderDetailForm()

    context = {
        'form': form,
        'errors': errors,
        'order_number': Order.objects.values('id', 'slug').order_by('-timestamp')
    }

    return render(request, "warehouse/warehouse_order/warehouse_order.html", context)


def update_warehouse(request, id):
    page = request.GET.get('page', '')  # Default to empty string if None
    obj = get_object_or_404(WarehouseOrderDetail, pk=id)
    form = WarehouseOrderDetailForm(request.POST or None, instance=obj)

    if form.is_valid():
        form.save()
        messages.success(request, 'Successfully Updated Warehouse.')
        url = reverse_lazy('warehouse-list')

        # Append page only if it's not empty
        if page:
            url += f"?page={page}"
            
        return redirect(url)
    return render(request, "warehouse/warehouse_order/warehouse_order.html", {'form': form, 'edit_obj': obj })


def delete_warehouse(request, id):
    obj = get_object_or_404(WarehouseOrderDetail, pk=id)
    context = {
        'obj': obj
    }
    if request.method == "POST":
        obj.delete()
        messages.add_message(request, messages.WARNING, 'Successfully Delete Order ID In Warehouse')
        return redirect("warehouse-list")
    return render(request, "warehouse/warehouse_order/warehouse_order.html", context)

def export_warehouse_csv(request):
    if request.method == "POST":
        start_date = request.POST.get('start-date')
        end_date = request.POST.get('end-date')

        if not start_date or not end_date:
            messages.error(request, "Please select both start date and end date.")
            return redirect('warehouse-list')

        try:
            queryset = WarehouseOrderDetail.objects.warehouse_order_detail_by_date(start_date, end_date)
            response = HttpResponse(content_type="text/csv")
            response['Content-Disposition'] = 'attachment; filename="warehouse.csv"'

            writer = csv.writer(response)
            writer.writerow(['ID', 'Order Number', 'Product Name', 'Quantity', 'Notes', 'Date', 'Request By'])

            for q in queryset:
                for product in q.order_number.cart.cart_items.all():
                    if not product.product:
                        continue
                    
                    writer.writerow([
                        q.id, 
                        q.order_number, 
                        product.product.title if product.product else "Unknown Product",
                        product.quantity, 
                        q.order_number.notes, 
                        q.date, 
                        q.request_by
                    ])

            return response
        except Exception as e:
            messages.error(request, f"An error occurred while generating the CSV: {str(e)}")
            return redirect('warehouse-list')



# Normal Product Summary ==================================================
def normal_product_summary(request):
    products = {}
    today = date.today()
    invoices = WarehouseOrderDetail.objects.filter(
        timestamp__year=today.year, timestamp__month=today.month, timestamp__day=today.day
    )

    # Filter the invoices based on the search query if provided
    query = request.GET.get('q')
    if query:
        invoices = invoices.filter(
            Q(order_number__cart__cart_items__product__title__icontains=query)
        )

    # Summarize product quantities
    for inv in invoices:
        for product_entry in inv.order_number.cart.cart_items.all():
            if product_entry.product:
                product_id = product_entry.product.pro_id
                product_name = product_entry.product.title
                quantity = product_entry.quantity

                if product_id in products:
                    products[product_id]['value'] += quantity
                else:
                    products[product_id] = {'value': quantity, 'product_name': product_name}

    context = {
        'products': products,
        'query': query,
    }

    return render(request, "warehouse/product_summary/product_summary.html", context)


def export_today_product_summary(request):
    response = HttpResponse(content_type="text/csv")
    writer = csv.writer(response)
    writer.writerow(
        ['SKU', 'Product Name', 'Quantity']
    )
    products = {}
    today = date.today()
    invoices = WarehouseOrderDetail.objects.filter(
        timestamp__year=today.year, timestamp__month=today.month,
        timestamp__day=today.day)
    for inv in invoices:
        for product_entry in inv.order_number.cart.cart_items.all():
            if product_entry.product.pro_id in products.keys():
                products[product_entry.product.pro_id]['value'] += product_entry.quantity
            else:
                products[product_entry.product.pro_id] = {
                    'value': product_entry.quantity,
                    'product_name': product_entry.product.title
                }

    for key, value in products.items():
        row = [key, value['product_name'], value['value']]

        writer.writerow(row[:])
        filename = f"product-summary-{today.strftime('%Y-%m-%d')}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@csrf_exempt
def product_summary_by_date_csv(request):
    if request.user.is_superuser:
        try:
            if request.method == "POST":
                start_date = request.POST.get('start-date')
                end_date = request.POST.get('end-date', None)
                
                if not start_date:
                    messages.add_message(request, messages.ERROR, "Please select a start date.")
                    return redirect('product-summary')

                response = HttpResponse(content_type='text/csv')
                response.write(u'\ufeff'.encode('utf8'))
                writer = csv.writer(response)
                writer.writerow(['SKU', 'Product Name', 'Quantity', 'Date'])

                products = {}
                invoices = WarehouseOrderDetail.objects.warehouse_order_detail_by_date(start_date, end_date)

                for inv in invoices:
                    for product_entry in inv.order_number.cart.cart_items.all():
                        if product_entry.product.pro_id in products:
                            products[product_entry.product.pro_id]['quantity'] += product_entry.quantity
                        else:
                            products[product_entry.product.pro_id] = {
                                'quantity': product_entry.quantity,
                                'product_name': product_entry.product.title,
                                'date': inv.date
                            }

                for key, value in products.items():
                    row = [key, value['product_name'], value['quantity'], value['date']]
                    writer.writerow(row)

                current_month_text = datetime.now().strftime('%B')
                response['Content-Disposition'] = f'attachment; filename="{current_month_text}-product-summary.csv"'
                return response
        except Exception as e:
            messages.add_message(request, messages.ERROR, f"An error occurred: {str(e)}")
            return redirect('product-summary')
    else:
        messages.add_message(request, messages.ERROR, "Sorry, you have no access to download.")
        return redirect('product-summary')