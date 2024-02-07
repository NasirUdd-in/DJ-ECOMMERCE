import json
import uuid
from django. views import generic
from django.urls import reverse_lazy
from django.http import JsonResponse
from django. shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CheckoutForm
from cart.carts import Cart
from .models import OrderItem, Order, Product
from product.models import Product


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import OrderItem

from django.db.models import Sum
from .forms import DateRangeForm

class Checkout (LoginRequiredMixin, generic.View):
     login_url = reverse_lazy('login')
     def get(self, *args, **kwargs):
        form = CheckoutForm()
        context = {
            'form': form
        }
        return render(self.request, 'order/checkout.html', context)
     
     def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST)
        
        if form.is_valid():
            data = form.cleaned_data
            print(data)
            return JsonResponse({
                'success': True,
                "errors": None
                                    
            })
        else:
            return JsonResponse({
                'success': False,
                "errors": dict(form.errors)
            })
            

class SaveOrder (LoginRequiredMixin, generic.View):
    login_url = reverse_lazy('login')
    def post (self, *args, **kwargs):
        customer_information =json.loads(self.request.body)
        cart = Cart(self.request)
        user_cart = Cart(self.request).cart
        products = Product.objects.filter(id__in=list(user_cart.keys()))
        ordered_products =[]
        for product in products:
            order_item = OrderItem.objects.create(
                product=product,
                price=product.price,
                quantity=user_cart[str(product.id)]['quantity']
            )
            ordered_products.append(order_item)
            
        order = Order.objects.create(
            user = self.request.user,
            transaction_id=uuid.uuid4().hex,
            **customer_information
        )
        
        order.order_items.add(*ordered_products)
        
        #security puerpose
        if float('%.2f' % cart.total()) != float(order.total):
            order.paid = False
            order.save()
         
        cart.clear()
        return JsonResponse({'success': True})
    
    
class Orders(LoginRequiredMixin, generic.ListView):
        login_url = reverse_lazy( 'login')
        model = Order
        template_name = 'order/orders.html'
        context_object_name = 'orders'
        
        def get_queryset(self):
            return Order.objects.filter(user=self.request.user)


#seller dashboard

# @login_required
# def seller_dashboard(request):
#     if request.user.is_staff:
#         # If the user is an admin, show all sold products
#         seller_orders = OrderItem.objects.all()
#     else:
#         # If the user is a normal user, show only their sold products
#         seller_orders = OrderItem.objects.filter(product__seller=request.user)
#     total_price = seller_orders.aggregate(Sum('price'))['price__sum'] or 0
    
#     return render(request, 'seller/seller_dashboard.html', {'seller_orders': seller_orders, 'total_price': total_price})

# views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .forms import DateRangeForm
from .models import OrderItem, Product

@login_required
def seller_dashboard(request):
    date_range_form = DateRangeForm(request.GET)
    
    if request.user.is_staff:
        # If the user is an admin, show all sold products
        seller_orders = OrderItem.objects.all()
    else:
        # If the user is a normal user, show only their sold products
        seller_orders = OrderItem.objects.filter(product__seller=request.user)

    # Handle date range filtering
    if date_range_form.is_valid():
        start_date = date_range_form.cleaned_data['start_date']
        end_date = date_range_form.cleaned_data['end_date']
        if start_date:
            seller_orders = seller_orders.filter(order__created_date__gte=start_date)
        if end_date:
            seller_orders = seller_orders.filter(order__created_date__lte=end_date)

    # Calculate the total price of all sold products
    total_price = seller_orders.aggregate(Sum('price'))['price__sum'] or 0

    return render(request, 'seller/seller_dashboard.html', {'seller_orders': seller_orders, 'total_price': total_price, 'date_range_form': date_range_form})
