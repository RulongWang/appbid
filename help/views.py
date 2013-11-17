__author__ = 'Rulong'

from django.shortcuts import render_to_response, RequestContext
from appbid import models as appModels
from query.views import queryAppsWithPaginator




def guide(request, *args, **kwargs):
    """Query the apps info in home page."""
    initParam = {}
    page = request.GET.get('page', 1)
    apps = appModels.App.objects.filter(status=2)

    initParam['apps'] = queryAppsWithPaginator(request, page=page, apps=apps)

    return render_to_response('help/guide.html', initParam, context_instance=RequestContext(request))


def pricing(request, *args, **kwargs):
    """Query the apps info in home page."""
    initParam = {}
    page = request.GET.get('page', 1)
    apps = appModels.App.objects.filter(status=2)

    initParam['apps'] = queryAppsWithPaginator(request, page=page, apps=apps)

    return render_to_response('help/pricing.html', initParam, context_instance=RequestContext(request))


def support(request, *args, **kwargs):
    """Query the apps info in home page."""
    initParam = {}
    page = request.GET.get('page', 1)
    apps = appModels.App.objects.filter(status=2)

    initParam['apps'] = queryAppsWithPaginator(request, page=page, apps=apps)

    return render_to_response('help/support.html', initParam, context_instance=RequestContext(request))


def privacy(request, *args, **kwargs):
    """Query the apps info in home page."""
    initParam = {}
    page = request.GET.get('page', 1)
    apps = appModels.App.objects.filter(status=2)

    initParam['apps'] = queryAppsWithPaginator(request, page=page, apps=apps)

    return render_to_response('help/privacy.html', initParam, context_instance=RequestContext(request))


def terms(request, *args, **kwargs):
    """Query the apps info in home page."""
    initParam = {}
    page = request.GET.get('page', 1)
    apps = appModels.App.objects.filter(status=2)

    initParam['apps'] = queryAppsWithPaginator(request, page=page, apps=apps)

    return render_to_response('help/terms.html', initParam, context_instance=RequestContext(request))


def security(request, *args, **kwargs):
    """Query the apps info in home page."""
    initParam = {}
    page = request.GET.get('page', 1)
    apps = appModels.App.objects.filter(status=2)

    initParam['apps'] = queryAppsWithPaginator(request, page=page, apps=apps)

    return render_to_response('help/security.html', initParam, context_instance=RequestContext(request))


def contact(request, *args, **kwargs):
    """Query the apps info in home page."""
    initParam = {}
    page = request.GET.get('page', 1)
    apps = appModels.App.objects.filter(status=2)

    initParam['apps'] = queryAppsWithPaginator(request, page=page, apps=apps)

    return render_to_response('help/contact.html', initParam, context_instance=RequestContext(request))


def siterules(request, *args, **kwargs):
    """Query the apps info in home page."""

    return render_to_response('help/siterules.html', context_instance=RequestContext(request))


def about(request, *args, **kwargs):
    """Query the apps info in home page."""
    initParam = {}
    page = request.GET.get('page', 1)
    apps = appModels.App.objects.filter(status=2)

    initParam['apps'] = queryAppsWithPaginator(request, page=page, apps=apps)

    return render_to_response('help/about.html', initParam, context_instance=RequestContext(request))



