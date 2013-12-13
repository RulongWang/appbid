import json
import time
import datetime
import string
import urllib

from django.shortcuts import render_to_response, RequestContext, get_object_or_404, HttpResponse, Http404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Max, Q, Count
from django.contrib.auth.models import User

from appbid import settings
from appbid import models as appModels
from transaction import models as txnModels
from dashboard import models as dashboardModels
from usersetting import models as userSettingModels
from bid import models as bidModels
from utilities import common
from auth import views as authViews
from notification import views as notificationViews


def listLatest(request):
    """Query the apps info in new listings page."""
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
        apps = appModels.App.objects.filter(status=2, end_date__gt=datetime.datetime.now()).order_by('-end_date')

    #Revenue Part
    REVENUE_LIST = [2000, 1000, 500, 100, 0]
    initParam['revenue_list'] = []
    for i in range(len(REVENUE_LIST)):
        if i == 0:
            temp_apps = appModels.App.objects.filter(status=2, end_date__gt=datetime.datetime.now(), revenue__gte=REVENUE_LIST[i]).order_by('-end_date')
        else:
            temp_apps = appModels.App.objects.filter(status=2, end_date__gt=datetime.datetime.now(), revenue__lt=REVENUE_LIST[i-1], revenue__gte=REVENUE_LIST[i]).order_by('-end_date')
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
            apps = monetizeModel.app_set.filter(status=2, end_date__gt=datetime.datetime.now()).order_by('-end_date')
            initParam['monetize_list'].append([temp_monetize, len(apps)])
            initParam['query_tile'] = [_('Monetize'), temp_monetize.method, ''.join(['?monetize=', monetize])]
        else:
            initParam['monetize_list'].append([temp_monetize, temp_monetize.app_set.filter(status=2, end_date__gt=datetime.datetime.now()).count()])

    #Device Part
    initParam['device_list'] = []
    if device:
        deviceModel = get_object_or_404(appModels.Device, pk=device)
    for tem_device in appModels.Device.objects.all():
        if device and deviceModel == tem_device:
            apps = deviceModel.app_set.filter(status=2, end_date__gt=datetime.datetime.now()).order_by('-end_date')
            initParam['device_list'].append([tem_device, len(apps)])
            initParam['query_tile'] = [_('Device'), tem_device.device, ''.join(['?device=', device])]
        else:
            initParam['device_list'].append([tem_device, tem_device.app_set.filter(status=2, end_date__gt=datetime.datetime.now()).count()])

    #Category Part
    initParam['category_list'] = []
    if category:
        categoryModel = get_object_or_404(appModels.Category, apple_id=category)
    for temp_category in appModels.Category.objects.all():
        if category and categoryModel == temp_category:
            apps = categoryModel.app_set.filter(status=2, end_date__gt=datetime.datetime.now()).order_by('-end_date')
            initParam['category_list'].append([temp_category, len(apps)])
            initParam['query_tile'] = [_('Category'), temp_category.name, ''.join(['?category=', category])]
        else:
            initParam['category_list'].append([temp_category, temp_category.app_set.filter(status=2, end_date__gt=datetime.datetime.now()).count()])
    common.sortWithIndexLie(initParam['category_list'], 1, order='desc')

    #Query data
    initParam['apps'] = queryAppsWithPaginator(request, page=page, apps=apps)

    return render_to_response('query/listing_base.html', initParam, context_instance=RequestContext(request))


