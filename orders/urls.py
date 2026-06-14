from django.urls import path
from orders import views

app_name = "orders"

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('calculate-delivery/', views.calculate_delivery, name='calculate_delivery'),
    path('reverse-geocode/', views.reverse_geocode, name='reverse_geocode'),
    path('payment/card/<int:order_id>/', views.payment_card, name='payment_card'),
    path('payment/success/<int:order_id>/', views.payment_success, name='payment_success'),
    path('list/', views.user_orders, name='user_orders'),
    path('create', views.checkout, name='create_order'),
    path('checkout/<int:order_id>', views.payment_success, name='pay_order'),
]
