from django.contrib import admin
from django.urls import path

from example.app_test.views import (
    category_create,
    category_list,
    home,
    product_create,
    product_list,
)

urlpatterns = [
    path("", home, name="home"),
    path("category/new/", category_create, name="category-create"),
    path("category/list/", category_list, name="category-list"),
    path("product/new/", product_create, name="product-create"),
    path("product/list/", product_list, name="product-list"),
    path("t-admin/", admin.site.urls),
]
