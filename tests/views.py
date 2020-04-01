from django.contrib.auth.decorators import login_required
from django.http import HttpResponse


def home(request):
    return HttpResponse('in home')


@login_required
def store_list(request):
    return HttpResponse('store lists')
