from django.contrib import admin

from example.app_test.models import Customer, Product, Category


class CustomerAdmin(admin.ModelAdmin):
    filter_horizontal = ['users']


admin.site.register(Customer, CustomerAdmin)
admin.site.register(Product)
admin.site.register(Category)
