from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Category, Blog, Advertisement, Comment, Reply
from notification.models import Subscribe


def blog(request):
    cat = Category.objects.all()
    blog_list = Blog.objects.all().order_by('-timestamp')
    recent_post = blog_list[:4]
    advertisement = Advertisement.objects.first()
    paginator = Paginator(blog_list, 1) 
    page = request.GET.get('page')
    
    try:
        blogs = paginator.page(page)
    except PageNotAnInteger:
        blogs = paginator.page(1)
    except EmptyPage:
        blogs = paginator.page(paginator.num_pages)
        
    context = {
        'cat': cat,
        'object_list': blogs,
        'recent_post': recent_post,
        'advertisement': advertisement
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

        # --- Handle Standard Comment ---
        name = request.POST.get('name')
        email = request.POST.get('email')
        body = request.POST.get('body')
        
        Comment.objects.create(
            post=blog,
            name=name,
            email=email,
            body=body,
            approve=False
        )
        messages.info(request, "Your comment is awaiting approval.")
        return redirect('blog-details', slug=blog.slug)

    context = {
        'cat': cat,
        'blog': blog,
        'related_blogs': related_blogs,
        'comments': comments,
        'advertisement': advertisement
    }
    return render(request, "blog/blog_details.html", context)


    