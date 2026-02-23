from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from .models import (Car, Part, TestDrive, LoanApplication, Cart, CartItem, 
                     Company, CarPurchase, CompanyRequest, PartOrder, PartOrderItem)
from .forms import CarForm, PartForm, TestDriveForm, LoanApplicationForm, CompanyForm, CompanyRequestForm

# Role check functions
def is_admin(user):
    return user.is_staff

def is_company(user):
    return hasattr(user, 'company')

def is_regular_user(user):
    return user.is_authenticated and not user.is_staff and not hasattr(user, 'company')

# ==================== PUBLIC VIEWS ====================
def home(request):
    featured_cars = Car.objects.filter(status='available')[:6]
    companies = Company.objects.all()[:4]
    return render(request, 'main/home.html', {
        'featured_cars': featured_cars,
        'companies': companies
    })

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('main:register')
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        messages.success(request, 'Registration successful!')
        return redirect('main:home')
    return render(request, 'main/register.html')

def company_register_request(request):
    if request.method == 'POST':
        form = CompanyRequestForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Company registration request submitted! Admin will review it soon.')
            return redirect('main:home')
    else:
        form = CompanyRequestForm()
    return render(request, 'main/company_register_request.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if user.is_staff:
                return redirect('main:admin_dashboard')
            elif hasattr(user, 'company'):
                return redirect('main:company_dashboard')
            else:
                return redirect('main:home')
        messages.error(request, 'Invalid credentials')
    return render(request, 'main/login.html')

def user_logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully')
    return redirect('main:home')

def car_list(request):
    cars = Car.objects.filter(status='available')
    companies = Company.objects.all()
    
    # Search filter
    search_query = request.GET.get('search', '')
    if search_query:
        cars = cars.filter(
            Q(model__icontains=search_query) |
            Q(company__name__icontains=search_query) |
            Q(color__icontains=search_query)
        )
    
    # Company filter
    selected_company = request.GET.get('company')
    if selected_company:
        cars = cars.filter(company__id=selected_company)
    
    return render(request, 'main/car_list.html', {
        'cars': cars,
        'companies': companies,
        'selected_company': selected_company,
        'search_query': search_query,
    })

def car_detail(request, pk):
    car = get_object_or_404(Car, pk=pk)
    parts = Part.objects.filter(company=car.company)
    return render(request, 'main/car_detail.html', {'car': car, 'parts': parts})

def part_list(request):
    parts = Part.objects.all()
    
    # Search filter
    search_query = request.GET.get('search', '')
    if search_query:
        parts = parts.filter(
            Q(name__icontains=search_query) |
            Q(category__icontains=search_query) |
            Q(company__name__icontains=search_query)
        )
    
    return render(request, 'main/part_list.html', {
        'parts': parts,
        'search_query': search_query,
    })

# ==================== USER VIEWS ====================
@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'main/cart.html', {'cart': cart})

@login_required
def add_to_cart(request, part_id):
    part = get_object_or_404(Part, pk=part_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, part=part)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f'{part.name} added to cart')
    return redirect('main:part_list')

@login_required
def update_cart_quantity(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
        action = request.POST.get('action')
        
        if action == 'increase':
            cart_item.quantity += 1
            cart_item.save()
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
                messages.info(request, 'Item removed from cart')
                return redirect('main:cart')
        
    return redirect('main:cart')

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, 'Item removed from cart')
    return redirect('main:cart')

