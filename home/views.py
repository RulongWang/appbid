# Create your views here.
from django.http import HttpResponse

def hello(request):
    #Jarvis add the line for testing.
    return HttpResponse(" This is the home page")