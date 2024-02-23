from django.db import models
from django.conf import settings
# from cart.models import Coupon
from product.models import Product
from decimal import Decimal


class OrderItem (models. Model):
        product = models.ForeignKey (Product, related_name='ordered', on_delete=models.CASCADE)
        price = models.DecimalField (max_digits=8, decimal_places=2)
        quantity= models.PositiveIntegerField()
        admin_share_amount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

        class Meta:
              ordering = ['id']
        def save(self, *args, **kwargs):
            # Calculate 20% of the total for admin share
            admin_share_percentage = Decimal('0.20')
            self.admin_share_amount = self.price * admin_share_percentage

            # Call the original save method
            super().save(*args, **kwargs)
        def _str_(self) -> str:
              return f"{self.product.title} x {self.quantity}"


class Order (models.Model):
        STATUS = ('Recieved', 'On the way', 'Delivered')

        user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='orders', on_delete=models.CASCADE)
        order_items = models.ManyToManyField(OrderItem)
        first_name=models.CharField(max_length=100)
        last_name = models.CharField(max_length=100)
        email = models.EmailField(max_length=150)
        city = models.CharField(max_length=50)
        zip_code = models.CharField(max_length=10)
        address = models.TextField()
        total = models.DecimalField(max_digits=8, decimal_places=2)
        paid = models.BooleanField(default=True)
        transaction_id= models.UUIDField()
        paypal_transaction_id = models.CharField(max_length=50, null= True, blank=True)
        status = models.CharField(max_length=15, choices=list (zip (STATUS, STATUS)), default = 'Recieved')
        created_date = models.DateTimeField(auto_now_add=True)


        class Meta:
              ordering = ['-created_date']


        def str (self) -> str:
              return self.first_name + ' ' + self.last_name