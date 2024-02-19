from django import forms
from .models import Order
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class CheckoutForm(forms.Form):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField(max_length=150)
    city = forms.CharField(max_length=50)
    zip_code = forms.CharField(max_length=10)
    address = forms.CharField(widget=forms.Textarea)


class DateRangeForm(forms.Form):
    start_date = forms.DateField(label='Start Date', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(label='End Date', required=False, widget=forms.DateInput(attrs={'type': 'date'}))


class OrderStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']
        labels = {'status': ''}

    def __init__(self, *args, **kwargs):
        super(OrderStatusUpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
