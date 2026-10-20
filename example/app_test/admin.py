from django.contrib import admin

from example.app_test.models import Category, Customer, Product


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin): ...


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_filter = ["tenant"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_filter = ["tenant"]
