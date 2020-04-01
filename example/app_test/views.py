from django.http import HttpResponse
from django.shortcuts import render

from example.app_test.models import Customer


def home(request):
    return HttpResponse('<h1>Home page</h1>')


def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'customer_list.html', {
        'object_list': customers
    })
