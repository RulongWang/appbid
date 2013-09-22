__author__ = 'rulongwang'

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, RequestContext, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_protect
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.db import transaction
from django.contrib import messages
from django.contrib.auth.models import User

from message import models as messageModels
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
@login_required(login_url='/usersetting/home/')
def messageDetail(request, *args, **kwargs):
    initParam = {}
    user = get_object_or_404(User, pk=request.user.id, username=request.user.username)
    message = get_object_or_404(messageModels.Message, pk=kwargs.get('pk'))
    initParam['message'] = message

    return render_to_response("dashboard/message_detail.html", initParam, context_instance=RequestContext(request))


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def createMessage(request, *args, **kwargs):
    """User from inbox page and send messages page reply or send message."""
    initParam = {}
    username = kwargs.get('username')
    user_id = kwargs.get('pk')
    user = get_object_or_404(User, pk=request.user.id, username=request.user.username)
    receiver = get_object_or_404(User, pk=user_id, username=username)
    initParam['sender'] = user
    initParam['receiver'] = receiver
    if sendMessage(request, initParam=initParam):
        messages.info(request, _('Send message successfully.'))
        return redirect(reverse('dashboard:sent_messages'))
    return render_to_response("dashboard/create_message.html", initParam, context_instance=RequestContext(request))


def past_orders(request, *args, **kwargs):
    return render_to_response("dashboard/past_orders.html",{"payment_accounts":'test'},
                        context_instance=RequestContext(request))

def past_invoices(request, *args, **kwargs):
    return render_to_response("dashboard/pastinvoices.html",{"payment_accounts":'test'},
                        context_instance=RequestContext(request))

def unpaid_fees(request, *args, **kwargs):
    return render_to_response("dashboard/unpaid_fees.html",{"payment_accounts":'test'},
                        context_instance=RequestContext(request))

def watched(request, *args, **kwargs):
    return render_to_response("dashboard/watched.html",{"payment_accounts":'test'},
                        context_instance=RequestContext(request))

def your_listing(request, *args, **kwargs):
    return render_to_response("dashboard/yourlisting.html",{"payment_accounts":'test'},
                        context_instance=RequestContext(request))

