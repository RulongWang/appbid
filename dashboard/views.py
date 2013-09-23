__author__ = 'rulongwang'

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, RequestContext, get_object_or_404, redirect, Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_protect
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.db import transaction
from django.contrib import messages
from django.contrib.auth.models import User

from message import models as messageModels
from appbid import models as appModels
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
def listingOverview(request, *args, **kwargs):
    """Query user's app in listing overview page."""
    initParam = {}
    page = request.GET.get('page', 1)
    user = get_object_or_404(User, pk=request.user.id, username=request.user.username)
    apps = appModels.App.objects.filter(publisher_id=user)
    initParam['apps'] = common.queryWithPaginator(request, page=page, obj=apps)

    return render_to_response("dashboard/listing_overview.html", initParam, context_instance=RequestContext(request))


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
