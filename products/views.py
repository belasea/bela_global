from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.template.loader import render_to_string
from products.models import Category, SubCategory, Product
from comments.models import Product, Comment, Reply
from comments.forms import CommentForm
from django.contrib import messages


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
    # print("active_category :", active_category)
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
    product = get_object_or_404(Product, slug=slug, active=True)
    related_products = Product.objects.filter(
        category=product.category, active=True
    ).exclude(id=product.id)[:8]
    
    comments = product.comments.filter(approve=True)
    
    form = CommentForm()
    
    if request.method == 'POST':
        # --- Handle Superuser Reply ---
        if 'parent_comment_id' in request.POST:
            if request.user.is_superuser:
                comment_id = request.POST.get('parent_comment_id')
                parent_comment = get_object_or_404(Comment, id=comment_id)
                Reply.objects.create(
                    comment=parent_comment,
                    name=f"{request.user.first_name} {request.user.last_name}" or "Admin",
                    body=request.POST.get('reply_body'),
                    approve=True
                )
                messages.success(request, "Reply posted successfully.")
            return redirect('product_details', slug=product.slug)

        
        # --- Handle Standard Comment with Validation ---
        form = CommentForm(request.POST) # Bind POST data to the form
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = product
            comment.approve = False
            comment.save()
            messages.info(request, "Your comment is awaiting approval.")
            return redirect('product_details', slug=product.slug)
        else:
            messages.error(request, "Please correct the errors below.")
    
    context = {
        'product': product,
        'comments': comments,
        'form': form,
        'related_products': related_products,
    }
    return render(request, "products/product_details.html", context)


