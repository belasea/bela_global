
from django.db.models import JSONField
from django.db import models
from django.contrib.auth import get_user_model
from offers.models import Coupon
from products.models import Product
from decimal import Decimal
from django.utils import timezone
import re
from django.db.models import Sum, F
from decimal import Decimal, InvalidOperation



User = get_user_model()


class CartManager(models.Manager):
    def new_or_get(self, request):
        cart_id = request.session.get("cart_id", None)
        qs = self.get_queryset().filter(id=cart_id)

        if qs.count() == 1:
            new_obj = False
            cart_obj = qs.first()
            if request.user.is_authenticated and cart_obj.owner is None:
                cart_obj.owner = request.user
                cart_obj.save()
        else:
            user_obj = None
            if request.user.is_authenticated:
                user_obj = request.user

            cart_obj = self.new(user=user_obj)
            new_obj = True
            request.session['cart_id'] = cart_obj.id

        return cart_obj, new_obj

    def new(self, user=None):
        user_obj = None
        if user is not None:
            user_obj = user
        return self.model.objects.create(owner=user_obj)


class Cart(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    items = models.ManyToManyField('CartItem', related_name='cart_items', blank=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    objects = CartManager()

    def __str__(self):
        return f"Cart #{self.id} for {self.owner.username if self.owner else 'Guest'}"

    def get_count(self):
        count = 0
        for item in self.cart_items.all():
            count += item.quantity
        return count
    
    
    def total_weight(self):
        total = Decimal('0.0')
        for item in self.cart_items.all():
            # Calculate weight for the main product
            if item.product and item.product.weight:
                try:
                    product_weight = Decimal(item.product.weight[:-2])
                    total += product_weight * Decimal(item.quantity)
                except (InvalidOperation, ValueError):
                    continue
        return total


    def get_coupon_discount_percentage(self):
        if self.coupon and self.coupon.active:
            now = timezone.now()
            if self.coupon.valid_from <= now <= self.coupon.valid_to:
                return self.coupon.coupon_discount
        return Decimal(0.0)
    

    def get_sub_total(self):
        total_cost = Decimal(0.0)
        for cart_item in self.cart_items.all():
            item_cost = Decimal(cart_item.quantity) * Decimal(cart_item.price)
            total_cost += item_cost
        return total_cost
    

    def get_total(self):
        total_cost = Decimal(0.0)
        for cart_item in self.cart_items.all():
            item_cost = Decimal(cart_item.quantity) * Decimal(cart_item.price)
            total_cost += item_cost
        total_with_discount = total_cost - self.get_coupon_discount_percentage()
        return total_with_discount
    
    
class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveSmallIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    last_purchase_price = models.DecimalField(default=0.0, max_digits=10, decimal_places=2)
    weight_avg_cost = models.DecimalField(default=0.0, max_digits=10, decimal_places=2)
    seller_name = JSONField(default=list, blank=True, null=True)
    purchase_quantity_cost = JSONField(default=list, blank=True, null=True)
    selling_quantity = JSONField(default=list, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)


    @property
    def line_total(self):
        """
        Calculates the total price for this specific line item (quantity * price).
        """
        return Decimal(self.quantity) * Decimal(self.price)
    
    def get_total_price(self):
        return self.quantity * self.product.price


    def cart_item_total(self):
        total = Decimal(self.quantity) * Decimal(self.price)
        return total
    
    
    def total_profit(self):
        profit = Decimal(self.cart_item_total()) - Decimal(self.quantity * self.weight_avg_cost)
        return profit
    

    def quantity_cost(self):
        quantity = Decimal(self.weight_avg_cost) * Decimal(self.quantity)
        return quantity
    
    
    def single_profit(self):
        profit = Decimal(self.price) - Decimal(self.weight_avg_cost)
        return profit
    

    