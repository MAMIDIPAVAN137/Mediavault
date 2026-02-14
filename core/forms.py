from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import uuid

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, label="First Name")
    last_name = forms.CharField(max_length=30, label="Last Name")
    email = forms.EmailField(required=True, label="Email Address")
    phone_number = forms.CharField(max_length=20, required=True, label="Phone Number")
    gender = forms.ChoiceField(choices=User.GENDER_CHOICES, label="Gender", widget=forms.Select(attrs={'class': 'v-auth-input'}))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'gender')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'password1' in self.fields:
            self.fields['password1'].label = "Password"
            self.fields['password1'].help_text = ""
        if 'password2' in self.fields:
            self.fields['password2'].label = "Confirm Password"
            self.fields['password2'].help_text = ""
        for field_name, field in self.fields.items():
            label_text = field.label if field.label else field_name.replace('_', ' ').capitalize()
            field.widget.attrs.update({
                'class': 'v-auth-input',
                'placeholder': label_text
            })
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data.get('email').split('@')[0] + '-' + str(uuid.uuid4())[:8] # Ensure unique username
        if commit:
            user.save()
        return user

class EmailOrPhoneAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label="Email or Phone", widget=forms.TextInput(attrs={
        'autofocus': True, 
        'placeholder': 'Email or Phone',
        'class': 'v-auth-input'
    }))
    password = forms.CharField(label="Password", strip=False, widget=forms.PasswordInput(attrs={
        'autocomplete': 'current-password',
        'placeholder': 'Password',
        'class': 'v-auth-input'
    }))
    
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)
        self.fields['username'].label = "Email or Phone"
        self.fields['password'].label = "Password"

class ProfileUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and not user.is_superuser:
            self.fields['email'].disabled = True
            self.fields['phone_number'].disabled = True
            self.fields['email'].help_text = "Only admins can change this contact info."
            self.fields['phone_number'].help_text = "Only admins can change this contact info."
            
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'gender', 'profile_picture', 'bio', 'download_preference', 'theme_preference']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'v-auth-input'}),
            'last_name': forms.TextInput(attrs={'class': 'v-auth-input'}),
            'email': forms.EmailInput(attrs={'class': 'v-auth-input'}),
            'phone_number': forms.TextInput(attrs={'class': 'v-auth-input'}),
            'gender': forms.Select(attrs={'class': 'v-auth-input'}),
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'v-auth-input'}),
            'bio': forms.Textarea(attrs={'class': 'v-auth-input', 'rows': 3}),
            'download_preference': forms.Select(attrs={'class': 'v-auth-input'}),
            'theme_preference': forms.Select(attrs={'class': 'v-auth-input'}),
        }

class AdminUserUpdateForm(forms.ModelForm):
    new_password = forms.CharField(
        required=False, 
        widget=forms.PasswordInput(attrs={'class': 'v-auth-input', 'placeholder': 'Enter new password to reset'}),
        label="Reset Password"
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'gender', 'is_uploader', 'download_preference', 'theme_preference']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'v-auth-input'}),
            'last_name': forms.TextInput(attrs={'class': 'v-auth-input'}),
            'email': forms.EmailInput(attrs={'class': 'v-auth-input'}),
            'phone_number': forms.TextInput(attrs={'class': 'v-auth-input'}),
            'gender': forms.Select(attrs={'class': 'v-auth-input'}),
            'download_preference': forms.Select(attrs={'class': 'v-auth-input'}),
            'theme_preference': forms.Select(attrs={'class': 'v-auth-input'}),
        }
        help_texts = {
            'is_uploader': "Designates whether the user can upload files and create folders.",
        }

from .models import UploadRequest, ReportedProblem

class UsernameUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'v-auth-input', 'placeholder': 'New username'}),
        }
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise ValidationError("This username is already taken.")
        return username

class UploadRequestForm(forms.ModelForm):
    class Meta:
        model = UploadRequest
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'fluent-input', 
                'rows': 4,
                'placeholder': 'Please explain why you want to become an uploader...'
            }),
        }

class ReportProblemForm(forms.ModelForm):
    class Meta:
        model = ReportedProblem
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'v-auth-input',
                'rows': 4,
                'placeholder': 'Describe the problem you are facing...'
            }),
        }