@login_required
def checkout_parts(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.cartitem_set.all()
    
    if not cart_items:
        messages.error(request, 'Your cart is empty!')
        return redirect('main:cart')
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        shipping_address = request.POST.get('shipping_address')
        
        # Create order
        order = PartOrder.objects.create(
            user=request.user,
            total_amount=cart.get_total(),
            payment_method=payment_method,
            shipping_address=shipping_address,
            status='pending'
        )
        
        # Create order items
        for item in cart_items:
            PartOrderItem.objects.create(
                order=order,
                part=item.part,
                quantity=item.quantity,
                price=item.part.price
            )
        
        # Clear cart
        cart_items.delete()
        
        messages.success(request, f'Order #{order.id} placed successfully!')
        return redirect('main:my_part_orders')
    
    return render(request, 'main/checkout_parts.html', {'cart': cart})

@login_required
def my_part_orders(request):
    orders = PartOrder.objects.filter(user=request.user).order_by('-order_date')
    return render(request, 'main/my_part_orders.html', {'orders': orders})

@login_required
def buy_car(request, car_id):
    car = get_object_or_404(Car, pk=car_id)
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        
        purchase = CarPurchase.objects.create(
            user=request.user,
            car=car,
            total_price=car.price,
            payment_method=payment_method,
            status='pending'
        )
        car.status = 'reserved'
        car.save()
        messages.success(request, f'Purchase request for {car.company.name} {car.model} submitted!')
        return redirect('main:my_purchases')
    return render(request, 'main/buy_car.html', {'car': car})

@login_required
def my_purchases(request):
    purchases = CarPurchase.objects.filter(user=request.user).order_by('-purchase_date')
    return render(request, 'main/my_purchases.html', {'purchases': purchases})

@login_required
def schedule_test_drive(request, car_id):
    car = get_object_or_404(Car, pk=car_id)
    if request.method == 'POST':
        form = TestDriveForm(request.POST)
        if form.is_valid():
            test_drive = form.save(commit=False)
            test_drive.user = request.user
            test_drive.car = car
            test_drive.save()
            messages.success(request, 'Test drive scheduled successfully!')
            return redirect('main:my_test_drives')
    else:
        form = TestDriveForm()
    return render(request, 'main/schedule_test_drive.html', {'form': form, 'car': car})

@login_required
def apply_loan(request, car_id):
    car = get_object_or_404(Car, pk=car_id)
    if request.method == 'POST':
        form = LoanApplicationForm(request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.user = request.user
            loan.car = car
            loan.is_editable = True
            loan.save()
            messages.success(request, 'Loan application submitted!')
            return redirect('main:my_loans')
    else:
        form = LoanApplicationForm()
    return render(request, 'main/apply_loan.html', {'form': form, 'car': car})

@login_required
def edit_loan(request, pk):
    loan = get_object_or_404(LoanApplication, pk=pk, user=request.user)
    
    # Check if loan is editable
    if not loan.is_editable:
        messages.error(request, 'This loan has been reviewed and cannot be edited. Please contact the company.')
        return redirect('main:my_loans')
    
    if request.method == 'POST':
        form = LoanApplicationForm(request.POST, instance=loan)
        if form.is_valid():
            form.save()
            messages.success(request, 'Loan application updated successfully!')
            return redirect('main:my_loans')
    else:
        form = LoanApplicationForm(instance=loan)
    
    return render(request, 'main/edit_loan.html', {'form': form, 'loan': loan})

@login_required
def my_test_drives(request):
    test_drives = TestDrive.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'main/my_test_drives.html', {'test_drives': test_drives})

@login_required
def my_loans(request):
    loans = LoanApplication.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'main/my_loans.html', {'loans': loans})

# ==================== COMPANY VIEWS ====================
@login_required
def company_dashboard(request):
    if not hasattr(request.user, 'company'):
        messages.error(request, 'Access denied!')
        return redirect('main:home')
    company = request.user.company
    stats = {
        'total_cars': Car.objects.filter(company=company).count(),
        'total_parts': Part.objects.filter(company=company).count(),
        'pending_test_drives': TestDrive.objects.filter(car__company=company, status='pending').count(),
        'pending_loans': LoanApplication.objects.filter(car__company=company, status='pending').count(),
        'car_purchases': CarPurchase.objects.filter(car__company=company).count(),
        'part_orders': PartOrderItem.objects.filter(part__company=company).count(),
    }
    return render(request, 'main/company_dashboard.html', {'company': company, 'stats': stats})

@login_required
def company_car_list(request):
    if not hasattr(request.user, 'company'):
        return redirect('main:home')
    company = request.user.company
    cars = Car.objects.filter(company=company)
    return render(request, 'main/company_car_list.html', {'cars': cars, 'company': company})

@login_required
def company_car_add(request):
    if not hasattr(request.user, 'company'):
        return redirect('main:home')
    company = request.user.company
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES)
        if form.is_valid():
            car = form.save(commit=False)
            car.company = company
            car.save()
            messages.success(request, 'Car added successfully!')
            return redirect('main:company_car_list')
    else:
        form = CarForm()
    return render(request, 'main/company_car_form.html', {'form': form, 'action': 'Add'})

@login_required
def company_car_edit(request, pk):
    if not hasattr(request.user, 'company'):
        return redirect('main:home')
    company = request.user.company
    car = get_object_or_404(Car, pk=pk, company=company)
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES, instance=car)
        if form.is_valid():
            form.save()
            messages.success(request, 'Car updated successfully!')
            return redirect('main:company_car_list')
    else:
        form = CarForm(instance=car)
    return render(request, 'main/company_car_form.html', {'form': form, 'action': 'Edit'})

@login_required
def company_car_delete(request, pk):
    if not hasattr(request.user, 'company'):
        return redirect('main:home')
    car = get_object_or_404(Car, pk=pk, company=request.user.company)
    car.delete()
    messages.success(request, 'Car deleted!')
    return redirect('main:company_car_list')

