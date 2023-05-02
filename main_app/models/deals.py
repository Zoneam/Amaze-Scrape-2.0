from django.db import models
from datetime import datetime

class Store(models.Model):
    name = models.CharField(max_length=40, blank=True)
    # link = models.URLField(max_length = 250, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def age(self):
        return (datetime.now().replace(tzinfo=None) - self.created_at.replace(tzinfo=None)).days
    
    def __str__(self):
        return self.name

class Product(models.Model):    
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='store')
    title = models.CharField(max_length=250, blank=True)
    was = models.EmailField(max_length=254, null=True, blank=True)
    current = models.URLField(max_length = 250, null=True, blank=True)
    imgLink = models.URLField(max_length = 250, null=True, blank=True)
    link = models.URLField(max_length = 250, null=True, blank=True)
    discount = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.store.name
    
# class Price(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product')
#     price = models.FloatField(null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.product.title