from django.db import models
from django.db.models.signals import pre_save
from .utils import blog_unique_slug_generator



class Category(models.Model):
    title = models.CharField(max_length=120)
    slug = models.SlugField(null=True, blank=True, max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-timestamp']


def category_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = blog_unique_slug_generator(instance)


pre_save.connect(category_pre_save_receiver, sender=Category)


class Blog(models.Model):
    title = models.CharField(max_length=120)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.FileField(upload_to="blog/", blank=True, null=True)
    facebook_url = models.URLField(blank=True, null=True, max_length=50)
    instagram_url = models.URLField(blank=True, null=True, max_length=50)
    twitter_url = models.URLField(blank=True, null=True, max_length=50)
    linkedin_url = models.URLField(blank=True, null=True, max_length=50)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(null=True, blank=True, max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-timestamp']


def blog_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = blog_unique_slug_generator(instance)


pre_save.connect(blog_pre_save_receiver, sender=Blog)


class Comment(models.Model):
    post = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField(blank=True, null=True)
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    approve = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_on']

    def __str__(self):
        return 'Comment {} by {}'.format(self.body, self.name)
    

class Reply(models.Model):
    # Link to the main comment
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='replies')
    name = models.CharField(max_length=80, default="Admin") # Default to Admin for your design
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    approve = models.BooleanField(default=True) # Usually replies are pre-approved if by admin

    class Meta:
        ordering = ['created_on']
        verbose_name_plural = "Replies"

    def __str__(self):
        return f'Reply by {self.name} to {self.comment.name}'
    

class Advertisement(models.Model):
    title = models.CharField(max_length=120, blank=True, null=True)
    image = models.FileField(blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    url_field = models.URLField(max_length=120, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-timestamp']


