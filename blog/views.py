from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from blog.models import Category, Blog, Advertisement, Comment, Reply
from blog.forms import CommentForm
from notification.models import Subscribe
from django.db.models import Q


# def blog(request):
#     cat = Category.objects.all()
#     query = request.GET.get('q')
#     blog_list = Blog.objects.all().order_by('-timestamp')
#     recent_post = blog_list[:4]
#     advertisement = Advertisement.objects.first()
#     paginator = Paginator(blog_list, 1) 
#     page = request.GET.get('page')
    
#     if query:
#         blog_list = blog_list.filter(
#             Q(title__icontains=query)
#         ).distinct()
#     print("query", query)
#     try:
#         blogs = paginator.page(page)
#     except PageNotAnInteger:
#         blogs = paginator.page(1)
#     except EmptyPage:
#         blogs = paginator.page(paginator.num_pages)
        
#     context = {
#         'cat': cat,
#         'object_list': blogs,
#         'recent_post': recent_post,
#         'advertisement': advertisement,
#         'query': query
#     }
#     return render(request, "blog/blog.html", context)


from django.db.models import Q

def blog(request):
    cat = Category.objects.all()
    query = request.GET.get('q')
    
    # 1. Start with the base queryset
    blog_list = Blog.objects.all().order_by('-timestamp')
    
    # 2. FILTER FIRST (If query exists)
    if query:
        blog_list = blog_list.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        ).distinct()
    
    # 3. PAGINATE SECOND (Use the filtered list)
    paginator = Paginator(blog_list, 6) # Set to 6 or 9 for a better grid
    page = request.GET.get('page')
    
    try:
        blogs = paginator.page(page)
    except PageNotAnInteger:
        blogs = paginator.page(1)
    except EmptyPage:
        blogs = paginator.page(paginator.num_pages)
        
    recent_post = Blog.objects.all().order_by('-timestamp')[:4]
    advertisement = Advertisement.objects.first()
        
    context = {
        'cat': cat,
        'object_list': blogs, # This will be empty if no search match found
        'recent_post': recent_post,
        'advertisement': advertisement,
        'query': query
    }
    return render(request, "blog/blog.html", context)


def blog_category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    categories = Category.objects.all()
    blog_list = Blog.objects.filter(category=category).order_by('-timestamp')
    
    paginator = Paginator(blog_list, 5)
    page = request.GET.get('page')
    try:
        blogs = paginator.page(page)
    except PageNotAnInteger:
        blogs = paginator.page(1)
    except EmptyPage:
        blogs = paginator.page(paginator.num_pages)
    
    if request.method == "POST":
        email = request.POST.get('email')
        if email:
            if not Subscribe.objects.filter(email=email).exists():
                Subscribe.objects.create(email=email)
                messages.success(request, "Subscribed successfully!")
            else:
                messages.warning(request, "You are already subscribed!")
        else:
            messages.error(request, "Please enter a valid email!")

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
    context = {
        'category': category,
        'cat': categories,
        'object_list': blogs,
    }
    return render(request, "blog/blog_category.html", context)


def blog_details(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    cat = Category.objects.all()
    related_blogs = Blog.objects.filter(category=blog.category).exclude(id=blog.id)[:3]
    comments = blog.comments.filter(approve=True)
    advertisement = Advertisement.objects.first()
    
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
            return redirect('blog-details', slug=blog.slug)

        
        # --- Handle Standard Comment with Validation ---
        form = CommentForm(request.POST) # Bind POST data to the form
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = blog
            comment.approve = False
            comment.save()
            messages.info(request, "Your comment is awaiting approval.")
            return redirect('blog-details', slug=blog.slug)
        else:
            messages.error(request, "Please correct the errors below.")

    context = {
        'cat': cat,
        'blog': blog,
        'related_blogs': related_blogs,
        'comments': comments,
        'advertisement': advertisement,
        'form': form
    }
    return render(request, "blog/blog_details.html", context)


    