def mostActive(request):
    """Query the apps info in most active page."""
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

    app_id = []
    bids = bidModels.Bidding.objects.values('app').annotate(bid_num=Count('app')).order_by('-bid_num')
    for bid in bids:
        app_id.append(bid.get('app'))
    # apps = appModels.App.objects.raw('select * from appbid_app')

    if revenue_min is None and category is None and subcategory is None and monetize is None and device is None and seller is None:
        apps = appModels.App.objects.filter(pk__in=app_id, status=2)

    #Revenue Part
    REVENUE_LIST = [2000, 1000, 500, 100, 0]
    initParam['revenue_list'] = []
    for i in range(len(REVENUE_LIST)):
        if i == 0:
            temp_apps = appModels.App.objects.filter(pk__in=app_id, status=2, revenue__gte=REVENUE_LIST[i])
        else:
            temp_apps = appModels.App.objects.filter(pk__in=app_id, status=2, revenue__lt=REVENUE_LIST[i-1], revenue__gte=REVENUE_LIST[i])
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
            apps = monetizeModel.app_set.filter(pk__in=app_id, status=2)
            initParam['monetize_list'].append([temp_monetize, len(apps)])
            initParam['query_tile'] = [_('Monetize'), temp_monetize.method, ''.join(['?monetize=', monetize])]
        else:
            initParam['monetize_list'].append([temp_monetize, temp_monetize.app_set.filter(pk__in=app_id, status=2).count()])

    #Device Part
    initParam['device_list'] = []
    if device:
        deviceModel = get_object_or_404(appModels.Device, pk=device)
    for tem_device in appModels.Device.objects.all():
        if device and deviceModel == tem_device:
            apps = deviceModel.app_set.filter(pk__in=app_id, status=2)
            initParam['device_list'].append([tem_device, len(apps)])
            initParam['query_tile'] = [_('Device'), tem_device.device, ''.join(['?device=', device])]
        else:
            initParam['device_list'].append([tem_device, tem_device.app_set.filter(pk__in=app_id, status=2).count()])

    #Category Part
    initParam['category_list'] = []
    if category:
        categoryModel = get_object_or_404(appModels.Category, apple_id=category)
    for temp_category in appModels.Category.objects.all():
        if category and categoryModel == temp_category:
            apps = categoryModel.app_set.filter(pk__in=app_id, status=2)
            initParam['category_list'].append([temp_category, len(apps)])
            initParam['query_tile'] = [_('Category'), temp_category.name, ''.join(['?category=', category])]
        else:
            initParam['category_list'].append([temp_category, temp_category.app_set.filter(pk__in=app_id, status=2).count()])
    common.sortWithIndexLie(initParam['category_list'], 1, order='desc')

    #Query data
    initParam['apps'] = queryAppsWithPaginator(request, page=page, apps=apps)

    return render_to_response('query/listing_base.html', initParam, context_instance=RequestContext(request))


def endingSoon(request):
    """Query the apps info in ending soon page."""
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
        apps = appModels.App.objects.filter(status=2, end_date__gt=datetime.datetime.now()).order_by('end_date')

    #Revenue Part
    REVENUE_LIST = [2000, 1000, 500, 100, 0]
    initParam['revenue_list'] = []
    for i in range(len(REVENUE_LIST)):
        if i == 0:
            temp_apps = appModels.App.objects.filter(status=2, end_date__gt=datetime.datetime.now(), revenue__gte=REVENUE_LIST[i]).order_by('end_date')
        else:
            temp_apps = appModels.App.objects.filter(status=2, end_date__gt=datetime.datetime.now(), revenue__lt=REVENUE_LIST[i-1], revenue__gte=REVENUE_LIST[i]).order_by('end_date')
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
            apps = monetizeModel.app_set.filter(status=2, end_date__gt=datetime.datetime.now()).order_by('end_date')
            initParam['monetize_list'].append([temp_monetize, len(apps)])
            initParam['query_tile'] = [_('Monetize'), temp_monetize.method, ''.join(['?monetize=', monetize])]
        else:
            initParam['monetize_list'].append([temp_monetize, temp_monetize.app_set.filter(status=2, end_date__gt=datetime.datetime.now()).count()])

    #Device Part
    initParam['device_list'] = []
    if device:
        deviceModel = get_object_or_404(appModels.Device, pk=device)
    for tem_device in appModels.Device.objects.all():
        if device and deviceModel == tem_device:
            apps = deviceModel.app_set.filter(status=2, end_date__gt=datetime.datetime.now()).order_by('end_date')
            initParam['device_list'].append([tem_device, len(apps)])
            initParam['query_tile'] = [_('Device'), tem_device.device, ''.join(['?device=', device])]
        else:
            initParam['device_list'].append([tem_device, tem_device.app_set.filter(status=2, end_date__gt=datetime.datetime.now()).count()])

    #Category Part
    initParam['category_list'] = []
    if category:
        categoryModel = get_object_or_404(appModels.Category, apple_id=category)
    for temp_category in appModels.Category.objects.all():
        if category and categoryModel == temp_category:
            apps = categoryModel.app_set.filter(status=2, end_date__gt=datetime.datetime.now()).order_by('end_date')
            initParam['category_list'].append([temp_category, len(apps)])
            initParam['query_tile'] = [_('Category'), temp_category.name, ''.join(['?category=', category])]
        else:
            initParam['category_list'].append([temp_category, temp_category.app_set.filter(status=2, end_date__gt=datetime.datetime.now()).count()])
    common.sortWithIndexLie(initParam['category_list'], 1, order='desc')

    #Query data
    initParam['apps'] = queryAppsWithPaginator(request, page=page, apps=apps)

    return render_to_response('query/listing_base.html', initParam, context_instance=RequestContext(request))


