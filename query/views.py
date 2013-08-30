import json

from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, render, RequestContext, get_object_or_404
from django.db.models import Max
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

        #The part of Bid info
        bids = app.bidding_set.all()
        initParam['bid_num'] = len(bids)
        if bids:
            max_price = app.bidding_set.filter(status=1).aggregate(Max('price'))
            initParam['current_price'] = max_price.get('price__max')
        else:
            initParam['current_price'] = app.begin_price
        if initParam['current_price']:
            initParam['bid_price'] = initParam['current_price'] + app.minimum_bid
        else:
            initParam['bid_price'] = app.minimum_bid
        return render_to_response('query/listing_detail.html', initParam, context_instance=RequestContext(request))
    raise Http404


def getBidInfo(request, *args, **kwargs):
    """Get the bid info"""
    data = {}
    try:
        dict = request.POST
    except:
        dict = request.GET
    try:
        app = models.App.objects.get(id=dict.get('id'))
        bids = app.bidding_set.all()
        data['bid_num'] = len(bids)
        if bids:
            max_price = app.bidding_set.filter(status=1).aggregate(Max('price'))
            data['current_price'] = max_price.get('price__max')
        else:
            data['current_price'] = app.begin_price
        if data['current_price']:
            data['bid_price'] = data['current_price'] + app.minimum_bid
        else:
            data['bid_price'] = app.minimum_bid
        data['ok'] = 'true'
    except models.App.DoesNotExist:
        data['ok'] = 'false'
    return HttpResponse(json.dumps(data), mimetype=u'application/json')
