from django.db.models import Q
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, DetailView
from django.views import generic
from cart.carts import Cart
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .forms import ProductForm
from django.core.paginator import (
    PageNotAnInteger,
    EmptyPage,
    InvalidPage,
    Paginator

)
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
    
    

class CategorytDetails(generic.DetailView):
    model = Category
    template_name = 'product/category-details.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = self.get_object().products.all() 
        return context
class CustomPaginator:
    def __init__(self, request, queryset, paginated_by) -> None:
        self.paginator = Paginator(queryset, paginated_by)
        self.paginated_by = paginated_by
        self.queryset = queryset
        self.page = request.GET.get('page', 1)

    def get_queryset(self):
        try:
            queryset = self.paginator.page(self.page)
        except PageNotAnInteger:
            queryset = self.paginator.page(1)
        except EmptyPage:
            queryset = self.paginator.page(1)
        except InvalidPage:
            queryset = self.paginator.page(1)
        return queryset



class Productlist(generic.ListView):
    model = Product
    template_name = 'product/product-list.html'
    context_object_name = 'object_list'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_obj = CustomPaginator(self.request, self.get_queryset(), self.paginate_by)
        queryset = page_obj.get_queryset()
        paginator = page_obj.paginator
        context['object_list'] = queryset
        context['paginator'] = paginator
        return context

class SearchProducts(generic.View):
    def get(self, *args, **kwargs):
        key = self.request.GET.get('key', '')
        products = Product.objects.filter(
            Q(title__icontains=key) |
            Q(category__title__icontains=key)
        )
        context = {
            'products': products,
            "key": key
        }
        return render(self.request, 'product/search-products.html', context)
        
        


#seller part begin
@login_required
def upload_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            return redirect('upload_product')  # Redirect to a view displaying the list of products
    else:
        form = ProductForm()

    return render(request, 'seller/upload_product.html', {'form': form})


@login_required
def sidebar(request):
    return render(request, 'sidebar.html')