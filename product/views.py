from django.shortcuts import render
from django.views.generic import TemplateView
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
        
class ProductDetails(TemplateView):
    template_name = 'product/product-details.html'