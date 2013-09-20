__author__ = 'rulongwang'

import json
import os

from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, HttpResponse, RequestContext, HttpResponseRedirect, get_object_or_404, Http404
from django.views.decorators.csrf import csrf_protect
from django.utils.translation import ugettext as _
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.models import User


def activity(request, *args, **kwargs):
    return render_to_response("dashboard/activity.html",{"payment_accounts":'test'},
                        context_instance=RequestContext(request))



def inbox(request, *args, **kwargs):
    return render_to_response("dashboard/activity.html",{"payment_accounts":'test'},
                        context_instance=RequestContext(request))

def sentMsg(request, *args, **kwargs):
    return render_to_response("dashboard/sent_messages.html",{"payment_accounts":'test'},
                        context_instance=RequestContext(request))

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

