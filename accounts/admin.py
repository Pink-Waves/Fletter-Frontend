from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin
from .models import ExtendedUser

admin.site.register(ExtendedUser, UserAdmin)
