from django.contrib import admin
from .models import Order, register_user, sampling_stock, Designs

# Register your models here.
admin.site.register(Order)
admin.site.register(register_user)
admin.site.register(sampling_stock)
admin.site.register(Designs)