__author__ = 'rulongwang'

import json
import os

from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, HttpResponse, RequestContext, HttpResponseRedirect, get_object_or_404, Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_protect
from django.db import transaction
from django.utils.translation import ugettext as _
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.models import User

from message import models as messageModels
from utilities import common


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def inbox(request, *args, **kwargs):
    initParam = {}
    page = request.GET.get('page', 1)
    user = get_object_or_404(User, pk=request.user.id, username=request.user.username)
    page_range = common.getSystemParam(key='page_range', default=10)
    messages = messageModels.Message.objects.filter(receiver=user)
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
    messages = messageModels.Message.objects.filter(sender=user)
    paginator = Paginator(messages, page_range)
    try:
        message_list = paginator.page(page)
    except PageNotAnInteger:
        message_list = paginator.page(1)
    except EmptyPage:
        message_list = paginator.page(paginator.num_pages)
    initParam['message_list'] = message_list

    return render_to_response("dashboard/sent_messages.html", initParam, context_instance=RequestContext(request))


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

