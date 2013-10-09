__author__ = 'rulongwang'

import datetime
import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, HttpResponse, RequestContext, get_object_or_404, redirect, Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_protect
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.db.models import Q, Max
from django.db import transaction
from django.contrib import messages
from django.contrib.auth.models import User

from message import models as messageModels
from appbid import models as appModels
from bid import models as bidModels
from transaction import models as txnModels
from dashboard import models
from utilities import common
from message.views import sendMessage


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def inbox(request, *args, **kwargs):
    initParam = {}
    page = request.GET.get('page', 1)
    user = get_object_or_404(User, pk=request.user.id, username=request.user.username)
    messages = messageModels.Message.objects.filter(receiver_id=user.id).order_by('-submit_date')
    initParam['message_list'] = common.queryWithPaginator(request, page=page, obj=messages)

    return render_to_response("dashboard/activity.html", initParam, context_instance=RequestContext(request))


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def sentMessages(request, *args, **kwargs):
    initParam = {}
    page = request.GET.get('page', 1)
    user = get_object_or_404(User, pk=request.user.id, username=request.user.username)
    messages = messageModels.Message.objects.filter(sender_id=user.id).order_by('-submit_date')
    initParam['message_list'] = common.queryWithPaginator(request, page=page, obj=messages)

    return render_to_response("dashboard/sent_messages.html", initParam, context_instance=RequestContext(request))


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def messageDetail(request, *args, **kwargs):
    """Query the message detail."""
    initParam = {}
    msg_action = kwargs.get('msg_action')
    if msg_action and (msg_action == 'reply' or msg_action == 'send'):
        initParam['msg_action'] = msg_action
    else:
        raise Http404
    user = get_object_or_404(User, pk=request.user.id, username=request.user.username)
    message = get_object_or_404(messageModels.Message, Q(pk=kwargs.get('msg_id')) & (Q(sender_id=user.id) | Q(receiver_id=user.id)))
    if msg_action == 'reply':
        message.is_read = True
        message.save()

    initParam['message'] = message
    initParam['page'] = request.GET.get('page', 1)

    return render_to_response("dashboard/message_detail.html", initParam, context_instance=RequestContext(request))


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def createMessage(request, *args, **kwargs):
    """User from inbox page, send messages page and app detail page, reply or send message."""
    initParam = {}
    username = kwargs.get('username')
    user_id = kwargs.get('user_id')
    msg_id = kwargs.get('msg_id')
    msg_action = kwargs.get('msg_action')
    if msg_action and (msg_action == 'reply' or msg_action == 'send'):
        initParam['msg_action'] = msg_action
    else:
        raise Http404

    user = get_object_or_404(User, pk=request.user.id, username=request.user.username)
    receiver = get_object_or_404(User, pk=user_id, username=username)

    if msg_id:
        if msg_action == 'reply':
            message = get_object_or_404(messageModels.Message, pk=msg_id, sender_id=receiver.id, receiver_id=user.id)
        if msg_action == 'send':
            message = get_object_or_404(messageModels.Message, pk=msg_id, sender_id=user.id, receiver_id=receiver.id)
        initParam['msg_id'] = message.id

    initParam['sender'] = user
    initParam['receiver'] = receiver
    initParam['next'] = request.GET.get('next', None)
    initParam['page'] = request.GET.get('page', 1)

    if sendMessage(request, initParam=initParam):
        messages.info(request, _('Send message successfully.'))
        return redirect(reverse('dashboard:sent_messages'))

    return render_to_response("dashboard/create_message.html", initParam, context_instance=RequestContext(request))


@csrf_protect
@login_required(login_url='/usersetting/home/')
def myListing(request, *args, **kwargs):
    """Query user's app in my listing page."""
    initParam = {}
    page_range = 5
    user = get_object_or_404(User, pk=request.user.id, username=request.user.username)

    draft_page = request.GET.get('draft_page', 1)
    published_page = request.GET.get('published_page', 1)
    traded_page = request.GET.get('traded_page', 1)
    initParam['draft_page'] = draft_page
    initParam['published_page'] = published_page
    initParam['traded_page'] = traded_page

    draft_apps = appModels.App.objects.filter(publisher_id=user, status=1)
    initParam['draft_apps'] = common.queryWithPaginator(request, page_range=page_range, page=draft_page, obj=draft_apps)

    published_apps = appModels.App.objects.filter(publisher_id=user, status=2)
    initParam['published_apps'] = common.queryWithPaginator(request, page_range=page_range, page=published_page,
                                                            obj=published_apps, query_method=queryAppServiceDetail)

    traded_apps = appModels.App.objects.filter(publisher_id=user, status=3)
    initParam['traded_apps'] = common.queryWithPaginator(request, page_range=page_range, page=traded_page,
                                                         obj=traded_apps, query_method=queryAppTxnInfo)

    return render_to_response("dashboard/my_listing.html", initParam, context_instance=RequestContext(request))


def queryAppServiceDetail(request, *args, **kwargs):
    """Return bid count."""
    if kwargs.get('obj_param'):
        return kwargs.get('obj_param').bidding_set.count()
    return None


