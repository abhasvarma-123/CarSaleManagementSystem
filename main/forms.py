from django import forms
from .models import Company, Car, Part, TestDrive, LoanApplication, CompanyRequest

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'country', 'description', 'logo', 'established_year']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'established_year': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['model', 'year', 'price', 'color', 'fuel_type', 'mileage', 'description', 'image', 'status']
        widgets = {
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
            'fuel_type': forms.Select(attrs={'class': 'form-control'}),
            'mileage': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

class PartForm(forms.ModelForm):
    class Meta:
        model = Part
        fields = ['name', 'category', 'price', 'stock', 'description', 'image', 'compatible_cars']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'compatible_cars': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

class TestDriveForm(forms.ModelForm):
    class Meta:
        model = TestDrive
        fields = ['date', 'time', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class LoanApplicationForm(forms.ModelForm):
    class Meta:
        model = LoanApplication
        fields = ['amount', 'duration_months', 'monthly_income', 'employment_status']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'duration_months': forms.NumberInput(attrs={'class': 'form-control'}),
            'monthly_income': forms.NumberInput(attrs={'class': 'form-control'}),
            'employment_status': forms.TextInput(attrs={'class': 'form-control'}),
        }
        # Add at the end of the file

class CompanyRequestForm(forms.ModelForm):
    class Meta:
        model = CompanyRequest
        fields = ['company_name', 'country', 'description', 'established_year', 
                  'contact_email', 'contact_phone', 'requested_username', 'requested_password']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Toyota Motors'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Japan'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Tell us about your company...'}),
            'established_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 1937'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'company@example.com'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 234 567 8900'}),
            'requested_username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a username'}),
            'requested_password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Choose a password'}),
        }