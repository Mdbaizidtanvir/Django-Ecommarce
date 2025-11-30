# store/admin.py
from django.contrib import admin
from .models import *

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]

admin.site.register(Product, ProductAdmin)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price']

class PaidOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'email', 'status', 'payment_staus', 'total_price', 'created_at')
    inlines = [OrderItemInline]
    search_fields = ['user__username', 'email']
    list_filter = ['status', 'payment_staus', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(payment_staus='paid')  # Only show paid orders

admin.site.register(Order, PaidOrderAdmin)



@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'order_item', 'created_at', 'pickup_date')
    search_fields = ('user__username', 'order_item__product__name')
    list_filter = ('created_at',)


admin.site.register(NewsletterEmail)
admin.site.register(Category)
admin.site.register(Size)
admin.site.register(Color)
admin.site.register(Deals_of_the_Day)
admin.site.register(DiscountCode)