def queryAppTxnInfo(request, *args, **kwargs):
    """
        Return app max price / transaction price, transaction status_id, status.
        If no trade now, then return max price of bid.
    """
    app = kwargs.get('obj_param')
    if app:
        transactions = txnModels.Transaction.objects.filter(app_id=app.id)
        if transactions:
            status_id = app.transaction.status
            status = txnModels.Transaction.STATUS[status_id-1][1]
            price = app.transaction.price
        else:
            status_id = 1
            status = txnModels.Transaction.STATUS[0][1]
            bids = app.bidding_set.filter(status=1).order_by('-price')
            if bids:
                price = bids[0].price
            else:
                price = 0
        return [price, status_id, status]
    return None


@csrf_protect
@login_required(login_url='/usersetting/home/')
def myBidding(request, *args, **kwargs):
    """Query user's bidding in my bidding page."""
    initParam = {}
    page_range = 5
    user = get_object_or_404(User, pk=request.user.id, username=request.user.username)

    joined_page = request.GET.get('joined_page', 1)
    won_page = request.GET.get('won_page', 1)
    initParam['joined_page'] = joined_page
    initParam['won_page'] = won_page

    #For joined bidding
    info_list = []
    bidInfo_map = bidModels.Bidding.objects.filter(buyer_id=user.id).values('app_id').annotate(max_price=Max('price'))
    for bidInfo in bidInfo_map:
        #list[0]: app_id; list[1]:my max price.
        info_list.append([bidInfo.get('app_id'), bidInfo.get('max_price')])
    initParam['joined_bids'] = common.queryWithPaginator(request, page_range=page_range, page=joined_page,
                                                         obj=info_list, query_method=queryJoinedBidInfo)

    #For won bidding
    transactions = txnModels.Transaction.objects.filter(buyer_id=user.id).exclude(status=1)
    initParam['transactions'] = common.queryWithPaginator(request, page_range=page_range, page=won_page,
                                                          obj=transactions, query_method=queryTxnInfo)

    return render_to_response("dashboard/my_bidding.html", initParam, context_instance=RequestContext(request))


def queryJoinedBidInfo(request, *args, **kwargs):
    """Return app bid info."""
    obj = kwargs.get('obj_param')
    if obj:
        app = appModels.App.objects.get(pk=obj[0])
        maxPrice = bidModels.Bidding.objects.filter(app_id=app.id, status=1).aggregate(Max('price'))
        #list[0]:app name; list[1]:end date; list[2]:app max price; list[3]:currency.
        return [app.app_name, app.end_date, maxPrice.get('price__max'), app.currency.currency]
    return None


def queryTxnInfo(request, *args, **kwargs):
    """Return transaction status."""
    transaction = kwargs.get('obj_param')
    if transaction:
        return txnModels.Transaction.STATUS[transaction.status-1][1]
    return None


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def watchApp(request, *args, **kwargs):
    data = {}
    try:
        dict = request.POST
    except:
        dict = request.GET
    try:
        apps = appModels.App.objects.filter(pk=dict.get('app_id'))
        if apps and apps[0].publisher.id != request.user.id:
            data['ok'] = 'true'
            count = models.WatchApp.objects.filter(app_id=apps[0].id, buyer_id=request.user.id).count()
            if count == 0:
                watchApp = models.WatchApp()
                watchApp.app = apps[0]
                watchApp.buyer = request.user
                watchApp.save()
        else:
            raise
    except:
        data['ok'] = 'false'
        data['message'] = _('Watch app failed.')
    return HttpResponse(json.dumps(data), mimetype=u'application/json')


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def unwatchApp(request, *args, **kwargs):
    data = {}
    try:
        dict = request.POST
    except:
        dict = request.GET
    try:
        apps = appModels.App.objects.filter(pk=dict.get('app_id'))
        if apps and apps[0].publisher.id != request.user.id:
            data['ok'] = 'true'
            watchApps = models.WatchApp.objects.filter(app_id=apps[0].id, buyer_id=request.user.id)
            if watchApps:
                watchApps[0].delete()
            else:
                raise
        else:
            raise
    except:
        data['ok'] = 'false'
        data['message'] = _('Unwatch app failed.')
    return HttpResponse(json.dumps(data), mimetype=u'application/json')


@csrf_protect
@login_required(login_url='/usersetting/home/')
def watchApps(request, *args, **kwargs):
    """Query user's watch apps in my watch apps page."""
    initParam = {}
    page = request.GET.get('page', 1)
    user = get_object_or_404(User, pk=request.user.id, username=request.user.username)
    watch_apps = models.WatchApp.objects.filter(buyer_id=user.id)
    initParam['watch_apps'] = common.queryWithPaginator(request, page=page,
                                                        obj=watch_apps, query_method=queryWatchAppMaxPrice)

    return render_to_response("dashboard/watched_apps.html", initParam, context_instance=RequestContext(request))


