from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Order

class CustomRegisterForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border rounded',
            'placeholder': 'Username'
        })
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 border rounded',
            'placeholder': 'Password'
        })
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 border rounded',
            'placeholder': 'Confirm Password'
        })
    )

    email = forms.EmailField(
    widget=forms.EmailInput(attrs={
        'class': 'w-full px-3 py-2 border rounded',
        'placeholder': 'Email'
    })
)


    class Meta:
        model = User
        fields = ['username', 'email','password1', 'password2']

class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'w-full px-3 py-2 border rounded'})
        self.fields['password'].widget.attrs.update({'class': 'w-full px-3 py-2 border rounded'})



class OrderAddressForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['address', 'zip_code', 'phone']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }