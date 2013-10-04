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
    page_range = common.getSystemParam(key='page_range', default=10)
    messages = messageModels.Message.objects.filter(receiver=user).order_by('-submit_date')
    paginator = Paginator(messages, page_range)
    try:
        message_list = paginator.page(page)
    except PageNotAnInteger:
        message_list = paginator.page(1)
    except EmptyPage:
        message_list = paginator.page(paginator.num_pages)
    initParam['message_list'] = message_list

    return render_to_response("dashboard/activity.html", initParam, context_instance=RequestContext(request))


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def sentMessages(request, *args, **kwargs):
    initParam = {}
    page = request.GET.get('page', 1)
    user = get_object_or_404(User, pk=request.user.id, username=request.user.username)
    page_range = common.getSystemParam(key='page_range', default=10)
    messages = messageModels.Message.objects.filter(sender=user).order_by('-submit_date')
    paginator = Paginator(messages, page_range)
    try:
        message_list = paginator.page(page)
    except PageNotAnInteger:
        message_list = paginator.page(1)
    except EmptyPage:
        message_list = paginator.page(paginator.num_pages)
    initParam['message_list'] = message_list

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
    draft_page = request.GET.get('draft_page', 1)
    published_page = request.GET.get('published_page', 1)
    traded_page = request.GET.get('traded_page', 1)
    user = get_object_or_404(User, pk=request.user.id, username=request.user.username)

    draft_apps = appModels.App.objects.filter(publisher_id=user, status=1)
    initParam['draft_apps'] = common.queryWithPaginator(request, page_range=5, page=draft_page, obj=draft_apps)

    published_apps = appModels.App.objects.filter(publisher_id=user, status=2)
    initParam['published_apps'] = common.queryWithPaginator(request, page_range=5, page=published_page,
                                                            obj=published_apps, query_method=queryAppServiceDetail)

    traded_apps = appModels.App.objects.filter(publisher_id=user, status=3)
    initParam['traded_apps'] = common.queryWithPaginator(request, page_range=5, page=traded_page,
                                                         obj=traded_apps, query_method=queryAppServiceDetail)

    return render_to_response("dashboard/my_listing.html", initParam, context_instance=RequestContext(request))


def queryAppServiceDetail(request, *args, **kwargs):
    """Return bid count."""
    if kwargs.get('app'):
        return kwargs.get('app').bidding_set.count()
    return None


@csrf_protect
@login_required(login_url='/usersetting/home/')
def myBidding(request, *args, **kwargs):
    """Query user's bidding in my bidding page."""
    initParam = {}
    joined_page = request.GET.get('joined_page', 1)
    won_page = request.GET.get('won_page', 1)
    user = get_object_or_404(User, pk=request.user.id, username=request.user.username)

    #For joined bidding
    info_list = []
    bidInfo_map = bidModels.Bidding.objects.filter(buyer_id=user.id).values('app_id').annotate(max_price=Max('price'))
    for bidInfo in bidInfo_map:
        #list[0]: app_id; list[1]:my max price.
        info_list.append([bidInfo.get('app_id'), bidInfo.get('max_price')])
    paginator = Paginator(info_list, 5)
    try:
        initParam['joined_apps'] = paginator.page(joined_page)
    except PageNotAnInteger:
        initParam['joined_apps'] = paginator.page(1)
    except EmptyPage:
        initParam['joined_apps'] = paginator.page(paginator.num_pages)
    for info in initParam['joined_apps']:
        app = appModels.App.objects.get(pk=info[0])
        maxPrice = bidModels.Bidding.objects.filter(app_id=app.id, status=1).aggregate(Max('price'))
        #list[2]:app name; list[3]:end date; list[4]:app max price; list[5]:currency.
        info.extend([app.app_name, app.end_date, maxPrice.get('price__max'), app.currency.currency])


    # published_apps = appModels.App.objects.filter(publisher_id=user, status=2)
    # initParam['published_apps'] = common.queryWithPaginator(request, page_range=5, page=joined_page,
    #                                                         obj=published_apps, query_method=queryAppServiceDetail)

    won_apps = ''
    return render_to_response("dashboard/my_bidding.html", initParam, context_instance=RequestContext(request))


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
        if apps:
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
        if apps:
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


def watched(request, *args, **kwargs):
    return render_to_response("dashboard/watched.html",{"payment_accounts":'test'},
                        context_instance=RequestContext(request))


def past_invoices(request, *args, **kwargs):
    return render_to_response("dashboard/pastinvoices.html",{"payment_accounts":'test'},
                        context_instance=RequestContext(request))


def unpaid_fees(request, *args, **kwargs):
    return render_to_response("dashboard/unpaid_fees.html",{"payment_accounts":'test'},
                        context_instance=RequestContext(request))


def past_orders(request, *args, **kwargs):
    return render_to_response("dashboard/past_orders.html",{"payment_accounts":'test'},
                        context_instance=RequestContext(request))
