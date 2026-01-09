from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Company, User

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('nom', 'slug', 'date_creation')
    prepopulated_fields = {'slug': ('nom',)}

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('company',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('company',)}),
    )
    list_display = UserAdmin.list_display + ('company',)
