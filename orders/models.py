from django.db import models
from accounts.models import User
from shop.models import Product


class ShopSettings(models.Model):
    shop_address = models.TextField(
        default="Toshkent, O'zbekiston",
        verbose_name="Do'kon manzili",
        help_text="Do'kon joylashgan to'liq manzil (geocoding uchun ishlatiladi)"
    )
    shop_lat = models.FloatField(
        default=41.2995,
        verbose_name="Do'kon kengligi (lat)",
        help_text="Google Maps yoki Yandex Maps dan olish mumkin"
    )
    shop_lon = models.FloatField(
        default=69.2401,
        verbose_name="Do'kon uzunligi (lon)"
    )
    cost_per_km = models.IntegerField(
        default=1000,
        verbose_name="1 km uchun narx (so'm)"
    )
    min_delivery_cost = models.IntegerField(
        default=10000,
        verbose_name="Minimal yetkazib berish narxi (so'm)"
    )

    class Meta:
        verbose_name = "Do'kon sozlamalari"
        verbose_name_plural = "Do'kon sozlamalari"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Do'kon sozlamalari"


class Order(models.Model):
    PAYMENT_CASH = 'cash'
    PAYMENT_CARD = 'card'
    PAYMENT_CHOICES = [
        (PAYMENT_CASH, 'Naqd pul'),
        (PAYMENT_CARD, 'Karta orqali'),
    ]

    DELIVERY_PENDING = 'pending'
    DELIVERY_PROCESSING = 'processing'
    DELIVERY_SHIPPING = 'shipping'
    DELIVERY_DELIVERED = 'delivered'
    DELIVERY_CANCELLED = 'cancelled'
    DELIVERY_CHOICES = [
        (DELIVERY_PENDING, 'Kutilmoqda'),
        (DELIVERY_PROCESSING, 'Tayyorlanmoqda'),
        (DELIVERY_SHIPPING, 'Yetkazilmoqda'),
        (DELIVERY_DELIVERED, 'Yetkazildi'),
        (DELIVERY_CANCELLED, 'Bekor qilindi'),
    ]

    PAYMENT_STATUS_PENDING = 'pending'
    PAYMENT_STATUS_PAID = 'paid'
    PAYMENT_STATUS_FAILED = 'failed'
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, "To'lov kutilmoqda"),
        (PAYMENT_STATUS_PAID, "To'langan"),
        (PAYMENT_STATUS_FAILED, "Muvaffaqiyatsiz"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    full_name = models.CharField(max_length=100, default='')
    phone = models.CharField(max_length=20, default='')
    city = models.CharField(max_length=100, default='', blank=True)
    address = models.TextField(default='')
    notes = models.TextField(blank=True, default='')
    address_label = models.CharField(max_length=100, blank=True, default='', verbose_name="Manzil nomi")
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default=PAYMENT_CASH)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_PENDING)
    delivery_status = models.CharField(max_length=20, choices=DELIVERY_CHOICES, default=DELIVERY_PENDING)
    delivery_cost = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=False)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return f"{self.user.full_name} — buyurtma #{self.id}"

    @property
    def get_total_price(self):
        return sum(item.get_cost() for item in self.items.all())

    @property
    def get_grand_total(self):
        return self.get_total_price + self.delivery_cost


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    price = models.IntegerField()
    quantity = models.SmallIntegerField(default=1)

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        return self.price * self.quantity


class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    card_last4 = models.CharField(max_length=4)
    card_holder = models.CharField(max_length=100, blank=True, default='')
    amount = models.IntegerField()
    transaction_id = models.CharField(max_length=50, unique=True)
    card_type = models.CharField(max_length=20, default='card')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"To'lov #{self.transaction_id}"
