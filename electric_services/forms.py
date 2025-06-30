from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile, ElectricProduct, ProductReview, QuoteRequest, ServiceBooking
from django.utils import timezone
from datetime import date, timedelta
import re

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone_number = forms.CharField(max_length=20, required=True, help_text="Enter your phone number")
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone_number', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address is already registered.')
        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone:
            # Clean phone number (remove spaces, dashes, etc.)
            cleaned_phone = re.sub(r'[\s\-\(\)]', '', phone)
            if len(cleaned_phone) < 10:
                raise forms.ValidationError('Phone number must be at least 10 digits.')
            
            # Check if phone number already exists
            if UserProfile.objects.filter(phone_number=phone).exists():
                raise forms.ValidationError('This phone number is already registered.')
        return phone

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            UserProfile.objects.create(user=user, phone_number=self.cleaned_data['phone_number'])
        return user

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label='Email')
    
    def clean_username(self):
        email = self.cleaned_data.get('username')
        try:
            user = User.objects.get(email=email)
            return user.username
        except User.DoesNotExist:
            raise forms.ValidationError('No account found with this email address.')

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class ProfileUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'profile_picture', 'phone_number', 'address_line_1', 
            'address_line_2', 'city', 'state_province_region', 
            'postal_code', 'country'
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['email'].initial = self.user.email

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if self.user and User.objects.filter(email=email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError('This email address is already registered.')
        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone:
            # Clean phone number (remove spaces, dashes, etc.)
            cleaned_phone = re.sub(r'[\s\-\(\)]', '', phone)
            if len(cleaned_phone) < 10:
                raise forms.ValidationError('Phone number must be at least 10 digits.')
            
            # Check if phone number already exists (excluding current user's profile)
            if self.instance and self.instance.pk:
                if UserProfile.objects.filter(phone_number=phone).exclude(pk=self.instance.pk).exists():
                    raise forms.ValidationError('This phone number is already registered.')
            else:
                if UserProfile.objects.filter(phone_number=phone).exists():
                    raise forms.ValidationError('This phone number is already registered.')
        return phone

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            # Update user email if changed
            if self.user and self.cleaned_data.get('email') != self.user.email:
                self.user.email = self.cleaned_data['email']
                self.user.save()
            profile.save()
        return profile

class ProductSearchForm(forms.Form):
    search = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search products...'})
    )
    category = forms.ChoiceField(
        choices=[('', 'All Categories')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    min_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Min Price'})
    )
    max_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max Price'})
    )
    condition = forms.ChoiceField(
        choices=[('', 'All Conditions'), ('new', 'New'), ('used', 'Used'), ('refurbished', 'Refurbished')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import ServiceCategory
        categories = ServiceCategory.objects.all()
        self.fields['category'].choices = [('', 'All Categories')] + [(cat.id, cat.name) for cat in categories]

class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, i) for i in range(1, 6)], attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Write your review...'}),
        }

class QuoteRequestForm(forms.ModelForm):
    class Meta:
        model = QuoteRequest
        fields = ['name', 'email', 'phone', 'service_type', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email address'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your phone number (optional)'
            }),
            'service_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe your electrical needs...'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial choices for service type
        self.fields['service_type'].choices = [
            ('', 'Select a service'),
            ('electrical-repair', 'Electrical Repair'),
            ('installation', 'New Installation'),
            ('maintenance', 'Maintenance'),
            ('emergency', 'Emergency Service'),
            ('smart-home', 'Smart Home Setup'),
            ('inspection', 'Inspection & Testing'),
            ('other', 'Other'),
        ]

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Clean phone number (remove spaces, dashes, etc.)
            cleaned_phone = re.sub(r'[\s\-\(\)]', '', phone)
            if len(cleaned_phone) < 10:
                raise forms.ValidationError('Please enter a valid phone number (at least 10 digits).')
        return phone

