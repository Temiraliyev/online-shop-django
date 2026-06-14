from django.db import models
from django.contrib.auth.models import AbstractBaseUser

from .managers import UserManager
from shop.models import Product


class User(AbstractBaseUser):
    email = models.EmailField(max_length=100, unique=True)
    full_name = models.CharField(max_length=100)    
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    likes = models.ManyToManyField(Product, blank=True, related_name='likes')
    # set a manager role for shop manager to access orders and products
    is_manager = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']


    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

    def get_likes_count(self):
        return self.likes.count()


class SavedAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_addresses')
    label = models.CharField(max_length=100, verbose_name="Manzil nomi")
    full_address = models.TextField(verbose_name="To'liq manzil")
    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created',)
        verbose_name = "Saqlangan manzil"
        verbose_name_plural = "Saqlangan manzillar"

    def __str__(self):
        return f"{self.user.email} — {self.label}"