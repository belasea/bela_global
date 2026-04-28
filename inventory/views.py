from django.shortcuts import render, get_object_or_404, HttpResponse, redirect
from django.contrib import messages
import csv
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from . forms import ProductInventoryCreateForm
from inventory.models import Inventory, InventoryStock
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from products.models import Product


# Inventory CRUD Operations ============================================
@login_required
def inventory_list(request):
    posts_list = Inventory.objects.all().order_by('-timestamp')
    query = request.GET.get('q')
    if query:
        posts_list = Inventory.objects.filter(
            Q(pro_id__brand__title__icontains=query) |
            Q(pro_id__title__icontains=query) |
            Q(seller__icontains=query)
        ).distinct()
    page = request.GET.get('page', 1)
    paginator = Paginator(posts_list, 10)
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
    return render(request, 'inventory/inventory_list/inventory_list.html', context)



@login_required
def add_inventory(request):
    if request.method == "POST":
        form = ProductInventoryCreateForm(request.POST or None)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "Added new inventory")
            return redirect('inventory-list')
    else:
        form = ProductInventoryCreateForm()
    context = {
        'form': form,
        'products': Product.objects.all()
    }
    return render(request, "inventory/inventory_list/inventory_form.html", context)


@login_required
def update_inventory(request, id):
    page = request.GET.get("page")
    obj = get_object_or_404(Inventory, id=id)
    form = ProductInventoryCreateForm(request.POST or None, request.FILES or None, instance=obj)
    if form.is_valid():
        form.save()
        messages.add_message(request, messages.SUCCESS, "Inventory successfully Updated !")
        url = reverse_lazy("inventory-list") + "?page=" + page
        return redirect(url)
    context = {
        'form': form,
        'products': Product.objects.all(),
    }
    return render(request, "inventory/inventory_list/inventory_update.html", context)


@login_required
def delete_inventory(request, id):
    if request.user.is_superuser:
        # fetch the object related to passed id
        obj = get_object_or_404(Inventory, pk=id)
        context = {
            'obj': obj
        }
        if request.method == "POST":
            obj.delete()
            messages.add_message(request, messages.WARNING, 'Product Inventory successfully deleted')
            return redirect("inventory-list")
        return render(request, "inventory/inventory_list/inventory_delete.html", context)
    else:
        messages.add_message(request, messages.WARNING, "Sorry you can't access this")
        return redirect("inventory-list")


@login_required
def inventory_by_date_csv(request):
    if request.method == "POST":
        start_date = request.POST.get('start-date')
        end_date = request.POST.get('end-date', None)
        queryset = Inventory.objects.inventory_by_date(start_date, end_date)
        response = HttpResponse(content_type='text/csv')
        writer = csv.writer(response)
        writer.writerow(
            [
                "Product ID", "Product Title", "Purchase Date", "Quantity cost", "Purchase Quantity",
                "Stock Quantity", "Seller", "Quantity Updated"
            ]
        )
        for q in queryset:
            row = []
            row.extend([
                q.pro_id, q.pro_id.title, q.purchase_date_field, q.quantity_cost, q.purchase_quantity,
                q.stock_quantity, q.seller, q.quantity_updated
            ])
            writer.writerow(row[:])
        response['Content-Disposition'] = 'attachment; filename="inventory.csv"'
        return response


@login_required
def inventory_by_purchase_date(request):
    if request.method == "POST":
        start_date = request.POST.get('start-date')
        end_date = request.POST.get('end-date', None)
        queryset = Inventory.objects.filter(purchase_date__range=[start_date, end_date])
        response = HttpResponse(content_type='text/csv')
        writer = csv.writer(response)
        writer.writerow(
            [
                "Product ID", "Product Title", "Purchase Date", "Quantity cost", "Purchase Quantity",
                "Stock Quantity", "Seller", "Quantity Updated"
            ]
        )
        for q in queryset:
            row = []
            row.extend([
                q.pro_id, q.pro_id.title, q.purchase_date_field, q.quantity_cost, q.purchase_quantity,
                q.stock_quantity, q.seller, q.quantity_updated
            ])
            writer.writerow(row[:])
        response['Content-Disposition'] = 'attachment; filename="purchase-inventory.csv"'
        return response


@login_required
def inventory_stock_csv(request):
    queryset = InventoryStock.objects.all()
    response = HttpResponse(content_type="text/csv")
    writer = csv.writer(response)
    writer.writerow(['ID', 'Title', 'Stock Quantity', "Actual Quantity"])
    for q in queryset:
        row = []
        row.extend([
            q.pro_id, q.pro_id.title, q.stock_quantity, '',
        ])
        writer.writerow(row[:])
    response['Content-Disposition'] = 'attachment; filename="inventory_list.csv"'
    return response


@login_required
def out_of_stock(request):
    posts_list = Inventory.objects.all()
    query = request.GET.get('q', '')
    if query:
        query = query.strip()
        posts_list = Inventory.objects.filter(
            Q(pro_id__title__icontains=query) |
            Q(seller__icontains=query)
        ).distinct()
    page = request.GET.get('page', 1)
    paginator = Paginator(posts_list, 10)  # 5 posts per page
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
    return render(request, "inventory/out_of_stock/out_of_stock.html", context)


@login_required
def out_of_stock_csv(request):
    queryset = Inventory.objects.all()
    response = HttpResponse(content_type="text/csv")
    writer = csv.writer(response)
    writer.writerow(['ID', 'Product Name', 'Category', 'Date of Stock Out', 'Date of Purchase', 'Last Purchase Quantity'])
    for q in queryset:
        row = []
        if q.date_of_stock:
            row.extend([
                q.pro_id, q.pro_id.title, q.pro_id.category, q.date_of_stock['current_time'], q.purchase_date,
                q.stock_quantity
            ])
        else:
            row.extend([
                q.pro_id, q.pro_id.title, q.pro_id.category, " ", q.purchase_date, q.stock_quantity
            ])
        writer.writerow(row[:])
        response['Content-Disposition'] = 'attachment; filename="out-of-stock.csv"'
    return response


def check_stock_quantity(request):
    queryset = Inventory.objects.filter(stock_quantity__gte=2)
    response = HttpResponse(content_type="text/csv")
    writer = csv.writer(response)
    writer.writerow(['ID', 'Product Name', 'Purchase Quantity', 'Stock Quantity', 'Active'])
    for q in queryset:
        row = []
        row.extend([
            q.pro_id, q.pro_id.title, q.purchase_quantity, q.stock_quantity, q.pro_id.active
        ])
        writer.writerow(row[:])
        response['Content-Disposition'] = 'attachment; filename="check-stock-quantity.csv"'
    return response