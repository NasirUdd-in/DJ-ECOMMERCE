from django.urls import path
from .views import(
    Home,
    ProductDetails,
    CategorytDetails,
    Productlist,
    SearchProducts,
    upload_product,
    sidebar
)

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('product-details/<str:slug>/', ProductDetails.as_view(), name='product-details'),
    path('category-details/<str:slug>/', CategorytDetails.as_view(), name='category-details'),
    path('product-list/', Productlist.as_view(), name='product-list'),
    path('search-products/', SearchProducts.as_view(), name='search-products'),
    path('upload_product/', upload_product, name='upload_product'),
     path('sidebar/', sidebar, name='sidebar'),
]
