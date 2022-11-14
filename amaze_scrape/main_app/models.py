from django.db import models
from django.urls import reverse
from datetime import date
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Sum
from django.contrib.postgres.fields import ArrayField
# Create your models here.


class Product(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    pieces = ArrayField(models.CharField(max_length=200), blank=True)
    title = models.CharField(max_length=40, blank=True)
    was = models.EmailField(max_length=254, null=True, blank=True)
    current = models.URLField(max_length = 250, null=True, blank=True)
    imgLink = models.URLField(max_length = 250, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.user.username
