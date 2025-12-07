from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .models import CustomUser, File, FileCategoryMapping, Profile
from UserApp.utils import get_daily_passcode 
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from .utils import get_daily_passcode

User = get_user_model()  

class CustomUserCreationForm(UserCreationForm):
    passcode = forms.CharField(
        max_length=20,
        required=False,
        label="Passcode (required for Admin/Manager)",
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter today’s passcode if required'})
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role', 'passcode', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("Email is required.")
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        passcode = cleaned_data.get('passcode')

        if role in ['admin', 'manager']:
            if not passcode:
                raise forms.ValidationError("Passcode is required for admin/manager roles.")
            if passcode != get_daily_passcode():
                raise forms.ValidationError("Invalid passcode for the selected role.")
        return cleaned_data

class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'password')

class ForgotPasswordForm(forms.Form):
    username = forms.CharField(max_length=150, label="Username")
    new_password = forms.CharField(widget=forms.PasswordInput, label="New Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

class ProfileForm(forms.ModelForm):
    COUNTRY_CHOICES = [
        ('', 'Select Country'),
        ('India', 'India'),
        ('USA', 'USA'),
        ('UK', 'United Kingdom'),
        ('Canada', 'Canada'),
        ('Australia', 'Australia'),
    ]

    CITY_CHOICES = [
        ('', 'Select City'),
        ('Chennai', 'Chennai'),
        ('Mumbai', 'Mumbai'),
        ('Delhi', 'Delhi'),
        ('New York', 'New York'),
        ('London', 'London'),
        ('Toronto', 'Toronto'),
        ('Sydney', 'Sydney'),
        ('Madurai', 'Madurai')
    ]

    country = forms.ChoiceField(choices=COUNTRY_CHOICES, required=False)
    city = forms.ChoiceField(choices=CITY_CHOICES, required=False)

    class Meta:
        model = Profile
        fields = [
            'firstname', 'lastname', 'dob', 'email', 'phone',
            'country', 'city', 'postalcode', 'profile_image'
        ]
        widgets = {
            'firstname': forms.TextInput(attrs={'class': 'form-control'}),
            'lastname': forms.TextInput(attrs={'class': 'form-control'}),
            'dob': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'postalcode': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.Select(attrs={'class': 'form-select'}),
            'city': forms.Select(attrs={'class': 'form-select'}),
            'profile_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['title', 'description', 'file']

class FileCategoryMappingForm(forms.ModelForm):
    assign_to = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(role='employee'),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False,
        label="Assign To"
    )

    class Meta:
        model = FileCategoryMapping
        fields = ['file', 'category', 'assign_to']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].empty_label = "Select a file"
        self.fields['category'].empty_label = "Select a category"
        self.fields['assign_to'].empty_label = "Select an employee"
