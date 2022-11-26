from django.contrib import admin

from .models import User

@admin.register(User)
class RequestDemoAdmin(admin.ModelAdmin):
    list_display = [field.name for field in User._meta.get_fields()]