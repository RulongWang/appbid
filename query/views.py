# Create your views here.
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, render, RequestContext, get_object_or_404
from appbid import models


#register app entry
def register_app(request):
    return render(request, "seller/register_content.html",{"test":"test"})


def hello(request):
    return HttpResponse(" This is the home page")


def getIcon(request):
    pass

def list_latest(request):
    list_apps = []
    return render_to_response('query/listing_base.html', {"list_latest":list_apps}, context_instance=RequestContext(request))


def getDetail(request, *args, **kwargs):
    """Get app detail info."""
    if kwargs['pk']:
        initParam = {}
        app = get_object_or_404(models.App, pk=kwargs['pk'])
        initParam['app'] = app
        initParam['appInfo'] = app.appinfo
        initParam['attachments'] = app.attachment_set.all()
        initParam['cur_monetizes'] = app.monetize.all()
        initParam['all_monetizes'] = models.Monetize.objects.all()
        category_nums = {}
        for category in app.category.all():
            category_nums[category] = len(category.app_set.filter(category=category))
        initParam['category_nums'] = category_nums
        return render_to_response('query/listing_detail.html', initParam, context_instance=RequestContext(request))
    raise Http404

