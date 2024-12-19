from django.contrib import admin
from .models import Customer,Cart,OrderPlaced,Product

admin.site.register(Customer)
admin.site.register(Cart)
admin.site.register(OrderPlaced)
admin.site.register(Product)