# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.shortcuts import render_to_response,HttpResponse,  RequestContext, HttpResponseRedirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from appbid import models as appModels
from system import models as systemModels


def hello(request):
    #Jarvis add the line for testing.
    return HttpResponse(" This is the home page")


def home(request, *args, **kwargs):
    """Query the apps info in home page."""
    initParam = {}
    page_range = systemModels.SystemParam.objects.filter(key='page_range')
    if page_range:
        page_range = page_range[0].value
    else:
        page_range = 10
    app_list = appModels.App.objects.all()
    paginator = Paginator(app_list, page_range)

    page = request.GET.get('page', 1)
    try:
        apps = paginator.page(page)
    except PageNotAnInteger:
        apps = paginator.page(1)
    except EmptyPage:
        apps = paginator.page(paginator.num_pages)
    initParam['apps'] = apps

    return render_to_response('home/home.html', initParam, context_instance=RequestContext(request))