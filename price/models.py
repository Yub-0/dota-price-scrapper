from django.db import models

# Create your models here.
class Item(models.Model):
    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(decimal_places=2, max_digits=2, null=True)
    update_date = models.DateTimeField(auto_now=False)