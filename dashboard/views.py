from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.http import Http404

from shop.models import Product
from accounts.models import User
from orders.models import Order, OrderItem
from .forms import AddProductForm, AddCategoryForm, EditProductForm, AddManagerForm


def is_manager(user):
    try:
        if not user.is_manager:
            raise Http404
        return True
    except:
        raise Http404


@user_passes_test(is_manager)
@login_required
def dashboard_home(request):
    context = {
        'title': 'Boshqaruv paneli',
        'products_count': Product.objects.count(),
        'orders_count': Order.objects.count(),
        'users_count': User.objects.count(),
        'managers_count': User.objects.filter(is_manager=True).count(),
        'recent_orders': Order.objects.order_by('-id')[:5],
    }
    return render(request, 'dashboard_home.html', context)


@user_passes_test(is_manager)
@login_required
def products(request):
    products = Product.objects.all()
    context = {'title':'Products' ,'products':products}
    return render(request, 'products.html', context)


@user_passes_test(is_manager)
@login_required
def add_product(request):
    if request.method == 'POST':
        form = AddProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added Successfuly!')
            return redirect('dashboard:add_product')
    else:
        form = AddProductForm()
    context = {'title':'Add Product', 'form':form}
    return render(request, 'add_product.html', context)


@user_passes_test(is_manager)
@login_required
def delete_product(request, id):
    product = Product.objects.filter(id=id).delete()
    messages.success(request, 'product has been deleted!', 'success')
    return redirect('dashboard:products')


@user_passes_test(is_manager)
@login_required
def edit_product(request, id):
    product = get_object_or_404(Product, id=id)
    if request.method == 'POST':
        form = EditProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product has been updated', 'success')
            return redirect('dashboard:products')
    else:
        form = EditProductForm(instance=product)
    context = {'title': 'Edit Product', 'form':form}
    return render(request, 'edit_product.html', context)


@user_passes_test(is_manager)
@login_required
def add_category(request):
    if request.method == 'POST':
        form = AddCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added Successfuly!')
            return redirect('dashboard:add_category')
    else:
        form = AddCategoryForm()
    context = {'title':'Add Category', 'form':form}
    return render(request, 'add_category.html', context)


@user_passes_test(is_manager)
@login_required
def orders(request):
    orders = Order.objects.all()
    context = {'title':'Orders', 'orders':orders}
    return render(request, 'orders.html', context)


@user_passes_test(is_manager)
@login_required
def order_detail(request, id):
    order = Order.objects.filter(id=id).first()
    items = OrderItem.objects.filter(order=order).all()
    context = {'title':'order detail', 'items':items, 'order':order}
    return render(request, 'order_detail.html', context)


@user_passes_test(is_manager)
@login_required
def users_list(request):
    users = User.objects.all().order_by('-is_manager', 'full_name')
    context = {'title': 'Foydalanuvchilar', 'users': users}
    return render(request, 'users.html', context)


@user_passes_test(is_manager)
@login_required
def toggle_manager(request, id):
    user = get_object_or_404(User, id=id)
    if user == request.user:
        messages.error(request, "O'zingizdan manager huquqini ololmaysiz.", 'danger')
        return redirect('dashboard:users_list')
    user.is_manager = not user.is_manager
    user.save()
    if user.is_manager:
        messages.success(request, f"{user.full_name} ga manager huquqi berildi.", 'success')
    else:
        messages.warning(request, f"{user.full_name} dan manager huquqi olindi.", 'warning')
    return redirect('dashboard:users_list')


@user_passes_test(is_manager)
@login_required
def add_manager(request):
    if request.method == 'POST':
        form = AddManagerForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = User.objects.create_user(
                data['email'], data['full_name'], data['password']
            )
            user.is_manager = True
            user.save()
            messages.success(request, f"Manager '{user.full_name}' muvaffaqiyatli qo'shildi.", 'success')
            return redirect('dashboard:users_list')
    else:
        form = AddManagerForm()
    context = {'title': 'Yangi manager qo\'shish', 'form': form}
    return render(request, 'add_manager.html', context)