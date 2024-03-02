from typing import Any
from django.db.models import Q
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, DetailView, ListView
from django.views import generic
from cart.carts import Cart
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.http import HttpResponse

from django.contrib import messages
from django.views import View
from django.urls import reverse_lazy

from .forms import ProductForm, CategoryForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import (
    PageNotAnInteger,
    EmptyPage,
    InvalidPage,
    Paginator
)
from .models import(
    Category,
    Product,
    Slider,
    FlashSales
)

from order.models import(
    Order
)
from user_account.models import SellerType
from decimal import Decimal, InvalidOperation
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




# #seller part begin
# @login_required
# def upload_product(request):

#     if request.method == 'POST':
#         form = ProductForm(request.POST)
#         if form.is_valid():
#             product = form.save(commit=False)
#             product.seller = request.user
#             product.save()
#             return redirect('/upload_product')  # Redirect to a view displaying the list of products
#     else:
#         form = ProductForm()

#     return render(request, 'seller/upload_product.html', {'form': form})

@login_required
def upload_product(request):
    user = request.user

    # Check if the seller type is limited
    try:
        seller_type = user.sellertype.seller_type
    except SellerType.DoesNotExist:
        seller_type = 'Unlimited'  # Assuming default is Unlimited if SellerType does not exist for the user

    # Check the number of products uploaded by the seller
    if seller_type == 'Limited':
        num_products_uploaded = Product.objects.filter(seller=user).count()
        if num_products_uploaded >= 2:
            message = "You have reached the maximum limit for product uploads!"
            return render(request, 'seller/upload_product.html', {'message': message})

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = user
            product.save()
            return redirect('/upload_product')  # Redirect to a view displaying the list of products
    else:
        form = ProductForm()

    return render(request, 'seller/upload_product.html', {'form': form})



@login_required
def sidebar(request):
    return render(request, 'sidebar.html')


class ProductsBySellerView(LoginRequiredMixin, ListView):
    model = Product
    template_name = "product-by-seller.html"
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.filter(seller=self.request.user)

class AddCategoryView(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "product/add-category.html"
    success_url = reverse_lazy('category-list')


class CategoryListView(ListView):
    model = Category
    template_name = "product/category-list.html"
    context_object_name = 'categories'


class ProductDeleteView(LoginRequiredMixin, View):
    model = Product
    success_url = reverse_lazy('product-by-seller')

    def post(self, request, pk):
        product = self.model.objects.get(pk=pk, seller=request.user)
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect(self.success_url)


#dashboard overview start

class AdminOverView(View):
    template_name = 'dashboard/admin-overview.html'

    def get(self, request, *args, **kwargs):
        user = request.user

        total_products = Product.objects.filter(seller=user).count()
        total_category = Category.objects.count()
        total_order = Order.objects.count()
        total_slider = Slider.objects.count()
        context = {'total_products': total_products,'total_category': total_category,'total_order': total_order,'total_slider': total_slider}
        return render(request, self.template_name, context)

from decimal import Decimal, InvalidOperation
from django.shortcuts import render
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
import json
from .models import Category, Product

from django.utils import timezone
from decimal import Decimal, InvalidOperation


def FlashSale():
    flash_sale_data = []
    current_time = timezone.now()
    # Get specific categories for the flash sale (replace [1, 2, 3] with the actual category IDs)
    # category_ids = [ 3]
    test = FlashSales.objects.all()
    # for test1 in test:
    #     categories = Category.objects.filter(id__in=test1.category.id)

    for category in test:
        print(category)
        products_in_category = Product.objects.filter(category=category.category.id)
        current_time = timezone.now()
        for product in products_in_category:
            try:
                # Start flash sale for 30 minutes with a 5x multiplier
                item_price = Decimal(str(product.price))  # Convert to Decimal
                discount_percentage = Decimal(str(category.discount))  # Convert to Decimal
                discounted_price = item_price * (1 - discount_percentage / 100)
                # Apply the discount to the item price
                # price = item.price /  flash_sale.discount
                price = discounted_price

                flash_sale_data.append({
                    'category': category.category.title,
                    'product_id': product.id,
                    'product_name': product.title,
                    'discount': category.discount,
                    'regular_price': item_price,
                    'updated_price': price,
                    'active_date':category.active_date,
                    'expiry_date': category.expiry_date,

                })

            except InvalidOperation as e:
                # Handle Decimal arithmetic errors
                print(f"Error updating price for product {product.id}: {e}")

    return flash_sale_data

# def FlashSale():
#     flash_sale_data = []
#     categories = Category.objects.all()

#     for category in categories:
#         print(category)
#         products_in_category = Product.objects.filter(category=category)

#         for product in products_in_category:
#             # print(product.price ,"-", product.price*55)
#              updated_price = product.price * Decimal('5')
#              product.price = updated_price
#              product.save()
#              flash_sale_data.append({
#                 'category': category.title,
#                 'product_id': product.id,
#                 'product_name': product.title,
#                 'original_price': product.price,
#                 'updated_price': updated_price,
#             })

#     return flash_sale_data

from django.shortcuts import render
 # Import your FlashSale function

# def flash_sale_view(request):
#     flash_sale_data = FlashSale()
#     return render(request, 'flash_sale_template.html', {'flash_sale_data': flash_sale_data})

from django.shortcuts import render
from .models import FlashSales
from datetime import date

def flash_sale_view(request):
    flash_sale_data = FlashSale()
    current_date = date.today()
    flash_sale_data_check = FlashSales.objects.filter(active=True, active_date__lte=current_date, expiry_date__gte=current_date).first()

    show_flash_sale_details = False
    if flash_sale_data_check:
        # If there is an active flash sale, set show_flash_sale_details to True
        show_flash_sale_details = True

    return render(request, 'flash_sale_template.html', {'flash_sale_data': flash_sale_data, 'show_flash_sale_details': show_flash_sale_details})
