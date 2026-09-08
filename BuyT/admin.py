from django.contrib import admin
from .models import category, brand, product
from django.contrib import admin
from .models import Coupon, OrderTracking
from .models import Order, OrderItem

admin.site.register(Order)
admin.site.register(OrderItem)

admin.site.register(Coupon)
admin.site.register(OrderTracking)

admin.site.register(category)
admin.site.register(brand)
admin.site.register(product)
# Register your models here.
