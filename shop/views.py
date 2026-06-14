from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from shop.models import Product, Category, Review
from cart.forms import QuantityForm


def paginat(request, list_objects):
	p = Paginator(list_objects, 20)
	page_number = request.GET.get('page')
	try:
		page_obj = p.get_page(page_number)
	except PageNotAnInteger:
		page_obj = p.page(1)
	except EmptyPage:
		page_obj = p.page(p.num_pages)
	return page_obj


def home_page(request):
	products = Product.objects.all()
	context = {'products': paginat(request, products)}
	return render(request, 'home_page.html', context)


def product_detail(request, slug):
	form = QuantityForm()
	product = get_object_or_404(Product, slug=slug)
	related_products = Product.objects.filter(category=product.category).exclude(slug=slug)[:5]
	reviews = product.reviews.select_related('user').all()

	user_review = None
	can_review = False
	if request.user.is_authenticated:
		user_review = reviews.filter(user=request.user).first()
		if not user_review:
			from orders.models import Order
			can_review = Order.objects.filter(
				user=request.user,
				delivery_status='delivered',
				items__product=product
			).exists()

	context = {
		'title': product.title,
		'product': product,
		'form': form,
		'favorites': 'favorites',
		'related_products': related_products,
		'reviews': reviews,
		'user_review': user_review,
		'can_review': can_review,
		'gallery': product.images.all(),
	}
	if request.user.is_authenticated and request.user.likes.filter(id=product.id).first():
		context['favorites'] = 'remove'
	return render(request, 'product_detail.html', context)


@login_required
def submit_review(request, product_id):
	product = get_object_or_404(Product, id=product_id)
	if request.method == 'POST':
		try:
			rating = int(request.POST.get('rating', 5))
		except (ValueError, TypeError):
			rating = 5
		comment = request.POST.get('comment', '').strip()
		rating = max(1, min(5, rating))

		from orders.models import Order
		has_delivered = Order.objects.filter(
			user=request.user,
			delivery_status='delivered',
			items__product=product
		).exists()
		if not has_delivered:
			messages.error(request, "Sharh qoldirish uchun mahsulotni olgan bo'lishingiz kerak.")
			return redirect('shop:product_detail', slug=product.slug)

		Review.objects.update_or_create(
			product=product,
			user=request.user,
			defaults={'rating': rating, 'comment': comment}
		)
		messages.success(request, 'Sharhingiz qabul qilindi!')
	return redirect('shop:product_detail', slug=product.slug)


@login_required
def delete_review(request, product_id):
	product = get_object_or_404(Product, id=product_id)
	Review.objects.filter(product=product, user=request.user).delete()
	messages.success(request, 'Sharhingiz o\'chirildi.')
	return redirect('shop:product_detail', slug=product.slug)


@login_required
def add_to_favorites(request, product_id):
	product = get_object_or_404(Product, id=product_id)
	request.user.likes.add(product)
	return redirect('shop:product_detail', slug=product.slug)


@login_required
def remove_from_favorites(request, product_id):
	product = get_object_or_404(Product, id=product_id)
	request.user.likes.remove(product)
	return redirect('shop:favorites')


@login_required
def favorites(request):
	products = request.user.likes.all()
	context = {'title': 'Favorites', 'products': products}
	return render(request, 'favorites.html', context)


def search(request):
	query = request.GET.get('q', '').strip()
	products = Product.objects.filter(title__icontains=query).all() if query else Product.objects.none()
	context = {'products': paginat(request, products), 'query': query}
	return render(request, 'home_page.html', context)


def filter_by_category(request, slug):
	category = get_object_or_404(Category, slug=slug)
	result = list(Product.objects.filter(category=category))
	if not category.is_sub:
		for sub in category.sub_categories.all():
			result += list(Product.objects.filter(category=sub))
	context = {'products': paginat(request, result), 'category_name': category.title}
	return render(request, 'home_page.html', context)
