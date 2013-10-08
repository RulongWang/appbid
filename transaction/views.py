__author__ = 'Jarvis'

import time
import datetime
import string

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, RequestContext, redirect, get_object_or_404, Http404
from django.views.decorators.csrf import csrf_protect
from django.core.urlresolvers import reverse
from django.db import transaction
from django.contrib.auth.models import User

from appbid import models as appModels
from transaction import models
from bid import models as bidModels
from utilities import common
from notification import views as notificationViews


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def initTransaction(request, *args, **kwargs):
    """Init transaction model data, when seller pay the service fee."""
    app = kwargs.get('app')
    if app:
        transactions = models.Transaction.objects.filter(app_id=app.id, seller_id=request.user.id)
        if transactions:
            transaction = transactions[0]
            transaction.buyer = None
            transaction.price = None
            transaction.end_time = None
        else:
            transaction = models.Transaction()
            transaction.app = app
            transaction.seller = request.user
        transaction.status = 1
        transaction.save()
    return None


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def tradeNow(request, *args, **kwargs):
    """Trade app."""
    initParam = {}
    app = get_object_or_404(appModels.App, pk=kwargs.get('app_id'), publisher_id=request.user.id)
    user = get_object_or_404(User, pk=kwargs.get('buyer_id'))
    bid = get_object_or_404(bidModels.Bidding, pk=kwargs.get('bid_id'), buyer_id=user.id, app_id=app.id, status=1)
    initParam['app'] = app
    initParam['user'] = user
    initParam['bid'] = bid

    if request.method == 'POST':
        transactions = models.Transaction.objects.filter(app_id=app.id, seller_id=request.user.id)
        if transactions:
            transaction = transactions[0]
        else:
            transaction = models.Transaction()
            transaction.app = app
            transaction.seller = request.user
        transaction.status = 2
        transaction.buyer = user
        transaction.price = bid.price
        paid_expiry_date = string.atoi(common.getSystemParam(key='paid_expiry_date', default=7))
        transaction.end_time = datetime.datetime.now() + datetime.timedelta(days=paid_expiry_date)
        transaction.save()
        if app.status == 2:
            app.status = 3
            app.end_date = datetime.datetime.now()
            app.save()
        #Send the email of pay to buyer
        temp_name = 'buyer_trade_now'
        sub_params = [app.app_name]
        #TODO:Will make pay url later.
        temp_params = [user.username, ''.join(['http://127.0.0.1:8000/query/app-detail/', str(app.id)]),
                       app.app_name, 'http://127.0.0.1:8000/pay url........']
        recipient_list = [user.email]
        notificationViews.sendCommonEmail(request, temp_name=temp_name, sub_params=sub_params,
                                          temp_params=temp_params, recipient_list=recipient_list)
        return redirect(reverse('transaction:trade_action',
                                kwargs={'action': 'sell', 'app_id': app.id, 'user_id': request.user.id}))

    return render_to_response('transaction/trade_now.html', initParam, context_instance=RequestContext(request))


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def tradeAction(request, *args, **kwargs):
    """Query trade status."""
    initParam = {}
    user_id = string.atoi(kwargs.get('user_id'))
    action = kwargs.get('action')
    if 'sell' == action and user_id == request.user.id:
        transaction = get_object_or_404(models.Transaction, app_id=kwargs.get('app_id'), seller_id=user_id)
    elif 'buy' == action and user_id == request.user.id:
        transaction = get_object_or_404(models.Transaction, app_id=kwargs.get('app_id'), buyer_id=user_id)
    else:
        raise Http404

    initParam['action'] = action
    initParam['transaction'] = transaction
    if transaction.status == 2 or transaction.status == 3:
        initParam['time_remaining'] = time.mktime(time.strptime(str(transaction.end_time), '%Y-%m-%d %H:%M:%S'))
    elif transaction.status == 4:
        initParam['time_remaining'] = common.dateBefore(transaction.end_time)

    return render_to_response('transaction/trade_action.html', initParam, context_instance=RequestContext(request))


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def closedTransaction(request, *args, **kwargs):
    """Need update end_time to now."""
    return None