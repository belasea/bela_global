from django.utils import timezone
from django.utils.timezone import now
import datetime
from decimal import Decimal
from django.db.models import Sum, Avg, Count, Q
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver
from .utils import (
    order_unique_slug_generator, 
    cancelled_order_unique_slug_generator,
    returned_order_unique_slug_generator
)
from offers.models import Coupon
from addresses.models import Address
from products.models import Product
from carts.models import Cart


User = get_user_model()

ORDER_STATUS_CHOICES = (
    ('created', 'Created'),
    ('paid', 'Paid'),
    ('success', 'Success'),
    ('shipped', 'Shipped'),
    ('refunded', 'Refunded'),
)

class OrderManager(models.Manager):

    def new_or_get(self, request, address_obj, cart_obj):
        created = False
        queryset = self.get_queryset().filter(
            shipping_address=address_obj,
            cart=cart_obj
        )
        if queryset.exists():
            order_obj = queryset.first()
            if request.user.is_authenticated and order_obj.user is None:
                order_obj.user = request.user
                order_obj.save()
        else:
            order_obj = self.new(request.user, address_obj, cart_obj)
            created = True
        return order_obj, created

    def new(self, user=None, shipping_address=None, cart=None):
        user_obj = user if user and user.is_authenticated else None
        return self.model.objects.create(user=user_obj, shipping_address=shipping_address, cart=cart)
    
