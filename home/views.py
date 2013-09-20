__author__ = 'Jarvis'

from django.shortcuts import render_to_response, RequestContext
from appbid import models as appModels
from query.views import queryAppsWithPaginator


def home(request, *args, **kwargs):
    """Query the apps info in home page."""
    initParam = {}
    page = request.GET.get('page', 1)
    apps = appModels.App.objects.filter(status=2)

    initParam['apps'] = queryAppsWithPaginator(request, page=page, apps=apps)

    return render_to_response('home/home.html', initParam, context_instance=RequestContext(request))
