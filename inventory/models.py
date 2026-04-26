from django.db import models
from django.utils.text import slugify
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
from django.db.models import Sum
from django.utils import timezone
from .utils import inventory_unique_slug_generator
from products.models import Product


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


class Inventory(models.Model):
    pro_id = models.ForeignKey(Product, on_delete=models.PROTECT, null=True)
    purchase_date = models.DateTimeField(auto_now_add=False)
    quantity_cost = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    purchase_quantity = models.IntegerField(default=0)
    stock_quantity = models.IntegerField(default=0)
    seller = models.CharField(max_length=200)
    expiry_date = models.DateField(null=True, blank=True)
    is_cancelled = models.BooleanField(default=False)
    quantity_updated = models.BooleanField(default=False, help_text="Do Not Touch")
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    slug = models.SlugField(blank=True, null=True)

    objects = InventoryManager()

    def __str__(self):
        return self.pro_id.title
    
    class Meta:
        ordering = ['-purchase_date']


    @property
    def total_purchase(self):
        return self.quantity_cost * self.purchase_quantity

    @property
    def purchase_date_field(self):
        return self.purchase_date.date()

    @property
    def stock_value(self):
        return self.quantity_cost * (self.purchase_quantity - self.damage_quantity)

    @property
    def stock_loss(self):
        return self.quantity_cost * self.damage_quantity
    
    
    def in_stock(self):
        inventory = InventoryStock.objects.filter(
            pro_id__title=self.title)
        inventory = inventory.first()
        return inventory.stock_quantity

    @property
    def date_of_stock(self):
        if self.stock_quantity >= 0:
            stock_time = {'current_time': timezone.now(), 'timedelta': timezone.now() - self.timestamp}
            return stock_time

def inventory_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = inventory_unique_slug_generator(instance)


pre_save.connect(inventory_pre_save_receiver, sender=Inventory)


# @receiver(post_save, sender=Inventory)
# def inventory_post_save_receiver(sender, instance, *args, **kwargs):
#     if not instance.quantity_updated:
#         # Calculate the total stock quantity for the product
#         stock_sum = sender.objects.filter(pro_id=instance.pro_id).aggregate(Sum('stock_quantity'))['stock_quantity__sum'] or 0
        
#         # Update the InventoryStock record directly if stock_sum is different
#         updated_rows = InventoryStock.objects.filter(pro_id=instance.pro_id).update(stock_quantity=stock_sum)

#         if updated_rows:  
#             # Mark quantity_updated as True only if an update happened
#             sender.objects.filter(id=instance.id).update(quantity_updated=True)


@receiver(post_save, sender=Inventory)
def inventory_post_save_receiver(sender, instance, created, **kwargs):
    # 1. Calculate the total stock quantity for this product from all Inventory records
    total_stock = Inventory.objects.filter(
        pro_id=instance.pro_id,
        is_cancelled=False  # Good practice: exclude cancelled inventory
    ).aggregate(Sum('stock_quantity'))['stock_quantity__sum'] or 0
    
    # 2. Update or Create the InventoryStock record
    # update_or_create ensures that if the product isn't in the stock table yet, it gets added
    inventory_stock, created_stock = InventoryStock.objects.update_or_create(
        pro_id=instance.pro_id,
        defaults={'stock_quantity': total_stock}
    )

    # 3. Prevent recursion by using .update() to set the flag 
    # This avoids triggering the post_save signal again
    if not instance.quantity_updated:
        Inventory.objects.filter(id=instance.id).update(quantity_updated=True)
        

class InventoryStockQueryset(models.query.QuerySet):
    def by_range(self, start_date, end_date=None):
        if end_date is None:
            return self.filter(update__gte=start_date)
        return self.filter(timestamp__date__gte=start_date, timestamp__date__lte=end_date)


class InventoryStockManager(models.Manager):
    def get_queryset(self):
        return InventoryStockQueryset(self.model, using=self._db)

    def product_inventory_list_by_date(self, start_date, end_date):
        return self.get_queryset().by_range(start_date, end_date)


class InventoryStock(models.Model):
    pro_id = models.OneToOneField(
        Product, verbose_name='Product Name', on_delete=models.CASCADE)
    stock_quantity = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    objects = InventoryStockManager()

    class Meta:
        ordering = ['pro_id']

    def __str__(self):
        return self.pro_id.title

    @property
    def get_title(self):
        return self.pro_id.title


@receiver(post_save, sender=InventoryStock)
def inventory_stock_post_save_receiver(sender, instance, *args, **kwargs):
    pro_id = instance.pro_id_id
    stock_quantity = instance.stock_quantity

    # Set product active to False if stock_quantity is 0, else True
    Product.objects.filter(id=pro_id).update(active=stock_quantity > 0)

post_save.connect(inventory_stock_post_save_receiver, sender=InventoryStock)


class InventoryTransaction(models.Model):
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # keep this
    quantity = models.IntegerField()
    reason = models.CharField(max_length=20, choices=[('sale','Sale'), ('cancel','Cancel')])
    ref_id = models.IntegerField(null=True, blank=True)  # optional: cart/order id
    timestamp = models.DateTimeField(auto_now_add=True)
    is_restored = models.BooleanField(default=False)  # for restocked items

    def __str__(self):
        return f"{self.product.title} | {self.reason} | {self.quantity}"