class ServiceBookingForm(forms.ModelForm):
    class Meta:
        model = ServiceBooking
        fields = [
            'address_line_1', 'address_line_2', 'city', 'state_province', 'postal_code', 'country',
            'contact_phone', 'contact_email', 'alternate_phone',
            'preferred_date', 'preferred_time_slot', 'property_type',
            'service_description', 'special_requirements', 'payment_method'
        ]
        widgets = {
            'address_line_1': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Street Address'
            }),
            'address_line_2': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apartment, suite, etc. (optional)'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'state_province': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State/Province'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ZIP/Postal Code'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Country'
            }),
            'contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Primary Phone Number'
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Address'
            }),
            'alternate_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Alternate Phone (optional)'
            }),
            'preferred_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': date.today().isoformat()
            }),
            'preferred_time_slot': forms.Select(attrs={
                'class': 'form-select'
            }),
            'property_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'service_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Please describe the service you need in detail...'
            }),
            'special_requirements': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any special requirements, access instructions, or additional notes...'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set minimum date to today
        self.fields['preferred_date'].widget.attrs['min'] = date.today().isoformat()
        
        # Set choices for select fields
        self.fields['preferred_time_slot'].choices = [
            ('', 'Select time slot'),
            ('morning', 'Morning (8 AM - 12 PM)'),
            ('afternoon', 'Afternoon (12 PM - 4 PM)'),
            ('evening', 'Evening (4 PM - 8 PM)'),
            ('flexible', 'Flexible'),
        ]
        
        self.fields['property_type'].choices = [
            ('', 'Select property type'),
            ('residential', 'Residential'),
            ('commercial', 'Commercial'),
            ('industrial', 'Industrial'),
            ('other', 'Other'),
        ]
        
        self.fields['payment_method'].choices = [
            ('', 'Select payment method'),
            ('cash', 'Cash'),
            ('card', 'Credit/Debit Card'),
            ('bank_transfer', 'Bank Transfer'),
            ('online_payment', 'Online Payment'),
            ('check', 'Check'),
        ]
        
        # Pre-fill contact information if user has profile
        if self.user and self.user.is_authenticated:
            try:
                profile = self.user.profile
                if profile:
                    self.fields['contact_phone'].initial = profile.phone_number
                    self.fields['contact_email'].initial = self.user.email
                    if profile.address_line_1:
                        self.fields['address_line_1'].initial = profile.address_line_1
                    if profile.address_line_2:
                        self.fields['address_line_2'].initial = profile.address_line_2
                    if profile.city:
                        self.fields['city'].initial = profile.city
                    if profile.state_province_region:
                        self.fields['state_province'].initial = profile.state_province_region
                    if profile.postal_code:
                        self.fields['postal_code'].initial = profile.postal_code
                    if profile.country:
                        self.fields['country'].initial = profile.country
            except UserProfile.DoesNotExist:
                pass
    
    def clean_preferred_date(self):
        preferred_date = self.cleaned_data.get('preferred_date')
        if preferred_date and preferred_date < date.today():
            raise forms.ValidationError("Preferred date cannot be in the past.")
        return preferred_date
    
    def clean_contact_phone(self):
        phone = self.cleaned_data.get('contact_phone')
        if phone:
            # Clean phone number (remove spaces, dashes, etc.)
            cleaned_phone = re.sub(r'[\s\-\(\)]', '', phone)
            if len(cleaned_phone) < 10:
                raise forms.ValidationError("Please enter a valid phone number (at least 10 digits).")
        return phone

    def clean_alternate_phone(self):
        phone = self.cleaned_data.get('alternate_phone')
        if phone:
            # Clean phone number (remove spaces, dashes, etc.)
            cleaned_phone = re.sub(r'[\s\-\(\)]', '', phone)
            if len(cleaned_phone) < 10:
                raise forms.ValidationError("Please enter a valid alternate phone number (at least 10 digits).")
        return phone 