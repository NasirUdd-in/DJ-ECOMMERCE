import copy
from django.views import generic
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from django.views.generic import ListView, CreateView
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetConfirmView
)

from .forms import (
    LoginForm,
    UserRegistrationForm,
    ChangePasswordForm,
    SendEmailForm,
    ResetPasswordConfirmForm,
    SellerTypeForm
)
from .mixins import (
    LogoutRequiredMixin
)

from cart.carts import Cart
from .models import User,SellerType


from django.views import View
from .forms import UserCreationFormExtended

@method_decorator(never_cache, name='dispatch')
class Login(LogoutRequiredMixin, generic.View):
    def get(self, *args, **kwargs):
        form = LoginForm()
        context = {
            "form": form
        }
        return render(self.request, 'account/login.html', context)

    def post(self, *args, **kwargs):
        form = LoginForm(self.request.POST)

        if form.is_valid():
            user = authenticate(
                self.request,
                username=form.cleaned_data.get('username'),
                password=form.cleaned_data.get('password')
            )

            if user:
                login(self.request, user)
                if user.is_staff:
                    return redirect('admin_over_view')
                else:
                    return redirect('home')

            else:
                messages.warning(self.request, "Wrong credentials")
                return redirect('login')

        return render(self.request, 'account/login.html', {"form": form})


class Logout(generic.View):
    def get(self, *args, **kwargs):
        cart = Cart(self.request)
        current_cart = copy.deepcopy(cart.cart)
        logout(self.request)
        cart.restore_after_logout (current_cart)
        return redirect('login')


@method_decorator(never_cache, name='dispatch')
class Registration(LogoutRequiredMixin, generic.CreateView):
    template_name = 'account/registration.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        messages.success(self.request, "Registration Successfull !")
        return super().form_valid(form)


@method_decorator(never_cache, name='dispatch')
class ChangePassword(LoginRequiredMixin, generic.FormView):
    template_name = 'account/change_password.html'
    form_class = ChangePasswordForm
    login_url = reverse_lazy('login')
    success_url = reverse_lazy('login')

    def get_form_kwargs(self):
        context = super().get_form_kwargs()
        context['user'] = self.request.user
        return context

    def form_valid(self, form):
        user = self.request.user
        user.set_password(form.cleaned_data.get('new_password1'))
        user.save()
        messages.success(self.request, "Password changed Successfully !")
        return super().form_valid(form)


class SendEmailToResetPassword(PasswordResetView):
    template_name = 'account/password_reset.html'
    form_class = SendEmailForm


class ResetPasswordConfirm(PasswordResetConfirmView):
    template_name = 'account/password_reset_confirm.html'
    form_class = ResetPasswordConfirmForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        messages.success(self.request, "Password reset successfully !")
        return super().form_valid(form)



#registraion for merchant
@method_decorator(never_cache, name='dispatch')
class SellerRegistrationView(generic.CreateView):
    template_name = 'account/registration.html'  # Assuming the same template is used
    form_class = UserRegistrationForm  # Use the same form for both customers and sellers
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        # Set is_staff to True for seller registration
        form.instance.is_staff = True
        messages.success(self.request, "Seller registration successful!")
        return super().form_valid(form)

# class SellerListView(ListView):
#     model = User
#     template_name = 'seller/seller_list.html'
#     context_object_name = 'seller_list'

#     def get_queryset(self):
#         return User.objects.filter(is_staff=True, is_superuser=False)

class SellerListView(ListView):
    model = SellerType
    template_name = 'seller/seller_list.html'
    context_object_name = 'seller_types'


class CustomerListView(ListView):
    model = User
    template_name = 'customer/customer_list.html'
    context_object_name = 'customer_list'

    def get_queryset(self):
        return User.objects.filter(is_staff=False, is_superuser=False)


class AddSellerTypeView(CreateView):
    model = SellerType
    form_class = SellerTypeForm
    template_name = "seller/add-seller.html"
    success_url = reverse_lazy('staff_users_list')

    def form_valid(self, form):
        # Set is_active to True for the related User instance
        form.instance.seller.is_active = True

        # Save both SellerType and User instances to the database
        response = super().form_valid(form)
        form.instance.seller.save()

        return response


class AddUserView(View):
    template_name = 'add-user.html'

    def get(self, request, *args, **kwargs):
        form = UserCreationFormExtended()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = UserCreationFormExtended(request.POST)
        if form.is_valid():
            user = form.save()
            # You can perform additional actions here if needed
            return redirect('dashboard')  # Redirect to your dashboard page
        return render(request, self.template_name, {'form': form})