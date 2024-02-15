from django.urls import path
from .views import(
    Home,
    ProductDetails,
    CategorytDetails,
    Productlist,
    SearchProducts,
    ProductsBySellerView,
    upload_product,
    sidebar,
    AddCategoryView,
    CategoryListView
)

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('product-details/<str:slug>/', ProductDetails.as_view(), name='product-details'),
    path('category-details/<str:slug>/', CategorytDetails.as_view(), name='category-details'),
    path('product-list/', Productlist.as_view(), name='product-list'),
    path('search-products/', SearchProducts.as_view(), name='search-products'),
    path('product-by-seller/', ProductsBySellerView.as_view(), name="product-by-seller"),
    path('upload_product/', upload_product, name="upload-product"),
    path('sidebar/', sidebar, name='sidebar'),
    
    path('add-category/', AddCategoryView.as_view(), name='add-category'),
    path('category-list/', CategoryListView.as_view(), name='category-list'),
]
