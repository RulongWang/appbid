__author__ = 'Jarvis'

import datetime

from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render_to_response, RequestContext
from appbid import models as appModels
from query import views as queryViews


@csrf_protect
def home(request, *args, **kwargs):
    """Query the apps info in home page."""
    initParam = {}
    page = request.GET.get('page', 1)
    page_range = 10
    apps = appModels.App.objects.filter(status=2, end_date__gt=datetime.datetime.now())

    initParam['apps'] = queryViews.queryAppsWithPaginator(request, page_range=page_range, page=page, apps=apps)

    return render_to_response('home/home.html', initParam, context_instance=RequestContext(request))

@csrf_protect
def look(request, *args, **kwargs):
    """Query the apps info in home page."""
    initParam = {}
    return render_to_response('home/look.html', initParam, context_instance=RequestContext(request))


@csrf_protect
def haha(request, *args, **kwargs):
    """Query the apps info in home page."""
    initParam = {}
    return render_to_response('home/content.html', initParam, context_instance=RequestContext(request))


@csrf_protect
def screwHome(request, *args, **kwargs):
    """Query the apps info in screw home page."""
    initParam = {}
    page = request.GET.get('page', 1)
    page_range = 10
    apps = appModels.App.objects.filter(status=2, end_date__gt=datetime.datetime.now())

    initParam['apps'] = queryViews.queryAppsWithPaginator(request, page_range=page_range, page=page, apps=apps)

    return render_to_response('home/screw.html', initParam, context_instance=RequestContext(request))