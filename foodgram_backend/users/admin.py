from django.contrib import admin
from .models import User, Subscribe


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    pass