def queryWatchAppMaxPrice(request, *args, **kwargs):
    """Return watch app max price."""
    watchApp = kwargs.get('obj_param')
    if watchApp:
        max_price = watchApp.app.bidding_set.filter(status=1).aggregate(Max('price'))
        return max_price.get('price__max')
    return None


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def watchSeller(request, *args, **kwargs):
    data = {}
    try:
        dict = request.POST
    except:
        dict = request.GET
    try:
        users = User.objects.filter(pk=dict.get('user_id'))
        if users and users[0].id != request.user.id:
            data['ok'] = 'true'
            count = models.WatchSeller.objects.filter(seller_id=users[0].id, buyer_id=request.user.id).count()
            if count == 0:
                watchSeller = models.WatchSeller()
                watchSeller.seller = users[0]
                watchSeller.buyer = request.user
                watchSeller.save()
        else:
            raise
    except:
        data['ok'] = 'false'
        data['message'] = _('Watch seller failed.')
    return HttpResponse(json.dumps(data), mimetype=u'application/json')


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def unwatchSeller(request, *args, **kwargs):
    data = {}
    try:
        dict = request.POST
    except:
        dict = request.GET
    try:
        users = User.objects.filter(pk=dict.get('user_id'))
        if users and users[0].id != request.user.id:
            data['ok'] = 'true'
            watchSellers = models.WatchSeller.objects.filter(seller_id=users[0].id, buyer_id=request.user.id)
            if watchSellers:
                watchSellers[0].delete()
            else:
                raise
        else:
            raise
    except:
        data['ok'] = 'false'
        data['message'] = _('Unwatch seller failed.')
    return HttpResponse(json.dumps(data), mimetype=u'application/json')


@csrf_protect
@login_required(login_url='/usersetting/home/')
def watchSellers(request, *args, **kwargs):
    """Query user's watch sellers in my watch sellers page."""
    initParam = {}
    page = request.GET.get('page', 1)
    user = get_object_or_404(User, pk=request.user.id, username=request.user.username)
    watch_sellers = models.WatchSeller.objects.filter(buyer_id=user.id)
    initParam['watch_sellers'] = common.queryWithPaginator(request, page=page,
                                                           obj=watch_sellers, query_method=querySellerApps)
    return render_to_response("dashboard/watched_sellers.html", initParam, context_instance=RequestContext(request))


def querySellerApps(request, *args, **kwargs):
    """Return The user's app count."""
    watchSeller = kwargs.get('obj_param')
    if watchSeller:
        return appModels.App.objects.exclude(status=1).filter(publisher_id=watchSeller.seller.id).count()
    return None


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def watchCategory(request, *args, **kwargs):
    data = {}
    try:
        dict = request.POST
    except:
        dict = request.GET
    try:
        categories = appModels.Category.objects.filter(apple_id=dict.get('category_id'))
        if categories:
            data['ok'] = 'true'
            count = models.WatchCategory.objects.filter(category_id=categories[0].id, buyer_id=request.user.id).count()
            if count == 0:
                watchCategory = models.WatchCategory()
                watchCategory.category = categories[0]
                watchCategory.buyer = request.user
                watchCategory.save()
        else:
            raise
    except:
        data['ok'] = 'false'
        data['message'] = _('Watch category failed.')
    return HttpResponse(json.dumps(data), mimetype=u'application/json')


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def unwatchCategory(request, *args, **kwargs):
    data = {}
    try:
        dict = request.POST
    except:
        dict = request.GET
    try:
        categories = appModels.Category.objects.filter(apple_id=dict.get('category_id'))
        if categories:
            data['ok'] = 'true'
            watchCategories = models.WatchCategory.objects.filter(category_id=categories[0].id, buyer_id=request.user.id)
            if watchCategories:
                watchCategories[0].delete()
            else:
                raise
        else:
            raise
    except:
        data['ok'] = 'false'
        data['message'] = _('Unwatch category failed.')
    return HttpResponse(json.dumps(data), mimetype=u'application/json')


@csrf_protect
@login_required(login_url='/usersetting/home/')
def watchCategories(request, *args, **kwargs):
    """Query user's watch categories in my watch categories page."""
    initParam = {}
    page = request.GET.get('page', 1)
    user = get_object_or_404(User, pk=request.user.id, username=request.user.username)
    watch_categories = models.WatchCategory.objects.filter(buyer_id=user.id)
    initParam['watch_categories'] = common.queryWithPaginator(request, page=page,
                                                           obj=watch_categories, query_method=queryCategoryApps)
    return render_to_response("dashboard/watched_categories.html", initParam, context_instance=RequestContext(request))


def queryCategoryApps(request, *args, **kwargs):
    """Return The category's app count."""
    watchCategory = kwargs.get('obj_param')
    if watchCategory:
        return watchCategory.category.app_set.exclude(status=1).count()
    return None


def past_invoices(request, *args, **kwargs):
    return render_to_response("dashboard/pastinvoices.html",{"payment_accounts":'test'},
                        context_instance=RequestContext(request))


def unpaid_fees(request, *args, **kwargs):
    return render_to_response("dashboard/unpaid_fees.html",{"payment_accounts":'test'},
                        context_instance=RequestContext(request))


def past_orders(request, *args, **kwargs):
    return render_to_response("dashboard/past_orders.html",{"payment_accounts":'test'},
                        context_instance=RequestContext(request))
