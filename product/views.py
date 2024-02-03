from django.shortcuts import render
from django.views.generic import TemplateView, DetailView
from cart.carts import Cart
from .models import(
    Category,
    Product,
    Slider
)
# Create your views here.
class Home(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'featured_categories': Category.objects.filter(featured=True),
                'featured_products': Product.objects.filter(featured=True),
                'sliders': Slider.objects.filter(show=True)
            }
        )
        return context
        
class ProductDetails(DetailView):
    model = Product
    template_name = 'product/product-details.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Access the current product instance using self.object
        current_product = self.object
        # Assuming you have a related field named 'related' in your Product model
        context['related_products'] = current_product.related.all()
        return context