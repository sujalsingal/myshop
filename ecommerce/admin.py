from django.contrib import admin
from .models import * # replace with your actual models
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Order)
admin.site.register(Customer)
admin.site.register(OrderItem)
admin.site.register(Saved)
admin.site.register(Review)
