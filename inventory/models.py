
from django.db import models
from django.db.models import Sum
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone
from products.models import Product
from the_bella.countries import COUNTRIES_TYPES
from .utils import inventory_unique_slug_generator

# --- Inventory Manager ---
class InventoryManagerQueryset(models.query.QuerySet):
    def by_range(self, start_date, end_date=None):
        if end_date is None:
            return self.filter(update__gte=start_date)
        return self.filter(timestamp__date__gte=start_date, timestamp__date__lte=end_date)

class InventoryManager(models.Manager):
    def get_queryset(self):
        return InventoryManagerQueryset(self.model, using=self._db)

    def inventory_by_date(self, start_date, end_date):
        return self.get_queryset().by_range(start_date, end_date)

# --- Inventory Model (The Purchase Batches) ---
class Inventory(models.Model):
    pro_id = models.ForeignKey(Product, on_delete=models.PROTECT, null=True)
    country = models.CharField(max_length=150, choices=COUNTRIES_TYPES, blank=True, null=True)
    purchase_date = models.DateTimeField()
    quantity_cost = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    purchase_quantity = models.IntegerField(default=0)
    stock_quantity = models.IntegerField(default=0)
    seller = models.CharField(max_length=200)
    expiry_date = models.DateField(null=True, blank=True)
    is_cancelled = models.BooleanField(default=False)
    quantity_updated = models.BooleanField(default=False, help_text="Internal tracking")
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    slug = models.SlugField(blank=True, null=True)

    objects = InventoryManager()

    class Meta:
        ordering = ['-purchase_date']
        verbose_name_plural = "Inventories"

    def __str__(self):
        return f"{self.pro_id.title} ({self.country})"
    


# --- Inventory Stock Model (The Aggregated Totals) ---
class InventoryStock(models.Model):
    pro_id = models.ForeignKey(Product, verbose_name='Product Name', on_delete=models.CASCADE)
    country = models.CharField(max_length=150, choices=COUNTRIES_TYPES)
    stock_quantity = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('pro_id', 'country')
        ordering = ['pro_id']

    def __str__(self):
        return f"{self.pro_id.title} - {self.country}: {self.stock_quantity}"
    

# --- SIGNALS ---

@receiver(pre_save, sender=Inventory)
def inventory_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = inventory_unique_slug_generator(instance)

@receiver(post_save, sender=Inventory)
def inventory_post_save_receiver(sender, instance, created, **kwargs):
    """
    Step 1: When a new inventory batch is added, update the stock total 
    for that specific product in that specific country.
    """
    if instance.country:
        total_stock = Inventory.objects.filter(
            pro_id=instance.pro_id,
            country=instance.country,
            is_cancelled=False
        ).aggregate(Sum('stock_quantity'))['stock_quantity__sum'] or 0
        
        InventoryStock.objects.update_or_create(
            pro_id=instance.pro_id,
            country=instance.country,
            defaults={'stock_quantity': total_stock}
        )
        

@receiver(post_save, sender=InventoryStock)
def inventory_stock_post_save_receiver(sender, instance, **kwargs):
    product = instance.pro_id
    
    # Calculate total stock across ALL countries (BD, UK, etc.)
    total_global_stock = InventoryStock.objects.filter(
        pro_id=product
    ).aggregate(Sum('stock_quantity'))['stock_quantity__sum'] or 0

    # Only deactivate if EVERY country is out of stock
    if total_global_stock > 0:
        product.active = True
    else:
        product.active = False

    product.save(update_fields=['active'])

# --- Transaction Model ---
class InventoryTransaction(models.Model):
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    reason = models.CharField(max_length=20, choices=[('sale','Sale'), ('cancel','Cancel')])
    ref_id = models.CharField(max_length=120, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_restored = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.product.title} | {self.reason} | {self.quantity}"