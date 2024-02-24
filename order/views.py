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

from django.views.generic import ListView,View
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import OrderItem

from django.db.models import Sum
from .forms import DateRangeForm

from .models import Order
from .forms import OrderStatusUpdateForm


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

from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import os

# @login_required
# def seller_dashboard(request):
#     date_range_form = DateRangeForm(request.GET)

#     if request.user.is_superuser:
#         # If the user is an admin, show all sold products

#         seller_orders = OrderItem.objects.all()
#     elif request.user.is_staff and request.user.is_active:
#         # If the user is an seller, show all sold products
#         orders = Order.objects.filter(user=request.user)
#         seller_orders = OrderItem.objects.none()  # Initialize as an empty queryset
#         for order in orders:
#             seller_orders |= order.order_items.all()

#     # Handle date range filtering
#     if date_range_form.is_valid():
#         start_date = date_range_form.cleaned_data['start_date']
#         end_date = date_range_form.cleaned_data['end_date']
#         if start_date:
#             seller_orders = seller_orders.filter(order__created_date__gte=start_date)
#         if end_date:
#             seller_orders = seller_orders.filter(order__created_date__lte=end_date)

#     # Calculate the total price of all sold products
#     if request.user.is_staff and request.user.is_active:
#         sum = 0
#         for orders in seller_orders:
#             sum = sum + orders.price
#         total_price = sum
#     else:
#         total_price = seller_orders.aggregate(Sum('price'))['price__sum'] or 0

#     return render(request, 'seller/seller_dashboard.html', {'seller_orders': seller_orders, 'total_price': total_price, 'date_range_form': date_range_form})


from functools import wraps

def seller_dashboard(view_func):
    print("hello bangladesh: ")
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        date_range_form = DateRangeForm(request.GET)

        if request.user.is_superuser:
            # If the user is an admin, show all sold products
            seller_orders = OrderItem.objects.all()
        elif request.user.is_staff and request.user.is_active:
            # If the user is a seller, show all sold products
            orders = Order.objects.filter(user=request.user)
            seller_orders = OrderItem.objects.none()  # Initialize as an empty queryset
            for order in orders:
                seller_orders |= order.order_items.all()

        # Handle date range filtering
        if date_range_form.is_valid():
            start_date = date_range_form.cleaned_data['start_date']
            end_date = date_range_form.cleaned_data['end_date']
            if start_date:
                seller_orders = seller_orders.filter(order__created_date__gte=start_date)
            if end_date:
                seller_orders = seller_orders.filter(order__created_date__lte=end_date)

        # Calculate the total price of all sold products
        if request.user.is_staff and request.user.is_active:
            total_price = sum(order.price for order in seller_orders)
        else:
            total_price = seller_orders.aggregate(Sum('price'))['price__sum'] or 0

        return view_func(request, seller_orders=seller_orders, total_price=total_price, date_range_form=date_range_form, *args, **kwargs)

    return _wrapped_view

# Apply the decorator to your view
@seller_dashboard
def seller_dashboard_one(request, seller_orders=None, total_price=None, date_range_form=None):
    # Your view logic here, you can use seller_orders, total_price, and date_range_form
    print("seller_orders")
    return render(request, 'seller/seller_dashboard.html', {'seller_orders': seller_orders, 'total_price': total_price, 'date_range_form': date_range_form})

class OrderListView(ListView):
    model = Order
    template_name = 'admin-order-list.html'
    context_object_name = 'orders'
    ordering = ['created_date']


class OrderListView(ListView):
    model = Order
    template_name = 'admin-order-list.html'
    context_object_name = 'orders'
    ordering = ['-created_date']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_update_form'] = OrderStatusUpdateForm()
        return context

    def post(self, request, *args, **kwargs):
        order_id = request.POST.get('order_id')
        order = Order.objects.get(id=order_id)
        form = OrderStatusUpdateForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
        return redirect('order_list')  # Update this with your actual URL name

def generate_to_pdf(template_src,context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")),result)
    if not pdf.err:
        return HttpResponse(result.getvalue(),content_type="application/pdf")
    else:
     return None



class GenerateInvoice(View):
    def get(self,request,*args,**kwargs):

        if request.user.is_superuser:
        # If the user is an admin, show all sold products

            seller_orders = OrderItem.objects.all()
        elif request.user.is_staff and request.user.is_active:
        # If the user is an seller, show all sold products of the specific seller
            orders = Order.objects.filter(user=request.user)
            seller_orders = OrderItem.objects.none()  # Initialize as an empty queryset
            for order in orders:
                seller_orders |= order.order_items.all()

        price = 0
        for i in seller_orders:
            price = price+i.price
        quantity = 0
        for i in seller_orders:
            quantity = quantity+i.quantity
        data = {
            "name" : request.user.username,
            "email" : request.user.email,
            "order" : seller_orders,
            "price" : price,
            "quantity" : quantity,
        }
        pdf = generate_to_pdf("seller/pdf.html",data)
        if pdf:
            return pdf
        return HttpResponse("Unauthorized",status=401)