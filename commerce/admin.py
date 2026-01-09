from django.contrib import admin
from .models import Product, ProductVariant, Customer, Order, OrderItem

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('nom', 'company', 'type', 'est_actif')
    inlines = [ProductVariantInline]
    list_filter = ('company', 'type', 'est_actif')

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('nom', 'email', 'company', 'ltv')
    list_filter = ('company',)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'company', 'montant_total', 'statut', 'source', 'date_creation')
    list_filter = ('company', 'statut', 'source')
    inlines = [OrderItemInline]
