import json

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .forms import UserRegistrationForm, UserLoginForm, ManagerLoginForm, EditProfileForm
from accounts.models import User, SavedAddress


def create_manager():
    """
    to execute once on startup:
    this function will call in online_shop/urls.py
    """
    if not User.objects.filter(email="manager@example.com").first():
        user = User.objects.create_user(
            "manager@example.com", 'shop manager' ,'managerpass1234'
        )
        # give this user manager role
        user.is_manager = True
        user.save()


def manager_login(request):
    if request.method == 'POST':
        form = ManagerLoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = authenticate(
                request, email=data['email'], password=data['password']
            )
            if user is not None and user.is_manager:
                login(request, user)
                return redirect('dashboard:dashboard_home')
            else:
                messages.error(
                    request, 'username or password is wrong', 'danger'
                )
                return redirect('accounts:manager_login')
    else:
        form = ManagerLoginForm()
    context = {'form': form}
    return render(request, 'manager_login.html', context)


def user_register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = User.objects.create_user(
                data['email'], data['full_name'], data['password']
            )
            return redirect('accounts:user_login')
    else:
        form = UserRegistrationForm()
    context = {'title':'Signup', 'form':form}
    return render(request, 'register.html', context)


def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = authenticate(
                request, email=data['email'], password=data['password']
            )
            if user is not None:
                login(request, user)
                return redirect('shop:home_page')
            else:
                messages.error(
                    request, 'username or password is wrong', 'danger'
                )
                return redirect('accounts:user_login')
    else:
        form = UserLoginForm()
    context = {'title':'Login', 'form': form}
    return render(request, 'login.html', context)


def user_logout(request):
    logout(request)
    return redirect('accounts:user_login')


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated', 'success')
            return redirect('accounts:edit_profile')
    else:
        form = EditProfileForm(instance=request.user)
    context = {'title': 'Edit Profile', 'form': form}
    return render(request, 'edit_profile.html', context)


@login_required
@require_POST
def save_address(request):
    try:
        data = json.loads(request.body)
        label = data.get('label', '').strip()
        full_address = data.get('full_address', '').strip()
        lat = data.get('lat')
        lon = data.get('lon')
        if not label or not full_address:
            return JsonResponse({'ok': False, 'error': 'Label va manzil kiritilishi shart'})
        addr = SavedAddress.objects.create(
            user=request.user,
            label=label,
            full_address=full_address,
            lat=lat,
            lon=lon,
        )
        return JsonResponse({'ok': True, 'id': addr.id, 'label': addr.label})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})


@login_required
def delete_address(request, pk):
    SavedAddress.objects.filter(pk=pk, user=request.user).delete()
    return JsonResponse({'ok': True})


@login_required
def my_addresses(request):
    addresses = request.user.saved_addresses.all()
    context = {
        'title': 'Manzillarim',
        'addresses': addresses,
    }
    return render(request, 'my_addresses.html', context)