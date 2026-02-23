from django.contrib import admin
from .models import (Car, Part, TestDrive, LoanApplication, Cart, CartItem, 
                     Company, CompanyRequest, CarPurchase, PartOrder, PartOrderItem)

@admin.register(CompanyRequest)
class CompanyRequestAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'country', 'requested_username', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['company_name', 'requested_username', 'contact_email']

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'established_year', 'created_at']
    search_fields = ['name', 'country']

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ['company', 'model', 'year', 'price', 'status', 'created_at']
    list_filter = ['status', 'fuel_type', 'company']
    search_fields = ['model', 'company__name']

@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'category', 'price', 'stock']
    list_filter = ['company', 'category']
    search_fields = ['name', 'category']

@admin.register(TestDrive)
class TestDriveAdmin(admin.ModelAdmin):
    list_display = ['user', 'car', 'date', 'time', 'status']
    list_filter = ['status', 'date']

@admin.register(LoanApplication)
class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = ['user', 'car', 'amount', 'status', 'is_editable', 'created_at']
    list_filter = ['status', 'is_editable']

@admin.register(CarPurchase)
class CarPurchaseAdmin(admin.ModelAdmin):
    list_display = ['user', 'car', 'total_price', 'payment_method', 'status', 'purchase_date']
    list_filter = ['status', 'payment_method']

@admin.register(PartOrder)
class PartOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_amount', 'payment_method', 'status', 'order_date']
    list_filter = ['status', 'payment_method']

@admin.register(PartOrderItem)
class PartOrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'part', 'quantity', 'price']

admin.site.register(Cart)
admin.site.register(CartItem)