import json
import time
import datetime

from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, render, RequestContext, get_object_or_404
from django.db.models import Max
from appbid import models as appModels


#register app entry
def register_app(request):
    return render(request, "seller/register_content.html",{"test":"test"})


def hello(request):
    return HttpResponse(" This is the home page")


def getIcon(request):
    pass


def list_latest(request):
    list_apps = []
    list_apps = appModels.App.objects.all()

    return render_to_response('query/listing_base.html', {"list_latest": list_apps}, context_instance=RequestContext(request))


def most_active(request):
    list_apps = []
    list_apps = appModels.App.objects.all()

    return render_to_response('query/listing_base.html', {"list_latest": list_apps}, context_instance=RequestContext(request))


def list_ending_soon(request):
    list_apps = []
    list_apps = appModels.App.objects.all()

    return render_to_response('query/listing_base.html', {"list_latest": list_apps}, context_instance=RequestContext(request))


def list_just_sold(request):
    list_apps = []
    list_apps = appModels.App.objects.all()

    return render_to_response('query/listing_base.html', {"list_latest": list_apps}, context_instance=RequestContext(request))

def list_featured(request):
    list_apps = []
    list_apps = appModels.App.objects.all()

    return render_to_response('query/listing_base.html', {"list_latest": list_apps}, context_instance=RequestContext(request))

def getDetail(request, *args, **kwargs):
    """Get app detail info."""
    if kwargs.get('pk'):
        initParam = {}
        app = get_object_or_404(appModels.App, pk=kwargs.get('pk'))
        initParam['app'] = app
        initParam['appInfo'] = app.appinfo
        initParam['attachments'] = app.attachment_set.all()
        initParam['cur_monetizes'] = app.monetize.all()
        initParam['all_monetizes'] = appModels.Monetize.objects.all()
        category_nums = {}
        for category in app.category.all():
            category_nums[category] = len(category.app_set.filter(category=category))
        initParam['category_nums'] = category_nums
        initBidInfo(app=app, initParam=initParam)
        return render_to_response('query/listing_detail.html', initParam, context_instance=RequestContext(request))
    raise Http404


def initBidInfo(*args, **kwargs):
    """Init bid info, include bid num, current price, bid min price."""
    initParam = kwargs.get('initParam')
    app = kwargs.get('app')
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
    initParam['begin_bid'] = False
    if app.begin_date and datetime.datetime.now() >= app.begin_date:
        initParam['begin_bid'] = True
    if app.end_date:
        initParam['time_remaining'] = time.mktime(time.strptime(str(app.end_date), '%Y-%m-%d %H:%M:%S'))


def getBidInfo(request, *args, **kwargs):
    """Get the bid info"""
    data = {}
    try:
        dict = request.POST
    except:
        dict = request.GET
    try:
        app = appModels.App.objects.get(id=dict.get('id'))
        initBidInfo(app=app, initParam=data)
        data['ok'] = 'true'
    except appModels.App.DoesNotExist:
        data['ok'] = 'false'
    return HttpResponse(json.dumps(data), mimetype=u'application/json')
