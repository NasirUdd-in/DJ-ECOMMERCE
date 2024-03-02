from django.db import models
from user_account.models import User


# Create your models here.
class Category(models.Model):
    title = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(unique=True, max_length=150)
    featured = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title']

    def __str__(self) -> str:
        return self.title

# class Product(models.Model):
#     seller = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
#     category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
#     title = models.CharField(max_length=250, unique=True)
#     slug = models.SlugField(unique=True, max_length=250)
#     featured = models.BooleanField(default=False)
#     price = models.DecimalField(max_digits=8, decimal_places=2)
#     picture = models.ImageField(upload_to='myproduct',default='img/test.png')
#     thumbnail = models.URLField()
#     description = models.TextField(null=True, blank=True, default='N/A')
#     in_stock = models.BooleanField(default=True)
#     created_date = models.DateTimeField(auto_now_add=True)
#     updated_date = models.DateTimeField(auto_now=True)

#     class Meta:
#         ordering = ['title']

#     def __str__(self) -> str:
#         return self.title

#     @property
#     def related(self):
#         return self.category.products.all().exclude(pk=self.pk)

from django.db import models
from django.utils import timezone

class Product(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    title = models.CharField(max_length=250, unique=True)
    slug = models.SlugField(unique=True, max_length=250)
    featured = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    picture = models.ImageField(upload_to='myproduct',default='img/test.png')
    thumbnail = models.URLField()
    description = models.TextField(null=True, blank=True, default='N/A')
    in_stock = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)


class FlashSales(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="flashsales", default=1)
    title = models.CharField(max_length=50)
    discount = models.PositiveIntegerField(help_text='discount in percentage')
    active = models.BooleanField(default=True)
    active_date = models.DateField()
    expiry_date = models.DateField()
    created_date = models.DateTimeField(auto_now_add=True)


    def __str__(self) ->str:
        return self.title


class Slider(models.Model):
    title = models.CharField(max_length=50)
    banner = models.FileField(upload_to='banners')
    show = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.title


