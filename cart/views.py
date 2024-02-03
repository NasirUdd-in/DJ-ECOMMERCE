from django.shortcuts import get_object_or_404, redirect
from django.views import generic
from .carts import Cart
from product.models import Product

# Create your views here.

class AddToCart(generic.View):
    def post(self, *args, **kwargs):
        product = get_object_or_404(Product, id=kwargs.get('product_id'))
        cart = Cart(self.request)
        cart.update(product.id, 1)
        # return redirect('product-details', slug=product.slug)
        return redirect('cart')


class CartItems(generic.TemplateView):
    template_name = 'cart/cart.html'