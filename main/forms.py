from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Car, Order

class RegisterForm(UserCreationForm):
    first_name = forms.CharField(label="Имя", max_length=30)
    last_name = forms.CharField(label="Фамилия", max_length=30)
    middle_name = forms.CharField(label="Отчество", max_length=30, required=False)
    phone = forms.CharField(label="Номер телефона", max_length=20)
    email = forms.EmailField(label="Почта")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'middle_name', 'phone', 'email', 'password1', 'password2']

class PhoneAuthForm(AuthenticationForm):
    username = forms.CharField(label="Номер телефона")

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'middle_name', 'phone', 'address', 'email', 'is_active']

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = '__all__'

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['user', 'status', 'address']
