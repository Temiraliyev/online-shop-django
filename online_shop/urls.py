from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve



handler404 = 'online_shop.views.page_not_found'
handler500 = 'online_shop.views.server_error'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('shop.urls', namespace='shop')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('cart/', include('cart.urls', namespace='cart')),
    path('orders/', include('orders.urls', namespace='orders')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]