# from django.db import models
# from django.utils.text import slugify
# from django.dispatch import receiver
# from django.db.models.signals import pre_save, post_save
# from django.db.models import Sum
# from django.utils import timezone
# from .utils import inventory_unique_slug_generator
# from products.models import Product
# from bella_global.countries import COUNTRIES_TYPES

# class InventoryManagerQueryset(models.query.QuerySet):
#     def by_range(self, start_date, end_date=None):
#         if end_date is None:
#             return self.filter(update__gte=start_date)
#         return self.filter(timestamp__date__gte=start_date, timestamp__date__lte=end_date)


# class InventoryManager(models.Manager):
#     def get_queryset(self):
#         return InventoryManagerQueryset(self.model, using=self._db)

#     def inventory_by_date(self, start_date, end_date):
#         return self.get_queryset().by_range(start_date, end_date)


# class Inventory(models.Model):
#     pro_id = models.ForeignKey(Product, on_delete=models.PROTECT, null=True)
#     country = models.CharField(max_length=150, choices=COUNTRIES_TYPES, blank=True, null=True)
#     purchase_date = models.DateTimeField(auto_now_add=False)
#     quantity_cost = models.DecimalField(max_digits=20, decimal_places=2, default=0)
#     purchase_quantity = models.IntegerField(default=0)
#     stock_quantity = models.IntegerField(default=0)
#     seller = models.CharField(max_length=200)
#     expiry_date = models.DateField(null=True, blank=True)
#     is_cancelled = models.BooleanField(default=False)
#     quantity_updated = models.BooleanField(default=False, help_text="Do Not Touch")
#     timestamp = models.DateTimeField(auto_now_add=True)
#     update = models.DateTimeField(auto_now=True)
#     slug = models.SlugField(blank=True, null=True)

#     objects = InventoryManager()

#     def __str__(self):
#         return self.pro_id.title
    
#     class Meta:
#         ordering = ['-purchase_date']


#     @property
#     def total_purchase(self):
#         return self.quantity_cost * self.purchase_quantity

#     @property
#     def purchase_date_field(self):
#         return self.purchase_date.date()

#     @property
#     def stock_value(self):
#         return self.quantity_cost * (self.purchase_quantity - self.damage_quantity)

#     @property
#     def stock_loss(self):
#         return self.quantity_cost * self.damage_quantity

#     @property
#     def date_of_stock(self):
#         if self.stock_quantity >= 0:
#             stock_time = {'current_time': timezone.now(), 'timedelta': timezone.now() - self.timestamp}
#             return stock_time

# def inventory_pre_save_receiver(sender, instance, *args, **kwargs):
#     if not instance.slug:
#         instance.slug = inventory_unique_slug_generator(instance)


# pre_save.connect(inventory_pre_save_receiver, sender=Inventory)


# # @receiver(post_save, sender=Inventory)
# # def inventory_post_save_receiver(sender, instance, created, **kwargs):
# #     total_stock = Inventory.objects.filter(
# #         pro_id=instance.pro_id,
# #         is_cancelled=False  # Good practice: exclude cancelled inventory
# #     ).aggregate(Sum('stock_quantity'))['stock_quantity__sum'] or 0
    
# #     inventory_stock, created_stock = InventoryStock.objects.update_or_create(
# #         pro_id=instance.pro_id,
# #         defaults={'stock_quantity': total_stock}
# #     )

# #     if not instance.quantity_updated:
# #         Inventory.objects.filter(id=instance.id).update(quantity_updated=True)
    
# @receiver(post_save, sender=Inventory)
# def inventory_post_save_receiver(sender, instance, created, **kwargs):
#     # Calculate stock for THIS product in THIS country
#     total_stock = Inventory.objects.filter(
#         pro_id=instance.pro_id,
#         country=instance.country,
#         is_cancelled=False
#     ).aggregate(Sum('stock_quantity'))['stock_quantity__sum'] or 0
    