class Order(models.Model):
    order_id = models.CharField(max_length=120, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    country = models.CharField(max_length=150, blank=True, null=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    shipping_address = models.ForeignKey(Address, on_delete=models.PROTECT)
    status = models.CharField(max_length=120, default='created', choices=ORDER_STATUS_CHOICES)
    total_product_price = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    due = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    received = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    delivery_method = models.PositiveIntegerField(default=0)
    delivery_charge = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    discount = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    voucher = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    amount_collected = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    cancelled = models.BooleanField(default=False)
    returned = models.BooleanField(default=False)
    permit_to_edit = models.BooleanField(default=False)
    notes = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    slug = models.SlugField(blank=True, null=True)

    objects = OrderManager()

    def __str__(self):
        return self.order_id
    
    class Meta:
        ordering = ['-timestamp']
        

    def save(self, *args, **kwargs):
        if not self.timestamp:
            self.timestamp = now()

        if not self.order_id:
            order_count = (
                Order.objects.filter(
                    timestamp__year=self.timestamp.year,
                    timestamp__month=self.timestamp.month,
                    timestamp__day=self.timestamp.day
                ).count() + 1
            )
            self.order_id = f'bella-{self.timestamp.strftime("%d-%m-%y")}-{order_count}'

        if not self.slug:
            self.slug = order_unique_slug_generator(self)

        super().save(*args, **kwargs)

    
    @property
    def total_quantity_cost(self):
        quantity_cost = 0
        for items in self.cart.cart_items.all():
            quantity_cost += items.quantity * items.weight_avg_cost
        return quantity_cost
    

    @property
    def total_profit_order(self):
        if self.voucher:
            profit = 0
            for entry in self.cart.cart_items.all():
                profit += entry.quantity * entry.single_profit()
            return profit - self.voucher
        else:
            profit = 0
            for entry in self.cart.cart_items.all():
                profit += entry.quantity * entry.single_profit()
            return profit


    @property
    def get_profit(self):
        import_cost = Decimal(0.0)
        for  items in self.cart.cart_items.all():
            import_cost +=  items.quantity *  items.weight_avg_cost

        return self.cart.get_total() - import_cost, import_cost
    

     # New Sales Report ==================================
    def entry_total_profit(self):
        total_profit = Decimal(0.0)

        for entry in self.cart.cart_items.all():
            # Handle selling quantities and purchase costs
            selling_quantity = entry.selling_quantity.split(',') if entry.selling_quantity else ["0.00"]
            purchase_costs = entry.purchase_quantity_cost.split(',') if entry.purchase_quantity_cost else ["0.00"]
            
            # Convert quantities and costs to Decimal
            selling_quantity = [Decimal(q) for q in selling_quantity]
            purchase_costs = [Decimal(c) for c in purchase_costs]
            
            # Calculate product price and product cost
            unit_price = Decimal(entry.price) if entry.price else Decimal('0.00')
            product_price = [quantity * unit_price for quantity in selling_quantity]
            product_cost = [quantity * cost for quantity, cost in zip(selling_quantity, purchase_costs)]
            
            # Calculate profit for each entry
            profit = [price - cost for price, cost in zip(product_price, product_cost)]
            total_profit += sum(profit)
        
        return total_profit
    

    @property
    def total_quantity_cost(self):
        quantity_cost = Decimal(0.0)

        for entry in self.cart.cart_items.all():
            selling_quantity = entry.selling_quantity.split(',') if entry.selling_quantity else ["0.00"]
            purchase_costs = entry.purchase_quantity_cost.split(',') if entry.purchase_quantity_cost else ["0.00"]
            selling_quantity = [Decimal(q) for q in selling_quantity]
            purchase_costs = [Decimal(c) for c in purchase_costs]
            product_cost = sum(quantity * cost for quantity, cost in zip(selling_quantity, purchase_costs))
            quantity_cost += product_cost
        
        return quantity_cost
    

    @property
    def parcel_price(self):
        try:
            p_price = Decimal(0.0)
            for i in self.cart.order_set.all():
                p_price = i.total_product_price + i.delivery_charge - i.voucher
            return p_price
        except:
            p_price = Decimal(0.0)
            for i in self.cart.invoice_set.all():
                p_price = i.total_product_price + i.delivery_charge
            return p_price
    

    @property
    def discounted_price_calculation(self):
        try:
            total_p_price = self.total_product_price - self.voucher
            return total_p_price
        except:
            total_p_price = self.total_product_price
            return total_p_price


    @property
    def due_calculation(self):
        try:
            due = self.total_product_price - self.voucher - self.received
            return due
        except:
            due = self.total_product_price
            return due


    @property
    def amount_to_be_collect(self):
        try:
            due_amount = self.due_calculation + self.delivery_charge
            return due_amount
        except:
            due_amount = self.total_product_price
            return due_amount
    

class CancelledOrder(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    slug = models.SlugField(blank=True, null=True)
    cancelled_id = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.cancelled_id
    
    class Meta:
        ordering = ['-timestamp']

    def save(self, *args, **kwargs):
        if not self.cancelled_id:
            today = datetime.date.today()
            cancelled_order_count = CancelledOrder.objects.filter(
                timestamp__year=today.year,
                timestamp__month=today.month,
                timestamp__day=today.day
            ).aggregate(count=Count('id'))['count'] + 1
            self.cancelled_id = f'cancel-{today.strftime("%y-%m-%d")}-{cancelled_order_count}'

        if not self.slug:
            self.slug = cancelled_order_unique_slug_generator(self)

        super(CancelledOrder, self).save(*args, **kwargs)


class ReturnedOrder(models.Model):
    returned_id = models.CharField(max_length=100, unique=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    loss = models.DecimalField(default=0.00, max_digits=6, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    slug = models.SlugField(blank=True, null=True)
    
    def __str__(self):
        return self.returned_id
    
    class Meta:
        ordering = ['-timestamp']


    @property
    def calculate_loss(self):
        # Calculate the loss based on the delivery charge
        self.loss = self.order.delivery_charge

    def save(self, *args, **kwargs):
        # Ensure loss is calculated before saving
        self.calculate_loss()
        super(ReturnedOrder, self).save(*args, **kwargs)


    def save(self, *args, **kwargs):
        if not self.returned_id:
            today = timezone.localdate()
            returned_order_count = ReturnedOrder.objects.filter(
                timestamp__year=today.year,
                timestamp__month=today.month,
                timestamp__day=today.day
            ).aggregate(count=Count('id'))['count'] + 1
            self.returned_id = f'returned-{today.strftime("%y-%m-%d")}-{returned_order_count}'

        if not self.slug:
            self.slug = returned_order_unique_slug_generator(self)

        super(ReturnedOrder, self).save(*args, **kwargs)
