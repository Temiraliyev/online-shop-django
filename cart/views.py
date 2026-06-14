from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from cart.utils.cart import Cart
from .forms import QuantityForm
from shop.models import Product


@login_required
def add_to_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = QuantityForm(request.POST)
    if form.is_valid():
        data = form.cleaned_data
        quantity = data['quantity']
        if product.stock == 0:
            messages.error(request, 'Kechirasiz, bu mahsulot omborda mavjud emas!', 'danger')
        elif quantity > product.stock:
            messages.warning(request, f'Faqat {product.stock} ta mavjud. Miqdor avtomatik moslantirildi.', 'warning')
            cart.add(product=product, quantity=product.stock)
        else:
            cart.add(product=product, quantity=quantity)
            messages.success(request, 'Savatchaga qo\'shildi!', 'info')
    else:
        messages.error(request, 'Noto\'g\'ri miqdor kiritildi.', 'danger')
    return redirect('shop:product_detail', slug=product.slug)


@login_required
def show_cart(request):
    cart = Cart(request)
    context = {'title': 'Cart', 'cart': cart}
    return render(request, 'cart.html', context)


@login_required
def remove_from_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart:show_cart')