from django.db import models
from django.urls import reverse
from django.conf import settings
from django.core.validators import RegexValidator
from bella_global.countries import COUNTRIES_TYPES  

User = settings.AUTH_USER_MODEL


class AddressManagerQueryset(models.query.QuerySet):
    def by_range(self, start_date, end_date=None):
        if end_date is None:
            return self.filter(update__gte=start_date)
        return self.filter(timestamp__date__gte=start_date, timestamp__date__lte=end_date)


class AddressManager(models.Manager):
    def get_queryset(self):
        return AddressManagerQueryset(self.model, using=self._db)

    def address_by_date(self, start_date, end_date):
        return self.get_queryset().by_range(start_date, end_date)


ADDRESS_TYPES = (
    ('billing', 'Billing Address'),
    ('shipping', 'Shipping Address'),
)


class Address(models.Model):
    user = models.OneToOneField(User, blank=True, null=True, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    email = models.EmailField(max_length=150)
    phone_regex = RegexValidator(
        regex=r"^(?:\+88|01)?\d{11}$",
        message="Phone number must be entered in the format: '+88 01987132107'. Up to 15 digits allowed."
    )
    contact_number = models.CharField(validators=[phone_regex], max_length=15, blank=True)
    address_type = models.CharField(max_length=120, choices=ADDRESS_TYPES)
    country = models.CharField(max_length=150, choices=COUNTRIES_TYPES, blank=True, null=True)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=120)
    location = models.CharField(max_length=120, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    objects = AddressManager()

    def __str__(self):
        return self.first_name

    class Meta:
        ordering = ['-update']

    def get_absolute_url(self):
        return reverse("address-update", kwargs={"pk": self.pk})

    def get_short_address(self):
        for_name = self.first_name + ' ' + self.last_name

        return "{for_name}, {line1}, {city}".format(
            for_name=for_name,
            line1=self.address,
            city=self.city
        )

    def get_address(self):
        return "{for_name}\n{line1}\n{city} {location}".format(
            for_name=self.first_name + ' ' + self.last_name,
            line1=self.address,
            city=self.city,
            location=self.location,
        )

    def get_parcel_address(self):
        return "{address},{city} {location}".format(
            address=self.address,
            city=self.city,
            location=self.location,
        )
    

    def get_user_address(self):
        return "{address},{city}".format(
            address=self.address,
            city=self.city,
        )