from django.contrib import admin

from example.app_test.models import Category, Customer, Product


class CustomerAdmin(admin.ModelAdmin):
    ...


class ProductAdmin(admin.ModelAdmin):
    list_filter = ["tenant"]


class CategoryAdmin(admin.ModelAdmin):
    list_filter = ["tenant"]


admin.site.register(Customer, CustomerAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
