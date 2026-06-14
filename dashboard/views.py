from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.http import Http404
from django.utils import timezone
from django.db.models import Count, Sum
import json
import datetime

from shop.models import Product, ProductImage
from accounts.models import User
from orders.models import Order, OrderItem, ShopSettings
from .forms import AddProductForm, AddCategoryForm, EditProductForm, AddManagerForm, ShopSettingsForm


def is_manager(user):
    try:
        return bool(user.is_authenticated and user.is_manager)
    except Exception:
        return False


@login_required(login_url='/accounts/login/manager/')
@user_passes_test(is_manager, login_url='/accounts/login/manager/')
def dashboard_home(request):
    today = timezone.now().date()
    last_30 = today - datetime.timedelta(days=29)

    daily_qs = (
        Order.objects
        .filter(created__date__gte=last_30, status=True)
        .extra(select={'day': 'date(created)'})
        .values('day')
        .annotate(count=Count('id'), revenue=Sum('delivery_cost'))
        .order_by('day')
    )

    items_revenue_qs = (
        OrderItem.objects
        .filter(order__created__date__gte=last_30, order__status=True)
        .extra(select={'day': 'date(orders_order.created)'}, tables=['orders_order'],
               where=['orders_orderitem.order_id = orders_order.id'])
        .values('day')
        .annotate(items_total=Sum('price'))
        .order_by('day')
    )
    items_map = {row['day']: row['items_total'] or 0 for row in items_revenue_qs}

    labels = []
    order_counts = []
    revenues = []
    date_cursor = last_30
    while date_cursor <= today:
        labels.append(date_cursor.strftime('%d/%m'))
        date_cursor += datetime.timedelta(days=1)

    daily_map = {str(row['day']): row for row in daily_qs}
    date_cursor = last_30
    while date_cursor <= today:
        key = str(date_cursor)
        row = daily_map.get(key)
        order_counts.append(row['count'] if row else 0)
        delivery = row['revenue'] if row else 0
        items = items_map.get(date_cursor, 0)
        revenues.append((delivery or 0) + (items or 0))
        date_cursor += datetime.timedelta(days=1)

    today_revenue = sum(revenues[-1:])
    week_revenue = sum(revenues[-7:])
    month_revenue = sum(revenues)

    low_stock = Product.objects.filter(stock__lte=5).order_by('stock')

    context = {
        'title': 'Boshqaruv paneli',
        'products_count': Product.objects.count(),
        'orders_count': Order.objects.count(),
        'users_count': User.objects.count(),
        'managers_count': User.objects.filter(is_manager=True).count(),
        'recent_orders': Order.objects.order_by('-id')[:5],
        'chart_labels': json.dumps(labels),
        'chart_orders': json.dumps(order_counts),
        'chart_revenues': json.dumps(revenues),
        'today_revenue': today_revenue,
        'week_revenue': week_revenue,
        'month_revenue': month_revenue,
        'low_stock': low_stock,
    }
    return render(request, 'dashboard_home.html', context)


@login_required(login_url='/accounts/login/manager/')
@user_passes_test(is_manager, login_url='/accounts/login/manager/')
def products(request):
    products = Product.objects.all()
    context = {'title':'Products' ,'products':products}
    return render(request, 'products.html', context)


@login_required(login_url='/accounts/login/manager/')
@user_passes_test(is_manager, login_url='/accounts/login/manager/')
def add_product(request):
    if request.method == 'POST':
        form = AddProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            for i, img in enumerate(request.FILES.getlist('gallery_images')):
                ProductImage.objects.create(product=product, image=img, order=i)
            messages.success(request, 'Mahsulot muvaffaqiyatli qo\'shildi!')
            return redirect('dashboard:products')
    else:
        form = AddProductForm()
    context = {'title': 'Mahsulot qo\'shish', 'form': form}
    return render(request, 'add_product.html', context)


@login_required(login_url='/accounts/login/manager/')
@user_passes_test(is_manager, login_url='/accounts/login/manager/')
def delete_product(request, id):
    product = Product.objects.filter(id=id).delete()
    messages.success(request, 'product has been deleted!', 'success')
    return redirect('dashboard:products')


@login_required(login_url='/accounts/login/manager/')
@user_passes_test(is_manager, login_url='/accounts/login/manager/')
def edit_product(request, id):
    product = get_object_or_404(Product, id=id)
    if request.method == 'POST':
        form = EditProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            existing_count = product.images.count()
            for i, img in enumerate(request.FILES.getlist('gallery_images')):
                ProductImage.objects.create(product=product, image=img, order=existing_count + i)
            messages.success(request, 'Mahsulot yangilandi.')
            return redirect('dashboard:products')
    else:
        form = EditProductForm(instance=product)
    context = {'title': 'Mahsulot tahrirlash', 'form': form, 'gallery': product.images.all()}
    return render(request, 'edit_product.html', context)


@login_required(login_url='/accounts/login/manager/')
@user_passes_test(is_manager, login_url='/accounts/login/manager/')
def delete_gallery_image(request, id):
    img = get_object_or_404(ProductImage, id=id)
    product_id = img.product.id
    img.image.delete(save=False)
    img.delete()
    return redirect('dashboard:edit_product', id=product_id)


@login_required(login_url='/accounts/login/manager/')
@user_passes_test(is_manager, login_url='/accounts/login/manager/')
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


@login_required(login_url='/accounts/login/manager/')
@user_passes_test(is_manager, login_url='/accounts/login/manager/')
def orders(request):
    orders = Order.objects.all()
    context = {'title':'Orders', 'orders':orders}
    return render(request, 'orders.html', context)


@login_required(login_url='/accounts/login/manager/')
@user_passes_test(is_manager, login_url='/accounts/login/manager/')
def order_detail(request, id):
    order = get_object_or_404(Order, id=id)
    items = order.items.all()
    context = {'title': 'order detail', 'items': items, 'order': order}
    return render(request, 'order_detail.html', context)


@login_required(login_url='/accounts/login/manager/')
@user_passes_test(is_manager, login_url='/accounts/login/manager/')
def update_delivery_status(request, id):
    order = get_object_or_404(Order, id=id)
    if request.method == 'POST':
        status = request.POST.get('delivery_status')
        valid = [s[0] for s in Order.DELIVERY_CHOICES]
        if status in valid:
            order.delivery_status = status
            if status == 'delivered':
                order.status = True
            order.save()
            messages.success(request, f"Buyurtma #{order.id} holati yangilandi.")
    return redirect('dashboard:order_detail', id=order.id)


@login_required(login_url='/accounts/login/manager/')
@user_passes_test(is_manager, login_url='/accounts/login/manager/')
def users_list(request):
    users = User.objects.all().order_by('-is_manager', 'full_name')
    context = {'title': 'Foydalanuvchilar', 'users': users}
    return render(request, 'users.html', context)


@login_required(login_url='/accounts/login/manager/')
@user_passes_test(is_manager, login_url='/accounts/login/manager/')
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


@login_required(login_url='/accounts/login/manager/')
@user_passes_test(is_manager, login_url='/accounts/login/manager/')
def shop_settings(request):
    settings = ShopSettings.get_settings()
    if request.method == 'POST':
        form = ShopSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, "Do'kon sozlamalari saqlandi.")
            return redirect('dashboard:shop_settings')
    else:
        form = ShopSettingsForm(instance=settings)
    context = {
        'title': "Do'kon sozlamalari",
        'form': form,
        'settings': settings,
    }
    return render(request, 'shop_settings.html', context)


@login_required(login_url='/accounts/login/manager/')
@user_passes_test(is_manager, login_url='/accounts/login/manager/')
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