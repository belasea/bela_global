from django.db import models
from django.db.models.signals import pre_save
from .utils import unique_slug_generator

class HomeCategory(models.Model):
    """
    Represents sections like 'New', 'Essentials', 'Star products'
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, help_text="Used for the data-target (e.g., 'group-new')")
    display_order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        return self.name
    
    
def product_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)

# Connect to both models
pre_save.connect(product_pre_save_receiver, sender=HomeCategory)


class HomeCategoryItem(models.Model):
    """
    Specific items (linked to Products) displayed in the HomeSections
    """
    COLOR_CHOICES = [
        ('bg-pink', 'Pink'),
        ('bg-mint', 'Mint'),
        ('bg-yellow', 'Yellow'),
    ]
    title = models.CharField(max_length=150, help_text="Overrides product title for homepage")
    short_description = models.CharField(max_length=50)
    section = models.ForeignKey(HomeCategory, on_delete=models.CASCADE, related_name='items')
    image = models.ImageField(upload_to='home/items/')
    card_color = models.CharField(max_length=20, choices=COLOR_CHOICES, default='bg-pink')
    display_order = models.PositiveIntegerField(default=0)
    slug = models.SlugField(unique=True, null=True, blank=True, db_index=True)

    class Meta:
        verbose_name = "Home Category Item"
        verbose_name_plural = "Home Category Items"
        ordering = ['display_order']
    
        indexes = [
            models.Index(fields=['section', 'display_order']),
        ]

    def __str__(self):
        return f"{self.section.name} - {self.title}"


def product_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)

pre_save.connect(product_pre_save_receiver, sender=HomeCategoryItem)