# Create your views here.
from django.http import HttpResponse

def hello(request):
    return HttpResponse(" This is the home page")