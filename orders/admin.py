from django.contrib import admin
from .models import Order, OrderItem, Payment, ShopSettings


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'price', 'quantity')


@admin.register(ShopSettings)
class ShopSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Do'kon manzili", {
            'fields': ('shop_address', 'shop_lat', 'shop_lon'),
            'description': (
                "Do'kon koordinatalarini Google Maps dan olish mumkin: "
                "xaritada o'ng tugma → 'Bu yerning koordinatalari' → nusxalash."
            ),
        }),
        ("Yetkazib berish narxi", {
            'fields': ('cost_per_km', 'min_delivery_cost'),
        }),
    )

    def has_add_permission(self, request):
        return not ShopSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'full_name', 'phone', 'payment_method',
                    'payment_status', 'delivery_status', 'delivery_cost', 'get_grand_total', 'created')
    list_filter = ('delivery_status', 'payment_method', 'payment_status')
    search_fields = ('user__email', 'full_name', 'phone', 'address')
    readonly_fields = ('created', 'updated', 'user')
    inlines = [OrderItemInline]
    list_per_page = 25
    list_editable = ('delivery_cost', 'delivery_status', 'payment_status')

    def get_grand_total(self, obj):
        return f"{obj.get_grand_total:,} so'm"
    get_grand_total.short_description = "Jami"


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'order', 'card_last4', 'card_type', 'amount', 'created')
    readonly_fields = ('transaction_id', 'created')
