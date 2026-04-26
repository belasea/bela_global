from django.db import models

class TimestampedModel(models.Model):
    """
    An abstract base model class with timestamp and update fields.
    """
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    coupon_discount = models.DecimalField(decimal_places=2, max_digits=5)
    active = models.BooleanField()

    def __str__(self):
        return self.code

