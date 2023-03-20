from django.db import models
from decimal import Decimal


class Types(models.Model):
    id = models.AutoField(primary_key=True)
    types = models.CharField(max_length=50)

    def __str__(self):
        return self.types

class Units(models.Model):
    id = models.AutoField(primary_key=True)
    units = models.CharField(max_length=10)

    def __str__(self):
        return self.units

class BasePrice(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField()
    units = models.ForeignKey(Units, on_delete=models.CASCADE)
    price_sum = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True, default=None)
    price_dol = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=None)
    types = models.ForeignKey(Types, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}"


class Estimate(models.Model):

    id = models.AutoField(primary_key=True)
    name = models.ForeignKey(BasePrice, on_delete=models.CASCADE, related_name='name_set')
    quantity = models.DecimalField(max_digits=15, decimal_places=2, blank=True)
    units = models.CharField(max_length=10, blank=True)
    types = models.CharField(max_length=50, blank=True)
    price_dol = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True)

    def save(self, *args, **kwargs):
        self.total_price = self.price_dol * Decimal(self.quantity)
        super().save(*args, **kwargs)

class ExchangeRate(models.Model):
    rate = models.DecimalField(decimal_places=2, max_digits=10)
    date = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return str(self.rate)


