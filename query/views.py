import json
import time
import datetime
import string
import urllib2

from django.shortcuts import render_to_response, render, RequestContext, get_object_or_404, HttpResponse, Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect
from django.db.models import Max
from django.contrib.auth.models import User

from appbid import models as appModels
from dashboard import models as dashboardModels
from usersetting import models as userSettingModels
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
    device = request.GET.get('device', None)
    seller = request.GET.get('seller', None)
    currency_id = common.getSystemParam(key='currency', default=2)
    initParam['currency'] = get_object_or_404(appModels.Currency, pk=currency_id)

    if revenue_min is None and category is None and subcategory is None and monetize is None and device is None and seller is None:
        apps = appModels.App.objects.exclude(status=1).order_by('status')

    #Revenue Part
    REVENUE_LIST = [2000, 1000, 500, 100, 0]
    initParam['revenue_list'] = []
    for i in range(len(REVENUE_LIST)):
        if i == 0:
            temp_apps = appModels.App.objects.exclude(status=1).filter(revenue__gte=REVENUE_LIST[i]).order_by('status')
        else:
            temp_apps = appModels.App.objects.exclude(status=1).filter(revenue__lt=REVENUE_LIST[i-1], revenue__gte=REVENUE_LIST[i]).order_by('status')
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
            apps = monetizeModel.app_set.exclude(status=1).order_by('status')
            initParam['monetize_list'].append([temp_monetize, len(apps)])
            initParam['query_tile'] = [_('Monetize'), temp_monetize.method, ''.join(['?monetize=', monetize])]
        else:
            initParam['monetize_list'].append([temp_monetize, temp_monetize.app_set.exclude(status=1).count()])

    #Device Part
    initParam['device_list'] = []
    if device:
        deviceModel = get_object_or_404(appModels.Device, pk=device)
    for tem_device in appModels.Device.objects.all():
        if device and deviceModel == tem_device:
            apps = deviceModel.app_set.exclude(status=1).order_by('status')
            initParam['device_list'].append([tem_device, len(apps)])
            initParam['query_tile'] = [_('Device'), tem_device.device, ''.join(['?device=', device])]
        else:
            initParam['device_list'].append([tem_device, tem_device.app_set.exclude(status=1).count()])

    #Category Part
    initParam['category_list'] = []
    if category:
        categoryModel = get_object_or_404(appModels.Category, apple_id=category)
    for temp_category in appModels.Category.objects.all():
        if category and categoryModel == temp_category:
            apps = categoryModel.app_set.exclude(status=1).order_by('status')
            initParam['category_list'].append([temp_category, len(apps)])
            initParam['query_tile'] = [_('Category'), temp_category.name, ''.join(['?category=', category])]
        else:
            initParam['category_list'].append([temp_category, temp_category.app_set.exclude(status=1).count()])
    common.sortWithIndexLie(initParam['category_list'], 1, order='desc')

    #SubCategory Part from app detail page.
    if subcategory:
        subcategoryModel = get_object_or_404(appModels.SubCategory, apple_id=subcategory)
        apps = subcategoryModel.app_set.exclude(status=1).order_by('status')
        initParam['query_tile'] = ['SubCategory', subcategoryModel.name, ''.join(['?subcategory=', subcategory])]

    #Seller part from watch sellers page.
    if seller:
        sellerModel = get_object_or_404(User, pk=seller)
        apps = sellerModel.app_set.exclude(status=1).order_by('status')
        initParam['query_tile'] = ['Seller', sellerModel.username, ''.join(['?seller=', seller])]

    #Query data
    initParam['apps'] = queryAppsWithPaginator(request, page=page, apps=apps)

    return render_to_response('query/listing_base.html', initParam, context_instance=RequestContext(request))


@csrf_protect
def getAppDetail(request, *args, **kwargs):
    """Get app detail info."""
    if kwargs.get('pk'):
        initParam = {}
        app = get_object_or_404(appModels.App, pk=kwargs.get('pk'))
        initParam['app'] = app
        initParam['appInfo'] = app.appinfo
        initParam['attachments'] = app.attachment_set.all()
        initParam['cur_monetizes'] = app.monetize.all()
        initParam['all_monetizes'] = appModels.Monetize.objects.all()
        userPublicProfiles = userSettingModels.UserPublicProfile.objects.filter(user_id=app.publisher.id)
        if userPublicProfiles and userPublicProfiles[0].thumbnail:
            initParam['thumbnail'] = app.publisher.userpublicprofile.thumbnail

        category_map = {}
        for category in app.category.all():
            #Check if user watch the category, if user is login.
            if request.user.is_authenticated() and dashboardModels.WatchCategory.objects.filter(category_id=category.id, buyer_id=request.user.id).count():
                # Map key:category, Map value list[0]:the app number of category, Map value list[1]:watch category
                category_map[category] = [category.app_set.exclude(status=1).count(), True]
            else:
                # Map key:category, Map value list[0]:the app number of category, Map value list[1]:unwatch category
                category_map[category] = [category.app_set.exclude(status=1).count(), False]
        for subcategory in app.subcategory.all():
            if category_map.get(subcategory.category):
                # Map value list[2]:subcategory, Map value list[3]:the app number of subcategory
                category_map.get(subcategory.category).append([subcategory, subcategory.app_set.exclude(status=1).count()])
        initParam['category_map'] = category_map

        initBidInfo(request, app=app, initParam=initParam)

        #Check if user watch the app/seller, if user is login.
        if request.user.is_authenticated():
            if dashboardModels.WatchApp.objects.filter(app_id=app.id, buyer_id=request.user.id).count():
                initParam['watch_app'] = True
            if dashboardModels.WatchSeller.objects.filter(seller_id=app.publisher.id, buyer_id=request.user.id).count():
                initParam['watch_seller'] = True

        #For social auth function
        urllib2.install_opener(urllib2.build_opener(common.HTTPSHandlerV3()))

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
    if app.status == 2 and app.begin_date and app.end_date:
        if current_date >= app.begin_date:
            initParam['begin_bid'] = True
            initParam['time_remaining'] = time.mktime(time.strptime(str(app.end_date), '%Y-%m-%d %H:%M:%S'))
        else:
            initParam['time_remaining'] = time.mktime(time.strptime(str(app.begin_date), '%Y-%m-%d %H:%M:%S'))
    elif app.status == 3:
        initParam['time_remaining'] = common.dateBefore(app.end_date)


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
            #info list[4]:remaining date, such as: [10, day], [25, minute]
            info_list.append(common.dateRemaining(info_list[0].end_date))
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