def justSold(request):
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

    app_id = txnModels.Transaction.objects.filter(status__gte=2, is_active=True).values_list('app_id')

    if revenue_min is None and category is None and subcategory is None and monetize is None and device is None and seller is None:
        apps = appModels.App.objects.filter(pk__in=app_id)

    #Revenue Part
    REVENUE_LIST = [2000, 1000, 500, 100, 0]
    initParam['revenue_list'] = []
    for i in range(len(REVENUE_LIST)):
        if i == 0:
            temp_apps = appModels.App.objects.filter(pk__in=app_id, revenue__gte=REVENUE_LIST[i])
        else:
            temp_apps = appModels.App.objects.filter(pk__in=app_id, revenue__lt=REVENUE_LIST[i-1], revenue__gte=REVENUE_LIST[i])
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
            apps = monetizeModel.app_set.filter(pk__in=app_id)
            initParam['monetize_list'].append([temp_monetize, len(apps)])
            initParam['query_tile'] = [_('Monetize'), temp_monetize.method, ''.join(['?monetize=', monetize])]
        else:
            initParam['monetize_list'].append([temp_monetize, temp_monetize.app_set.filter(pk__in=app_id).count()])

    #Device Part
    initParam['device_list'] = []
    if device:
        deviceModel = get_object_or_404(appModels.Device, pk=device)
    for tem_device in appModels.Device.objects.all():
        if device and deviceModel == tem_device:
            apps = deviceModel.app_set.filter(pk__in=app_id)
            initParam['device_list'].append([tem_device, len(apps)])
            initParam['query_tile'] = [_('Device'), tem_device.device, ''.join(['?device=', device])]
        else:
            initParam['device_list'].append([tem_device, tem_device.app_set.filter(pk__in=app_id).count()])

    #Category Part
    initParam['category_list'] = []
    if category:
        categoryModel = get_object_or_404(appModels.Category, apple_id=category)
    for temp_category in appModels.Category.objects.all():
        if category and categoryModel == temp_category:
            apps = categoryModel.app_set.filter(pk__in=app_id)
            initParam['category_list'].append([temp_category, len(apps)])
            initParam['query_tile'] = [_('Category'), temp_category.name, ''.join(['?category=', category])]
        else:
            initParam['category_list'].append([temp_category, temp_category.app_set.filter(pk__in=app_id).count()])
    common.sortWithIndexLie(initParam['category_list'], 1, order='desc')

    #Query data
    initParam['apps'] = queryAppsWithPaginator(request, page=page, apps=apps)

    return render_to_response('query/listing_base.html', initParam, context_instance=RequestContext(request))


