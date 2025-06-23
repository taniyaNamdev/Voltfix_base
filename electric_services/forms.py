from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile, ElectricProduct, ProductReview

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            UserProfile.objects.create(user=user)
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
    class Meta:
        model = UserProfile
        fields = [
            'profile_picture', 'phone_number', 'address_line_1', 
            'address_line_2', 'city', 'state_province_region', 
            'postal_code', 'country'
        ]

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