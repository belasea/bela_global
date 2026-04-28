from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .utils import unique_slug_generator


class HomeCategory(models.Model):
    """Sections like 'New', 'Essentials', 'Star products'"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True, help_text="Used for the data-target (e.g., 'group-new')")
    display_order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ['display_order']
        verbose_name = "Home Category"
        verbose_name_plural = "Home Categories"

    def __str__(self):
        return self.name


class HomeCategoryItem(models.Model):
    """Specific items displayed in the HomeSections"""
    COLOR_CHOICES = [
        ('bg-pink', 'Pink'),
        ('bg-mint', 'Mint'),
        ('bg-yellow', 'Yellow'),
    ]
    title = models.CharField(max_length=150, help_text="Overrides product title for homepage")
    sub_title = models.CharField(max_length=50)
    home_category = models.ForeignKey(HomeCategory, on_delete=models.CASCADE, related_name='items')
    image = models.ImageField(upload_to='home/items/')
    card_color = models.CharField(max_length=20, choices=COLOR_CHOICES, default='bg-pink')
    display_order = models.PositiveIntegerField(default=0)
    slug = models.SlugField(unique=True, null=True, blank=True, db_index=True)

    class Meta:
        ordering = ['display_order']
        verbose_name = "Home Category Item"
        verbose_name_plural = "Home Category Items"
        indexes = [
            models.Index(fields=['home_category', 'display_order']),
        ]

    def __str__(self):
        return f"{self.home_category.name} - {self.title}"


class Category(models.Model):
    """Main Product Categories (e.g., Skincare, Haircare)"""
    title = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.title


class SubCategory(models.Model):
    title = models.CharField(max_length=50)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    slug = models.SlugField(unique=True, null=True, blank=True)
    # New Fields for the Template
    subheading = models.CharField(
        max_length=255, blank=True, 
        help_text="e.g., Scaly skin. Hyperkeratosis"
    )
    description = models.TextField(blank=True, null=True)
    right_for_me = models.TextField(
        blank=True, verbose_name="Is it right for me?"
    )
    dermatologist_advice = models.TextField(
        blank=True, verbose_name="Advice from a dermatologist"
    )
    range_details = models.TextField(
        blank=True, verbose_name="Get to know the range"
    )

    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']
        verbose_name_plural = "Sub Categories"

    def __str__(self):
        return f"{self.category.title} > {self.title}"


class Product(models.Model):
    """The actual products"""
    title = models.CharField(max_length=200, db_index=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    sub_category = models.ForeignKey(
        SubCategory, on_delete=models.CASCADE, 
        related_name='products'
    )
    image = models.ImageField(upload_to='products/')
    price = models.DecimalField(decimal_places=2, max_digits=20) 
    old_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    weight = models.CharField(max_length=20, help_text='e.g., 20ml or 20gm')
    limit_buy = models.BooleanField(default=False, blank=True)
    active = models.BooleanField(default=True, db_index=True)
    slug = models.SlugField(unique=True, null=True, blank=True, db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    
    
    @property
    def get_discount(self):
        """
        Calculate the discount percentage for the product.
        """
        if self.old_price > 0:
            discount = ((self.old_price - self.price) / self.old_price) * 100
            return round(discount, 2)
        else:
            return 0

    class Meta:
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['sub_category']),
            models.Index(fields=['price']),
            models.Index(fields=['active', 'update']),
        ]
        ordering = ['-timestamp']


    def __str__(self):
        return self.pro_id
    

    @property
    def get_discount(self):
        return 10

    @property
    def pro_id(self):
        product_id = 'SKU000' + str(self.id)
        return product_id
    
   

# --- SIGNALS ---
@receiver(pre_save, sender=HomeCategory)
@receiver(pre_save, sender=HomeCategoryItem)
@receiver(pre_save, sender=Category)
@receiver(pre_save, sender=SubCategory)
@receiver(pre_save, sender=Product)
def slug_pre_save_receiver(sender, instance, *args, **kwargs):
    """
    Universal slug generator for all models listed in the decorators above.
    """
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)