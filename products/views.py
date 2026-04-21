from django.shortcuts import render, get_object_or_404, redirect
from products.models import Category, SubCategory, Product


def category_view(request):
    categories = Category.objects.all()
    context = {
        "categories": categories
    }
    return render(request, "products/category.html", context)


def product_category_view(request, category_slug):
    categories = Category.objects.all()
    active_category = get_object_or_404(Category, slug=category_slug)
    subcategories = active_category.subcategories.prefetch_related('products').all()

    context = {
        'categories': categories,
        'active_category': active_category,
        'subcategories': subcategories,
    }
    return render(request, "products/category.html", context)


def product_subcategory_view(request):
    return render(request, 'products/product_subcategory.html')


def product_list_view(request, subcategory_slug):
    # Fetch the subcategory or return 404
    subcategory = get_object_or_404(SubCategory, slug=subcategory_slug)
    
    # Fetch products belonging to this subcategory
    products = subcategory.products.filter(active=True)

    context = {
        'subcategory': subcategory,
        'products': products,
    }
    return render(request, 'products/product_list.html', context)


def product_details(request, slug):
    # Fetch the specific product using the slug from the URL
    product = get_object_or_404(Product, slug=slug, active=True)
    
    context = {
        'product': product,
    }
    return render(request, "products/product_details.html", context)