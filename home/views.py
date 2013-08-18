# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.shortcuts import render_to_response,HttpResponse,  RequestContext, HttpResponseRedirect, get_object_or_404



def hello(request):
    #Jarvis add the line for testing.
    return HttpResponse(" This is the home page")


def home(request):
    rangeNum = range(0, 7)
    return render_to_response('home/home.html',{'range': rangeNum}, context_instance=RequestContext(request))