def listAll(request):
    """Query the apps info in all page."""
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
        apps = appModels.App.objects.exclude(status=1).order_by("-end_date")

    #Revenue Part
    REVENUE_LIST = [2000, 1000, 500, 100, 0]
    initParam['revenue_list'] = []
    for i in range(len(REVENUE_LIST)):
        if i == 0:
            temp_apps = appModels.App.objects.exclude(status=1).filter(revenue__gte=REVENUE_LIST[i]).order_by("-end_date")
        else:
            temp_apps = appModels.App.objects.exclude(status=1).filter(revenue__lt=REVENUE_LIST[i-1], revenue__gte=REVENUE_LIST[i]).order_by("-end_date")
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
            apps = monetizeModel.app_set.exclude(status=1).order_by("-end_date")
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
            apps = deviceModel.app_set.exclude(status=1).order_by("-end_date")
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
            apps = categoryModel.app_set.exclude(status=1).order_by("-end_date")
            initParam['category_list'].append([temp_category, len(apps)])
            initParam['query_tile'] = [_('Category'), temp_category.name, ''.join(['?category=', category])]
        else:
            initParam['category_list'].append([temp_category, temp_category.app_set.exclude(status=1).count()])
    common.sortWithIndexLie(initParam['category_list'], 1, order='desc')

    #Query data
    initParam['apps'] = queryAppsWithPaginator(request, page=page, apps=apps)

    return render_to_response('query/listing_base.html', initParam, context_instance=RequestContext(request))


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
        apps = appModels.App.objects.filter(status=2, end_date__gt=datetime.datetime.now())

    #Revenue Part
    REVENUE_LIST = [2000, 1000, 500, 100, 0]
    initParam['revenue_list'] = []
    for i in range(len(REVENUE_LIST)):
        if i == 0:
            temp_apps = appModels.App.objects.filter(status=2, end_date__gt=datetime.datetime.now(), revenue__gte=REVENUE_LIST[i]).order_by('status')
        else:
            temp_apps = appModels.App.objects.filter(status=2, end_date__gt=datetime.datetime.now(), revenue__lt=REVENUE_LIST[i-1], revenue__gte=REVENUE_LIST[i]).order_by('status')
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
            apps = monetizeModel.app_set.filter(status=2, end_date__gt=datetime.datetime.now())
            initParam['monetize_list'].append([temp_monetize, len(apps)])
            initParam['query_tile'] = [_('Monetize'), temp_monetize.method, ''.join(['?monetize=', monetize])]
        else:
            initParam['monetize_list'].append([temp_monetize, temp_monetize.app_set.filter(status=2, end_date__gt=datetime.datetime.now()).count()])

    #Device Part
    initParam['device_list'] = []
    if device:
        deviceModel = get_object_or_404(appModels.Device, pk=device)
    for tem_device in appModels.Device.objects.all():
        if device and deviceModel == tem_device:
            apps = deviceModel.app_set.filter(status=2, end_date__gt=datetime.datetime.now())
            initParam['device_list'].append([tem_device, len(apps)])
            initParam['query_tile'] = [_('Device'), tem_device.device, ''.join(['?device=', device])]
        else:
            initParam['device_list'].append([tem_device, tem_device.app_set.filter(status=2, end_date__gt=datetime.datetime.now()).count()])

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
        # transactions = txnModels.Transaction.objects.filter(end_time__isnull=False, end_time__lte=datetime.datetime.now())
        # transactions = txnModels.Transaction.objects.filter(end_time__isnull=False, end_time__year=2013, end_time__month=12, Q(end_time__day=3) | Q(end_time__day=13))
        # for txn in transactions:
        #     print txn.id, txn.end_time
        # print datetime.date(datetime.datetime.now())
        # if request.user.username == 'jarvis' or request.user.username == 'test':
        #     authViews.shareToTwitter(request, app=app)
        #     authViews.shareToWeiBo(request, app=app)
        appInfo = app.appinfo
        initParam['app'] = app
        initParam['appInfo'] = appInfo
        initParam['attachments'] = app.attachment_set.all()
        initParam['cur_monetizes'] = app.monetize.all()
        initParam['all_monetizes'] = appModels.Monetize.objects.all()
        q1 = request.GET.get('q1')
        q2 = request.GET.get('q2')
        q3 = request.GET.get('q3')
        if q1 and q2 and q3:
            initParam['query_tile'] = [q1, q2, q3]
        transactions = txnModels.Transaction.objects.filter(app_id=app.id).exclude(status=1)
        if transactions:
            initParam['transaction'] = transactions[0]

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
        #Do something, when the time is app end date.
        if app.status == 2 and initParam['begin_bid']:
            initParam['is_callback'] = True

        #Check if user watch the app/seller, if user is login.
        if request.user.is_authenticated():
            if dashboardModels.WatchApp.objects.filter(app_id=app.id, buyer_id=request.user.id).count():
                initParam['watch_app'] = True
            if dashboardModels.WatchSeller.objects.filter(seller_id=app.publisher.id, buyer_id=request.user.id).count():
                initParam['watch_seller'] = True

        #For social auth function
        # urllib2.install_opener(urllib2.build_opener(common.HTTPSHandlerV3()))
        shareSocial(request, initParam=initParam, app=app)

        return render_to_response('query/listing_detail.html', initParam, context_instance=RequestContext(request))
    raise Http404


