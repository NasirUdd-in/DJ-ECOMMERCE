from django.conf import settings
from product.models import Product
from .models import Coupon
from product.models import FlashSales
from decimal import Decimal
class Cart(object):
    def __init__(self, request) -> None:
        self.session = request.session
        self.cart_id = settings.CART_ID
        self.coupon_id = settings.COUPOON_ID
        cart = self.session.get(self.cart_id)
        coupon = self.session.get(self.coupon_id)
        self.cart = self.session[self.cart_id] = cart if cart else {}
        self.coupon = self.session[self.coupon_id] = coupon if coupon else None



    def update(self, product_id, quantity=1):
        product = Product.objects.get(id=product_id)


        # Initialize price with a default value

        flash_sale_exists = FlashSales.objects.filter(category__id=product.category.id).exists()
        if  flash_sale_exists:
            # Get the flash sale for the current product's category
            flash_sale = FlashSales.objects.get(category__id=product.category.id)
        # Convert item.price to Decimal and then apply the discount
            item_price = Decimal(str(product.price))  # Convert to Decimal
            discount_percentage = Decimal(str(flash_sale.discount))  # Convert to Decimal

            discounted_price = item_price * (1 - discount_percentage / 100)
            # Apply the discount to the item price
            # price = item.price /  flash_sale.discount
            price = discounted_price
        else:
            price = item.price
        self.session[self.cart_id].setdefault(str(product_id), {"quantity": 0})
        updated_quantity = self.session[self.cart_id][str(product_id)]['quantity'] + quantity
        self.session[self.cart_id][str(product_id)]['quantity'] = updated_quantity
        self.session[self.cart_id][str(product_id)]['subtotal'] = updated_quantity * float(price)

        if updated_quantity < 1:
            del self.session[self.cart_id][str(product_id)]

        self.save()

    def add_coupon(self, coupon_id):
        self.session[self.coupon_id] = coupon_id
        self.save()
    def __iter__(self):
        products = Product.objects.filter(id__in=list(self.cart.keys()))
        cart = self.cart.copy()


        for item in products:
            product = Product.objects.get(id=item.id)
            # Initialize price with a default value
            price = item.price
            flash_sale_exists = FlashSales.objects.filter(category__id=item.category.id).exists()
            if  flash_sale_exists:
               # Get the flash sale for the current product's category
                flash_sale = FlashSales.objects.get(category__id=item.category.id)
            # Convert item.price to Decimal and then apply the discount
                item_price = Decimal(str(item.price))  # Convert to Decimal
                discount_percentage = Decimal(str(flash_sale.discount))  # Convert to Decimal

                discounted_price = item_price * (1 - discount_percentage / 100)
                # Apply the discount to the item price
                # price = item.price /  flash_sale.discount
                price = discounted_price
            cart[str(item.id)]['product'] = {
                "id": item.id,
                "title": item.title,
                "category": item.category.title,
                "price": float(price),
                "thumbnail": item.thumbnail,
                "slug": item.slug
            }

            yield cart[str(item.id)]


    def save(self):
        self.session.modified = True


    def __len__(self):
        return len(list(self.cart.keys()))


    def clear(self):
        try:
            del self.session[self.cart_id]
            del self.session[self.coupon_id]

        except:
            pass

        self.save()

    def restore_after_logout (self, cart={}):
        self.cart = self.session[self.cart_id] = cart
        self.save()

    def total(self):
        amount = sum(product['subtotal'] for product in self.cart.values())
        # if not self.coupon:
        #     amount += 5  # Add 5 to the total amount
        if self.coupon:
            coupon = Coupon.objects.get(id=self.coupon)
            amount -= amount * (coupon.discount / 100)
        return amount
    def test(self):
        return 5