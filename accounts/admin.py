from django.contrib import admin

from .models import User, SavedAddress

admin.site.register(User)
admin.site.register(SavedAddress)