@login_required
def company_part_list(request):
    if not hasattr(request.user, 'company'):
        return redirect('main:home')
    company = request.user.company
    parts = Part.objects.filter(company=company)
    return render(request, 'main/company_part_list.html', {'parts': parts, 'company': company})

@login_required
def company_part_add(request):
    if not hasattr(request.user, 'company'):
        return redirect('main:home')
    company = request.user.company
    if request.method == 'POST':
        form = PartForm(request.POST, request.FILES)
        if form.is_valid():
            part = form.save(commit=False)
            part.company = company
            part.save()
            form.save_m2m()
            messages.success(request, 'Part added successfully!')
            return redirect('main:company_part_list')
    else:
        form = PartForm()
    return render(request, 'main/company_part_form.html', {'form': form, 'action': 'Add'})

@login_required
def company_part_edit(request, pk):
    if not hasattr(request.user, 'company'):
        return redirect('main:home')
    part = get_object_or_404(Part, pk=pk, company=request.user.company)
    if request.method == 'POST':
        form = PartForm(request.POST, request.FILES, instance=part)
        if form.is_valid():
            form.save()
            messages.success(request, 'Part updated!')
            return redirect('main:company_part_list')
    else:
        form = PartForm(instance=part)
    return render(request, 'main/company_part_form.html', {'form': form, 'action': 'Edit'})

@login_required
def company_part_delete(request, pk):
    if not hasattr(request.user, 'company'):
        return redirect('main:home')
    part = get_object_or_404(Part, pk=pk, company=request.user.company)
    part.delete()
    messages.success(request, 'Part deleted!')
    return redirect('main:company_part_list')

@login_required
def company_test_drive_list(request):
    if not hasattr(request.user, 'company'):
        return redirect('main:home')
    company = request.user.company
    test_drives = TestDrive.objects.filter(car__company=company).order_by('-created_at')
    return render(request, 'main/company_test_drive_list.html', {'test_drives': test_drives})

@login_required
def company_test_drive_update(request, pk):
    if not hasattr(request.user, 'company'):
        return redirect('main:home')
    test_drive = get_object_or_404(TestDrive, pk=pk, car__company=request.user.company)
    if request.method == 'POST':
        test_drive.status = request.POST.get('status')
        test_drive.save()
        messages.success(request, 'Test drive updated!')
        return redirect('main:company_test_drive_list')
    return render(request, 'main/company_test_drive_update.html', {'test_drive': test_drive})

@login_required
def company_loan_list(request):
    if not hasattr(request.user, 'company'):
        return redirect('main:home')
    company = request.user.company
    loans = LoanApplication.objects.filter(car__company=company).order_by('-created_at')
    return render(request, 'main/company_loan_list.html', {'loans': loans})

@login_required
def company_loan_update(request, pk):
    if not hasattr(request.user, 'company'):
        return redirect('main:home')
    loan = get_object_or_404(LoanApplication, pk=pk, car__company=request.user.company)
    if request.method == 'POST':
        loan.status = request.POST.get('status')
        loan.admin_notes = request.POST.get('admin_notes', '')
        loan.is_editable = False  # Lock loan after review
        loan.save()
        messages.success(request, 'Loan updated!')
        return redirect('main:company_loan_list')
    return render(request, 'main/company_loan_update.html', {'loan': loan})

@login_required
def company_car_purchases(request):
    if not hasattr(request.user, 'company'):
        return redirect('main:home')
    company = request.user.company
    purchases = CarPurchase.objects.filter(car__company=company).order_by('-purchase_date')
    return render(request, 'main/company_car_purchases.html', {'purchases': purchases})

@login_required
def company_update_purchase(request, pk):
    if not hasattr(request.user, 'company'):
        return redirect('main:home')
    purchase = get_object_or_404(CarPurchase, pk=pk, car__company=request.user.company)
    if request.method == 'POST':
        purchase.status = request.POST.get('status')
        if request.POST.get('status') == 'paid':
            purchase.payment_date = timezone.now()
        purchase.save()
        messages.success(request, 'Purchase status updated!')
        return redirect('main:company_car_purchases')
    return render(request, 'main/company_update_purchase.html', {'purchase': purchase})

@login_required
def company_part_orders(request):
    if not hasattr(request.user, 'company'):
        return redirect('main:home')
    company = request.user.company
    order_items = PartOrderItem.objects.filter(part__company=company).select_related('order', 'part').order_by('-order__order_date')
    return render(request, 'main/company_part_orders.html', {'order_items': order_items})