def shareSocial(request, *args, **kwargs):
    initParam = kwargs.get('initParam')
    app = kwargs.get('app')
    appInfo = app.appinfo
    app_url = '/'.join([common.getHttpHeader(request), 'query/app-detail', str(app.id)])
    twitter = 'http://twitter.com/intent/tweet?'
    text = ''.join(['App (', app.app_name.encode('utf-8'), ') for sale from AppsWalk '])
    # initParam['twitter_url'] = twitter + urllib.urlencode({'status': status})
    initParam['twitter_url'] = twitter + urllib.urlencode({'url': app_url, 'text': text})
    initParam['http_header'] = common.getHttpHeader(request)

    facebook = 'http://www.facebook.com/sharer.php?'
    initParam['facebook_url'] = facebook + urllib.urlencode({'u': app_url, 't': text})

    weibo = 'http://service.weibo.com/share/share.php?'
    title = '- '.join([text, app_url])
    pic = ''.join([common.getHttpHeader(request), settings.MEDIA_URL, appInfo.icon])
    initParam['weibo_url'] = weibo + urllib.urlencode({'appkey': settings.WEIBO_CLIENT_KEY,
                                                       'title': title, 'pic': pic, 'url': app_url})
    initParam['title'] = text


@csrf_protect
@login_required(login_url='/usersetting/home/')
def addCommentForApp(request, *args, **kwargs):
    """Do operation, when add comment for App"""
    if kwargs.get('pk'):
        app = get_object_or_404(appModels.App, pk=kwargs.get('pk'))
        notificationViews.sendNewCommentEmail(request,app=app)
        return redirect(reverse('query:app_detail', kwargs={'pk': app.id}))


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
        initParam['current_price'] = 0
        initParam['bid_price'] = app.minimum_bid
    initParam['begin_bid'] = False
    # current_date = datetime.datetime.combine(datetime.date.today(), datetime.time())
    current_date = datetime.datetime.now()
    if app.status == 2 and app.begin_date and app.end_date:
        if current_date >= app.begin_date:
            if current_date < app.end_date:
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
            #info list[5]:percent of remaining date. 0:0, 1:1%-37%, 2:38%-62%, 1:63%-99%, 4:100%
            serviceDate = (info_list[0].end_date - info_list[0].begin_date).days
            if datetime.datetime.now() <= info_list[0].begin_date:
                percent = 100
            elif info_list[0].end_date <= datetime.datetime.now():
                percent = 0
            else:
                percent = (info_list[0].end_date - datetime.datetime.now()).days * 100 / serviceDate
            if percent <= 0:
                info_list.append(0)
            elif percent == 100:
                info_list.append(4)
            elif percent >= 63:
                info_list.append(3)
            elif percent >= 38:
                info_list.append(2)
            elif percent > 0:
                info_list.append(1)
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
