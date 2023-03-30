from django.db import models
from django.contrib.auth.models import User

class Wm_Product(models.Model):
    wm_title = models.CharField(max_length=350, blank=True)
    wm_price = models.FloatField(null=True, blank=True)
    wm_imgLink = models.URLField(max_length = 650, null=True, blank=True)
    wm_link = models.URLField(max_length = 650, null=True, blank=True)
    grade = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class Amazon_Product(models.Model):
    amazon_title = models.CharField(max_length=350, blank=True)
    amazon_price = models.FloatField(null=True, blank=True)
    amazon_imgLink = models.URLField(max_length = 650, null=True, blank=True)
    amazon_link = models.URLField(max_length = 650, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    wm_product = models.ForeignKey(Wm_Product, on_delete=models.CASCADE, related_name='wm_product')
    amazon_product = models.ForeignKey(Amazon_Product, on_delete=models.CASCADE, related_name='amazon_product')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.amazon_product.title