# ==================== ADMIN VIEWS ====================
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    stats = {
        'total_companies': Company.objects.count(),
        'total_users': User.objects.filter(is_staff=False, company__isnull=True).count(),
        'pending_test_drives': TestDrive.objects.filter(status='pending').count(),
        'pending_loans': LoanApplication.objects.filter(status='pending').count(),
        'pending_company_requests': CompanyRequest.objects.filter(status='pending').count(),
        'total_car_purchases': CarPurchase.objects.count(),
        'total_part_orders': PartOrder.objects.count(),
    }
    return render(request, 'main/admin_dashboard.html', {'stats': stats})

@login_required
@user_passes_test(is_admin)
def admin_company_list(request):
    companies = Company.objects.all().order_by('name')
    return render(request, 'main/admin_company_list.html', {'companies': companies})

@login_required
@user_passes_test(is_admin)
def admin_company_add(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        name = request.POST.get('name')
        country = request.POST.get('country')
        description = request.POST.get('description', '')
        established_year = request.POST.get('established_year', None)
        logo = request.FILES.get('logo')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('main:admin_company_add')

        user = User.objects.create_user(username=username, password=password)
        company = Company.objects.create(
            user=user,
            name=name,
            country=country,
            description=description,
            established_year=established_year if established_year else None,
            logo=logo
        )
        messages.success(request, f'Company {name} created with login credentials!')
        return redirect('main:admin_company_list')
    return render(request, 'main/admin_company_add.html')

@login_required
@user_passes_test(is_admin)
def admin_company_edit(request, pk):
    company = get_object_or_404(Company, pk=pk)
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, 'Company updated!')
            return redirect('main:admin_company_list')
    else:
        form = CompanyForm(instance=company)
    return render(request, 'main/admin_company_form.html', {'form': form, 'action': 'Edit'})

@login_required
@user_passes_test(is_admin)
def admin_company_delete(request, pk):
    company = get_object_or_404(Company, pk=pk)
    company.delete()
    messages.success(request, 'Company deleted!')
    return redirect('main:admin_company_list')

@login_required
@user_passes_test(is_admin)
def admin_user_list(request):
    users = User.objects.filter(is_staff=False, company__isnull=True).order_by('-date_joined')
    
    # Search filter
    search_query = request.GET.get('search', '')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    return render(request, 'main/admin_user_list.html', {
        'users': users,
        'search_query': search_query,
    })

@login_required
@user_passes_test(is_admin)
def admin_user_detail(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    test_drives = TestDrive.objects.filter(user=user_obj).order_by('-created_at')
    loans = LoanApplication.objects.filter(user=user_obj).order_by('-created_at')
    purchases = CarPurchase.objects.filter(user=user_obj).order_by('-purchase_date')
    part_orders = PartOrder.objects.filter(user=user_obj).order_by('-order_date')
    return render(request, 'main/admin_user_detail.html', {
        'user_obj': user_obj,
        'test_drives': test_drives,
        'loans': loans,
        'purchases': purchases,
        'part_orders': part_orders,
    })

@login_required
@user_passes_test(is_admin)
def admin_company_requests(request):
    requests = CompanyRequest.objects.all().order_by('-created_at')
    return render(request, 'main/admin_company_requests.html', {'requests': requests})

@login_required
@user_passes_test(is_admin)
def admin_approve_company(request, pk):
    company_request = get_object_or_404(CompanyRequest, pk=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve':
            if User.objects.filter(username=company_request.requested_username).exists():
                messages.error(request, 'Username already exists! Please reject this request and ask them to choose a different username.')
                return redirect('main:admin_company_requests')
            
            user = User.objects.create_user(
                username=company_request.requested_username,
                password=company_request.requested_password
            )
            
            company = Company.objects.create(
                user=user,
                name=company_request.company_name,
                country=company_request.country,
                description=company_request.description,
                established_year=company_request.established_year
            )
            
            company_request.status = 'approved'
            company_request.admin_notes = request.POST.get('admin_notes', '')
            company_request.save()
            
            messages.success(request, f'Company {company.name} approved! They can now login with username: {user.username}')
            
        elif action == 'reject':
            company_request.status = 'rejected'
            company_request.admin_notes = request.POST.get('admin_notes', '')
            company_request.save()
            messages.success(request, f'Company request from {company_request.company_name} rejected.')
        
        return redirect('main:admin_company_requests')
    
    return render(request, 'main/admin_approve_company.html', {'company_request': company_request})

@login_required
@user_passes_test(is_admin)
def admin_all_purchases(request):
    purchases = CarPurchase.objects.all().order_by('-purchase_date')
    return render(request, 'main/admin_all_purchases.html', {'purchases': purchases})

@login_required
@user_passes_test(is_admin)
def admin_all_part_orders(request):
    orders = PartOrder.objects.all().order_by('-order_date')
    return render(request, 'main/admin_all_part_orders.html', {'orders': orders})