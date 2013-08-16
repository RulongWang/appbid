# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
# from PIL import Image

#register app entry
def register_app(request):
    return render(request, "seller/register_content.html",{"test":"test"})


def hello(request):
    return HttpResponse(" This is the home page")


def getIcon(request):
    pass
