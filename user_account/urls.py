from django.urls import path
from django.contrib.auth.views import (
    PasswordResetDoneView,
    PasswordResetCompleteView
)

from .views import (
    Login,
    Logout,
    Registration,
    ChangePassword,
    SendEmailToResetPassword,
    ResetPasswordConfirm,
    SellerRegistrationView,
    SellerListView,
    CustomerListView,
    AddSellerTypeView
)


urlpatterns = [
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('registration/', Registration.as_view(), name='registration'),
    path('change-password/', ChangePassword.as_view(), name='change_password'),
    path('password-reset/', SendEmailToResetPassword.as_view(), name='password_reset'),
    path('password-reset/done/', PasswordResetDoneView.as_view(template_name='account/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', ResetPasswordConfirm.as_view(), name='password_reset_confirm'),

    path('seller-registration/', SellerRegistrationView.as_view(), name='seller-registration'),
    path('seller-list/', SellerListView.as_view(), name='staff_users_list'),
    path('customer-list/', CustomerListView.as_view(), name='customer_list'),

    path('add-seller/', AddSellerTypeView.as_view(), name='add_seller'),


]