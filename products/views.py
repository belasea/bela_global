from django.shortcuts import render, get_object_or_404, redirect
from products.models import Category, SubCategory


def category_list(request):
    categories = Category.objects.all()
    context = {
        "categories": categories
    }
    return render(request, "products/category_list.html", context)


def product_category(request, category_slug):
    categories = Category.objects.all()
    # Default to the first category if none is selected
    if category_slug:
        active_category = get_object_or_404(Category, slug=category_slug)
    else:
        active_category = categories.first()

    # Get subcategories for the active category
    subcategories = active_category.subcategories.all() if active_category else []

    context = {
        'categories': categories,
        'active_category': active_category,
        'subcategories': subcategories,
    }
    return render(request, "products/product_category.html", context)


def product_details(request):
    return render(request, "products/product_details.html")