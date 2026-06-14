from django.urls import path

from dashboard import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('products', views.products, name='products'),
    path('products/delete/<int:id>', views.delete_product, name='delete_product'),
    path('products/edit/<int:id>', views.edit_product, name='edit_product'),
    path('products/gallery/delete/<int:id>/', views.delete_gallery_image, name='delete_gallery_image'),
    path('orders', views.orders, name='orders'),
    path('orders/detail/<int:id>', views.order_detail, name='order_detail'),
    path('orders/update-status/<int:id>/', views.update_delivery_status, name='update_delivery_status'),
    path('add-product/', views.add_product, name='add_product'),
    path('add-category/', views.add_category, name='add_category'),
    path('users/', views.users_list, name='users_list'),
    path('users/toggle-manager/<int:id>/', views.toggle_manager, name='toggle_manager'),
    path('users/add-manager/', views.add_manager, name='add_manager'),
    path('settings/', views.shop_settings, name='shop_settings'),
]
