import json
import time
import datetime
import string

from django.shortcuts import render_to_response, render, RequestContext, get_object_or_404, HttpResponse, Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect
from django.db.models import Max

from appbid import models as appModels
from utilities import common


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


@csrf_protect
def listFeatured(request, *args, **kwargs):
    """Query the apps info in featured page."""
    initParam = {}
    page = request.GET.get('page', 1)
    revenue_min = request.GET.get('revenue_min', None)
    category = request.GET.get('category', None)
    subcategory = request.GET.get('subcategory', None)
    monetize = request.GET.get('monetize', None)
    currency_id = common.getSystemParam(key='currency', default=2)
    initParam['currency'] = get_object_or_404(appModels.Currency, pk=currency_id)

    if revenue_min is None and category is None and subcategory is None and monetize is None:
        apps = appModels.App.objects.filter(status=2)

    #Revenue Part
    REVENUE_LIST = [2000, 1000, 500, 100, 0]
    initParam['revenue_list'] = []
    for i in range(len(REVENUE_LIST)):
        if i == 0:
            temp_apps = appModels.App.objects.filter(status=2, revenue__gte=REVENUE_LIST[i])
        else:
            temp_apps = appModels.App.objects.filter(status=2, revenue__lt=REVENUE_LIST[i-1], revenue__gte=REVENUE_LIST[i])
        if revenue_min and string.atoi(revenue_min) == REVENUE_LIST[i]:
            apps = temp_apps
            title = _('Revenue(%(param)s/Month)') % {'param': initParam['currency'].currency}
            subTitle = _('Over %(param)s') % {'param': revenue_min}
            initParam['query_tile'] = [title, subTitle, ''.join(['?revenue_min=', revenue_min])]
        initParam['revenue_list'].append([REVENUE_LIST[i], len(temp_apps)])

    #Monetize Part
    initParam['monetize_list'] = []
    if monetize:
        monetizeModel = get_object_or_404(appModels.Monetize, pk=monetize)
    for temp_monetize in appModels.Monetize.objects.all():
        if monetize and monetizeModel == temp_monetize:
            apps = monetizeModel.app_set.filter(status=2, monetize=monetizeModel)
            initParam['monetize_list'].append([temp_monetize, len(apps)])
            initParam['query_tile'] = [_('Monetize'), temp_monetize.method, ''.join(['?monetize=', monetize])]
        else:
            initParam['monetize_list'].append([temp_monetize, len(temp_monetize.app_set.filter(status=2))])

    #Category Part
    initParam['category_list'] = []
    if category:
        categoryModel = get_object_or_404(appModels.Category, apple_id=category)
    for temp_category in appModels.Category.objects.all():
        if category and categoryModel == temp_category:
            apps = appModels.App.objects.filter(status=2, category=categoryModel)
            initParam['category_list'].append([temp_category, len(apps)])
            initParam['query_tile'] = [_('Category'), temp_category.name, ''.join(['?category=', category])]
        else:
            initParam['category_list'].append([temp_category, len(temp_category.app_set.filter(status=2))])
    common.sortWithIndexLie(initParam['category_list'], 1, order='desc')

    #SubCategory Part from app detail page.
    if subcategory:
        subcategoryModel = get_object_or_404(appModels.SubCategory, apple_id=subcategory)
        apps = appModels.App.objects.filter(status=2, subcategory=subcategoryModel)
        initParam['query_tile'] = ['SubCategory', subcategoryModel.name, ''.join(['?subcategory=', subcategory])]

    #Query data
    initParam['apps'] = queryAppsWithPaginator(request, page=page, apps=apps)

    return render_to_response('query/listing_base.html', initParam, context_instance=RequestContext(request))


@csrf_protect
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

        category_map = {}
        for category in app.category.all():
            # Map key:category, Map value list[0]:the app number of category
            category_map[category] = [len(category.app_set.all())]
        for subcategory in app.subcategory.all():
            if category_map.get(subcategory.category):
                # Map value list[1]:subcategory, Map value list[2]:the app number of subcategory
                category_map.get(subcategory.category).append([subcategory, len(subcategory.app_set.all())])
        initParam['category_map'] = category_map

        initBidInfo(request, app=app, initParam=initParam)

        return render_to_response('query/listing_detail.html', initParam, context_instance=RequestContext(request))
    raise Http404


def initBidInfo(request, *args, **kwargs):
    """Init bid info, include bid num, current price, bid min price."""
    initParam = kwargs.get('initParam')
    app = kwargs.get('app')
    bids_len = app.bidding_set.count()
    initParam['bid_num'] = bids_len
    if bids_len:
        max_price = app.bidding_set.filter(status=1).aggregate(Max('price'))
        initParam['current_price'] = max_price.get('price__max')
    else:
        initParam['current_price'] = app.begin_price
    if initParam['current_price']:
        initParam['bid_price'] = initParam['current_price'] + app.minimum_bid
    else:
        initParam['bid_price'] = app.minimum_bid
    initParam['begin_bid'] = False
    current_date = datetime.datetime.combine(datetime.date.today(), datetime.time())
    if app.begin_date and app.end_date:
        if current_date >= app.begin_date:
            initParam['begin_bid'] = True
            initParam['time_remaining'] = time.mktime(time.strptime(str(app.end_date), '%Y-%m-%d %H:%M:%S'))
        else:
            initParam['time_remaining'] = time.mktime(time.strptime(str(app.begin_date), '%Y-%m-%d %H:%M:%S'))


def queryAppsWithPaginator(request, *args, **kwargs):
    """App query function for home page, feature page and so on."""
    page_range = kwargs.get('page_range')
    page = kwargs.get('page', 1)
    apps = kwargs.get('apps')

    if page_range is None:
        page_range = common.getSystemParam(key='page_range', default=10)

    if apps:
        app_list = []
        for app in apps:
            #info list[0]:The app info
            info_list = [app]
            app_list.append(info_list)

        paginator = Paginator(app_list, page_range)
        try:
            appInfoList = paginator.page(page)
        except PageNotAnInteger:
            appInfoList = paginator.page(1)
        except EmptyPage:
            appInfoList = paginator.page(paginator.num_pages)

        #Just query the app bid information showed in the current page.
        for info_list in appInfoList:
            data = {}
            initBidInfo(request, app=info_list[0], initParam=data)
            #info list[1]:current price
            info_list.append(data.get('current_price'))
            #info list[2]:bid numbers
            info_list.append(data.get('bid_num'))
            #info list[3]:bid price
            info_list.append(data.get('bid_price'))
    else:
        return None

    return appInfoList


def getBidInfo(request, *args, **kwargs):
    """Get the bid info"""
    data = {}
    try:
        dict = request.POST
    except:
        dict = request.GET
    try:
        app = appModels.App.objects.get(id=dict.get('id'))
        initBidInfo(request, app=app, initParam=data)
        data['ok'] = 'true'
    except appModels.App.DoesNotExist:
        data['ok'] = 'false'
    return HttpResponse(json.dumps(data), mimetype=u'application/json')