#     # Update or create the stock entry for that specific country
#     InventoryStock.objects.update_or_create(
#         pro_id=instance.pro_id,
#         country=instance.country,
#         defaults={'stock_quantity': total_stock}
#     )

# class InventoryStockQueryset(models.query.QuerySet):
#     def by_range(self, start_date, end_date=None):
#         if end_date is None:
#             return self.filter(update__gte=start_date)
#         return self.filter(timestamp__date__gte=start_date, timestamp__date__lte=end_date)


# class InventoryStockManager(models.Manager):
#     def get_queryset(self):
#         return InventoryStockQueryset(self.model, using=self._db)

#     def product_inventory_list_by_date(self, start_date, end_date):
#         return self.get_queryset().by_range(start_date, end_date)


# class InventoryStock(models.Model):
#     pro_id = models.OneToOneField(
#         Product, verbose_name='Product Name', on_delete=models.CASCADE)
#     country = models.CharField(max_length=150, choices=COUNTRIES_TYPES, blank=True, null=True)
#     stock_quantity = models.IntegerField(default=0)
#     timestamp = models.DateTimeField(auto_now_add=True)
#     update = models.DateTimeField(auto_now=True)

#     objects = InventoryStockManager()

#     class Meta:
#         unique_together = ('pro_id', 'country')

#     def __str__(self):
#         return self.pro_id.title

#     @property
#     def get_title(self):
#         return self.pro_id.title

# @receiver(post_save, sender=InventoryStock)
# def inventory_stock_post_save_receiver(sender, instance, *args, **kwargs):
#     pro_id = instance.pro_id_id
#     stock_quantity = instance.stock_quantity

#     # Set product active to False if stock_quantity is 0, else True
#     Product.objects.filter(id=pro_id).update(active=stock_quantity > 0)

# post_save.connect(inventory_stock_post_save_receiver, sender=InventoryStock)



# class InventoryTransaction(models.Model):
#     inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)  # keep this
#     quantity = models.IntegerField()
#     reason = models.CharField(max_length=20, choices=[('sale','Sale'), ('cancel','Cancel')])
#     ref_id = models.IntegerField(null=True, blank=True)  # optional: cart/order id
#     timestamp = models.DateTimeField(auto_now_add=True)
#     is_restored = models.BooleanField(default=False)  # for restocked items

#     def __str__(self):
#         return f"{self.product.title} | {self.reason} | {self.quantity}"


from django.db import models
from django.db.models import Sum
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone

from products.models import Product
from bella_global.countries import COUNTRIES_TYPES
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
    # CHANGE: Use ForeignKey instead of OneToOneField to allow multiple countries per product
    pro_id = models.ForeignKey(Product, verbose_name='Product Name', on_delete=models.CASCADE)
    country = models.CharField(max_length=150, choices=COUNTRIES_TYPES)
    stock_quantity = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    class Meta:
        # CRITICAL: This ensures one unique stock total per product-country pair
        unique_together = ('pro_id', 'country')
        ordering = ['pro_id']

    def __str__(self):
        return f"{self.pro_id.title} - {self.country}: {self.stock_quantity}"

# --- Signals ---

@receiver(pre_save, sender=Inventory)
def inventory_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = inventory_unique_slug_generator(instance)

@receiver(post_save, sender=Inventory)
def inventory_post_save_receiver(sender, instance, created, **kwargs):
    """Updates the aggregated stock for the specific product and country."""
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
    """Checks if the product is globally out of stock across ALL countries."""
    total_global_stock = InventoryStock.objects.filter(pro_id=instance.pro_id).aggregate(
        Sum('stock_quantity'))['stock_quantity__sum'] or 0
    
    # Update product status based on global availability
    Product.objects.filter(id=instance.pro_id.id).update(active=total_global_stock > 0)

# --- Transaction Model ---
class InventoryTransaction(models.Model):
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    reason = models.CharField(max_length=20, choices=[('sale','Sale'), ('cancel','Cancel')])
    ref_id = models.IntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_restored = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.product.title} | {self.reason} | {self.quantity}"