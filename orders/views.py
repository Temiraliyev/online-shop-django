import uuid
import json
import math
import ssl
import urllib.request
import urllib.parse

_ssl_ctx = ssl.create_default_context()
_ssl_ctx.check_hostname = False
_ssl_ctx.verify_mode = ssl.CERT_NONE

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .models import Order, OrderItem, Payment, ShopSettings
from .forms import CheckoutForm, CardPaymentForm, detect_card_type
from cart.utils.cart import Cart


def _geocode(address):
    params = urllib.parse.urlencode({
        'q': address,
        'format': 'json',
        'limit': 1,
        'countrycodes': 'uz',
    })
    url = f'https://nominatim.openstreetmap.org/search?{params}'
    req = urllib.request.Request(
        url,
        headers={
            'User-Agent': 'Mozilla/5.0 (compatible; OnlineShop/1.0; +http://localhost)',
            'Referer': 'http://localhost:8000/',
            'Accept': 'application/json',
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=3, context=_ssl_ctx) as r:
            data = json.loads(r.read().decode('utf-8'))
            if data:
                return float(data[0]['lat']), float(data[0]['lon'])
    except Exception:
        pass
    return None


def _haversine_km(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def _get_delivery_cost(address, settings):
    coords = _geocode(address)
    if coords is None:
        return settings.min_delivery_cost
    lat, lon = coords
    dist_km = _haversine_km(settings.shop_lat, settings.shop_lon, lat, lon)
    cost = int(dist_km * settings.cost_per_km)
    return max(settings.min_delivery_cost, cost)


@require_GET
def reverse_geocode(request):
    try:
        lat = request.GET.get('lat', '').strip()
        lon = request.GET.get('lon', '').strip()
        if not lat or not lon:
            return JsonResponse({'address': ''})

        params = urllib.parse.urlencode({
            'lat': lat, 'lon': lon,
            'format': 'json',
            'accept-language': 'uz',
        })
        url = f'https://nominatim.openstreetmap.org/reverse?{params}'
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (compatible; OnlineShop/1.0; +http://localhost)',
            'Referer': 'http://localhost:8000/',
                'Accept': 'application/json',
            }
        )
        with urllib.request.urlopen(req, timeout=4, context=_ssl_ctx) as r:
            data = json.loads(r.read().decode('utf-8'))
            address = data.get('display_name', '')
            return JsonResponse({'address': address})
    except Exception:
        return JsonResponse({'address': ''})


@require_GET
def calculate_delivery(request):
    try:
        settings = ShopSettings.get_settings()
        lat = request.GET.get('lat')
        lon = request.GET.get('lon')

        if lat and lon:
            dist_km = _haversine_km(settings.shop_lat, settings.shop_lon, float(lat), float(lon))
            cost = max(settings.min_delivery_cost, int(dist_km * settings.cost_per_km))
            return JsonResponse({'cost': cost, 'distance_km': round(dist_km, 1)})

        address = request.GET.get('address', '').strip()
        if address and len(address) >= 5:
            cost = _get_delivery_cost(address, settings)
            return JsonResponse({'cost': cost})

        return JsonResponse({'cost': settings.min_delivery_cost})
    except Exception:
        return JsonResponse({'cost': 10000})


@login_required
def checkout(request):
    cart = Cart(request)
    if not cart.cart:
        messages.warning(request, "Savatingiz bo'sh. Avval mahsulot qo'shing!")
        return redirect('cart:show_cart')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            settings = ShopSettings.get_settings()

            try:
                lat = float(request.POST.get('delivery_lat', 0))
                lon = float(request.POST.get('delivery_lon', 0))
            except (ValueError, TypeError):
                lat = lon = 0.0

            if lat and lon:
                dist_km = _haversine_km(settings.shop_lat, settings.shop_lon, lat, lon)
                delivery_cost = max(settings.min_delivery_cost, int(dist_km * settings.cost_per_km))
            else:
                delivery_cost = _get_delivery_cost(data['address'], settings)

            address_label = request.POST.get('address_label', '').strip()
            order = Order.objects.create(
                user=request.user,
                full_name=data['full_name'],
                phone=data['phone'],
                city='',
                address=data['address'],
                address_label=address_label,
                notes=data.get('notes', ''),
                payment_method=data['payment_method'],
                delivery_cost=delivery_cost,
            )
            for item in cart:
                product = item['product']
                qty = item['quantity']
                if qty > product.stock:
                    order.delete()
                    messages.error(request, f"'{product.title}' mahsulotidan faqat {product.stock} ta mavjud. Savatchani yangilang.")
                    return redirect('cart:show_cart')
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    price=item['price'],
                    quantity=qty,
                )
                product.stock -= qty
                product.save()

            if data['payment_method'] == 'card':
                return redirect('orders:payment_card', order_id=order.id)

            cart.clear()
            order.payment_status = 'pending'
            order.delivery_status = 'processing'
            order.status = True
            order.save()
            return redirect('orders:payment_success', order_id=order.id)
    else:
        form = CheckoutForm(initial={'full_name': request.user.full_name})

    settings = ShopSettings.get_settings()
    context = {
        'title': 'Buyurtmani rasmiylashtirish',
        'form': form,
        'cart': cart,
        'shop_lat': settings.shop_lat,
        'shop_lon': settings.shop_lon,
        'saved_lat': request.POST.get('delivery_lat', ''),
        'saved_lon': request.POST.get('delivery_lon', ''),
        'saved_addresses': list(
            request.user.saved_addresses.values('id', 'label', 'full_address', 'lat', 'lon')
        ),
    }
    return render(request, 'checkout.html', context)


@login_required
def payment_card(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.payment_status == 'paid':
        return redirect('orders:payment_success', order_id=order.id)

    cart = Cart(request)

    if request.method == 'POST':
        form = CardPaymentForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            card_number = data['card_number'].replace(' ', '')
            last4 = card_number[-4:]
            card_type = detect_card_type(card_number)
            transaction_id = uuid.uuid4().hex[:16].upper()

            Payment.objects.create(
                order=order,
                card_last4=last4,
                card_holder='',
                amount=order.get_grand_total,
                transaction_id=transaction_id,
                card_type=card_type,
            )

            order.payment_status = 'paid'
            order.delivery_status = 'processing'
            order.status = True
            order.save()

            cart.clear()
            return redirect('orders:payment_success', order_id=order.id)
    else:
        form = CardPaymentForm()

    context = {
        'title': "Karta orqali to'lov",
        'order': order,
        'form': form,
    }
    return render(request, 'payment_card.html', context)


@login_required
def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {
        'title': "Buyurtma qabul qilindi",
        'order': order,
    }
    return render(request, 'payment_success.html', context)


@login_required
def user_orders(request):
    orders = request.user.orders.all()
    context = {'title': 'Buyurtmalarim', 'orders': orders}
    return render(request, 'user_orders.html', context)
