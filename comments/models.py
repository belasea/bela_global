from django.db import models
from products.models import Product

# Create your models here.
class Comment(models.Model):
    post = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
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