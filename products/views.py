from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.db.models import Q, F
from decimal import Decimal, InvalidOperation
from products.models import Product
from django.contrib.contenttypes.models import ContentType
from analytics.models import ObjectViewed
from analytics.utils import get_client_ip
from products.models import Category, SubCategory, Product
from comments.models import Product, Comment, Reply
from comments.forms import CommentForm


def category_view(request):
    categories = Category.objects.all()
    # Get the first category to use as a default
    active_category = categories.first()
    # If a category exists, get its subcategories; otherwise, return an empty list
    subcategories = active_category.subcategories.all() if active_category else []
    
    context = {
        "categories": categories,
        "active_category": active_category,
        "subcategories": subcategories,
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
    product = get_object_or_404(Product, slug=slug, active=True)
    # TRACK VIEW
    ObjectViewed.objects.create(
        user=request.user if request.user.is_authenticated else None,
        ip_address=get_client_ip(request),
        content_type=ContentType.objects.get_for_model(product),
        object_id=product.id
    )

    related_products = Product.objects.filter(
        category=product.category, active=True
    ).exclude(id=product.id)[:10]
    
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


@user_passes_test(lambda u: u.is_superuser)
def edit_comment_item(request, item_type, item_id):
    # Dynamically get the model (Comment or Reply)
    model = Comment if item_type == 'comment' else Reply
    obj = get_object_or_404(model, id=item_id)
    
    # Get slug for redirection
    product_slug = obj.post.slug if item_type == 'comment' else obj.comment.post.slug

    if request.method == "POST":
        action = request.POST.get('action')
        
        if action == "delete":
            obj.delete()
            messages.warning(request, f"{item_type.capitalize()} deleted.")
        
        elif action == "update":
            new_body = request.POST.get('body')
            if new_body:
                obj.body = new_body
                obj.save()
                messages.success(request, f"{item_type.capitalize()} updated.")
                
        return redirect('product_details', slug=product_slug)
    

@user_passes_test(lambda u: u.is_superuser)
def delete_comment_item(request, item_type, item_id):
    if request.method == "POST":
        if item_type == 'comment':
            obj = get_object_or_404(Comment, id=item_id)
        else:
            obj = get_object_or_404(Reply, id=item_id)
            
        product_slug = obj.post.slug if item_type == 'comment' else obj.comment.post.slug
        obj.delete()
        messages.warning(request, f"{item_type.capitalize()} deleted successfully.")
        return redirect('product_details', slug=product_slug)


def search_view(request):
    query = request.GET.get('q', '').strip()
    sort_by = request.GET.get('sort_by')
    min_price = request.GET.get('min', 0.00)
    max_price = request.GET.get('max', 10000.00)

    # Start with the base queryset for products
    queryset = Product.objects.filter(active=True)

    # Apply search filter only if query exists
    if query:
        queryset = Product.objects.filter(
            Q(title__icontains=query) |
            Q(title__startswith=query) |
            Q(title__endswith=query) |
            Q(description__icontains=query) |
            Q(category__title__icontains=query) |
            Q(sub_category__title__icontains=query)
        ).order_by('-timestamp').distinct()
        
    # Apply price range filter
    try:
        min_price = Decimal(min_price)
        max_price = Decimal(max_price)
        queryset = queryset.filter(price__range=(min_price, max_price))
    except (InvalidOperation, TypeError):
        messages.error(request, "Enter a valid numeric value for price range.")

    # Apply sorting
    sorting_map = {
        "1": "title",
        "2": "-title",
        "3": "price",
        "4": "-price",
    }
   
    # Paginate results
    paginator = Paginator(queryset, 4)
    page = request.GET.get('page', 1)
    try:
        object_list = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        object_list = paginator.page(1)

    context = {
        'object_list': object_list,
        'page_title': query or "All Products",
        'query': query,
    }

    return render(request, "products/search_product.html", context)
