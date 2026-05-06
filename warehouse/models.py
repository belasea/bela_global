from django.db import models
from orders.models import Order
from bella_global.countries import COUNTRIES_TYPES

class WarehouseOrderDetailQueryset(models.query.QuerySet):
    # This QuerySet filter date by date
    def by_range(self, start_date, end_date=None):
        if end_date is None:
            return self.filter(update__gte=start_date)
        return self.filter(timestamp__date__gte=start_date, timestamp__date__lte=end_date)


class WarehouseOrderDetailManager(models.Manager):
    def get_queryset(self):
        return WarehouseOrderDetailQueryset(self.model, using=self._db)

    def warehouse_order_detail_by_date(self, start_date, end_date):
        return self.get_queryset().by_range(start_date, end_date)


class WarehouseOrderDetail(models.Model):
    order_number = models.ForeignKey(Order, on_delete=models.CASCADE)
    country = models.CharField(max_length=150, choices=COUNTRIES_TYPES, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    request_by = models.CharField(max_length=120, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    objects = WarehouseOrderDetailManager()

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['-timestamp']