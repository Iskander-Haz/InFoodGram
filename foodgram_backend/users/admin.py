from django.contrib import admin
from .models import User, Subscribe


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email")
    list_filter = ("username", "email")


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    pass
