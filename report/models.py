from django.db import models
from orders.models import Order
from bella_global.countries import COUNTRIES_TYPES  

# Create your models here.

class CustomerManagerQueryset(models.query.QuerySet):
    def by_range(self, start_date, end_date=None):
        if end_date is None:
            return self.filter(update__gte=start_date, cancelled=False)
        return self.filter(timestamp__date__gte=start_date, timestamp__date__lte=end_date)


class CustomerManager(models.Manager):
    def get_queryset(self):
        return CustomerManagerQueryset(self.model, using=self._db)

    def customer_info(self, start_date, end_date):
        return self.get_queryset().by_range(start_date, end_date)


CUSTOMER_TYPE = [
    ('Good Customer', 'Good Customer'),
    ('Bad Customer', 'Bad Customer'),
]


DELIVERY_CONFORMATIONS = [
    ('Send', 'Send'),
    ('Cancel', 'Cancel'),
    ('Return', 'Return'),
    ('Need to call', 'Need to call'),
    ('Unanswered call', 'Unanswered call'),
    ('Delivery Successful', 'Delivery Successful'),
]


class CustomerReport (models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='customer_reports', blank=True, null=True)
    country = models.CharField(max_length=150, choices=COUNTRIES_TYPES, blank=True, null=True)
    order_conf_date = models.DateField(blank=True, null=True)
    delivery_conformations = models.CharField(max_length=50, choices=DELIVERY_CONFORMATIONS, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    customer_type = models.CharField(max_length=20, choices=CUSTOMER_TYPE, blank=True, null=True)
    parcel_send_receipt = models.FileField(upload_to='Customer/', null=True, blank=True)
    approve = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    objects = CustomerManager()

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return self.order.order_id
    

