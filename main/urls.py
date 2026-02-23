from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    # Public
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('company/register-request/', views.company_register_request, name='company_register_request'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('cars/', views.car_list, name='car_list'),
    path('cars/<int:pk>/', views.car_detail, name='car_detail'),
    path('parts/', views.part_list, name='part_list'),

    # User
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:part_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/checkout/', views.checkout_parts, name='checkout_parts'),
    path('my-part-orders/', views.my_part_orders, name='my_part_orders'),
    path('cars/<int:car_id>/buy/', views.buy_car, name='buy_car'),
    path('my-purchases/', views.my_purchases, name='my_purchases'),
    path('test-drive/schedule/<int:car_id>/', views.schedule_test_drive, name='schedule_test_drive'),
    path('loan/apply/<int:car_id>/', views.apply_loan, name='apply_loan'),
    path('loan/edit/<int:pk>/', views.edit_loan, name='edit_loan'),
    path('my-test-drives/', views.my_test_drives, name='my_test_drives'),
    path('my-loans/', views.my_loans, name='my_loans'),

    # Company
    path('company/dashboard/', views.company_dashboard, name='company_dashboard'),
    path('company/cars/', views.company_car_list, name='company_car_list'),
    path('company/cars/add/', views.company_car_add, name='company_car_add'),
    path('company/cars/edit/<int:pk>/', views.company_car_edit, name='company_car_edit'),
    path('company/cars/delete/<int:pk>/', views.company_car_delete, name='company_car_delete'),
    path('company/parts/', views.company_part_list, name='company_part_list'),
    path('company/parts/add/', views.company_part_add, name='company_part_add'),
    path('company/parts/edit/<int:pk>/', views.company_part_edit, name='company_part_edit'),
    path('company/parts/delete/<int:pk>/', views.company_part_delete, name='company_part_delete'),
    path('company/test-drives/', views.company_test_drive_list, name='company_test_drive_list'),
    path('company/test-drives/update/<int:pk>/', views.company_test_drive_update, name='company_test_drive_update'),
    path('company/loans/', views.company_loan_list, name='company_loan_list'),
    path('company/loans/update/<int:pk>/', views.company_loan_update, name='company_loan_update'),
    path('company/car-purchases/', views.company_car_purchases, name='company_car_purchases'),
    path('company/car-purchases/update/<int:pk>/', views.company_update_purchase, name='company_update_purchase'),
    path('company/part-orders/', views.company_part_orders, name='company_part_orders'),

    # Admin
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/companies/', views.admin_company_list, name='admin_company_list'),
    path('dashboard/companies/add/', views.admin_company_add, name='admin_company_add'),
    path('dashboard/companies/edit/<int:pk>/', views.admin_company_edit, name='admin_company_edit'),
    path('dashboard/companies/delete/<int:pk>/', views.admin_company_delete, name='admin_company_delete'),
    path('dashboard/company-requests/', views.admin_company_requests, name='admin_company_requests'),
    path('dashboard/company-requests/<int:pk>/review/', views.admin_approve_company, name='admin_approve_company'),
    path('dashboard/users/', views.admin_user_list, name='admin_user_list'),
    path('dashboard/users/<int:pk>/', views.admin_user_detail, name='admin_user_detail'),
    path('dashboard/all-purchases/', views.admin_all_purchases, name='admin_all_purchases'),
    path('dashboard/all-part-orders/', views.admin_all_part_orders, name='admin_all_part_orders'),
]