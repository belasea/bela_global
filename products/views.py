from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.template.loader import render_to_string
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


def product_list_view(request, category_slug, subcategory_slug):
    category = get_object_or_404(Category, slug=category_slug)
    subcategory = get_object_or_404(SubCategory, slug=subcategory_slug, category=category)
    active_products = subcategory.products.filter(active=True)

    paginator = Paginator(active_products, 4)
    page_number = request.GET.get('page', 1)
    products = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Render ONLY the product loops
        html = render_to_string('products/subcategory.html', {
            'products': products, 
            'is_ajax': True 
        }, request=request)
        
        return JsonResponse({'html': html,'has_next': products.has_next()})
    
    context = {
        'category': category,
        'subcategory': subcategory,
        'products': products,
    }
    return render(request, 'products/subcategory.html', context)


def product_details(request, slug):
    # Fetch the specific product using the slug from the URL
    product = get_object_or_404(Product, slug=slug, active=True)
    
    context = {
        'product': product,
    }
    return render(request, "products/product_details.html", context)