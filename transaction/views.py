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
from credit import models as creditModels
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
        #Log transaction
        transactionsLog = models.TransactionLog()
        transactionsLog.app = app
        transactionsLog.status = 1
        transactionsLog.seller = request.user
        transactionsLog.buyer = user
        transactionsLog.price = bid.price
        transactionsLog.save()

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


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def onePriceBuy(request, *args, **kwargs):
    """
        Buyer pay by clicking button 'Buy It Now with 10 USD' in app detail page.
        Note: url include app_id, and publisher_id, because of preventing user to cheat.
    """
    initParam = {}
    app_id = kwargs.get('app_id')
    publisher_id = kwargs.get('publisher_id')
    app = get_object_or_404(appModels.App, pk=app_id, publisher_id=publisher_id, status=2)

    if request.method == 'POST':
        #TODO: credit point < 50 can not buy.
        #TODO:invoke pay method
        #Maybe read the table of pay result.
        result = 'success'
        if result:
            transactions = models.Transaction.objects.filter(app_id=app.id, seller_id=publisher_id, status=1)
            if transactions:
                transaction = transactions[0]
            else:
                transaction = models.Transaction()
                transaction.app = app
                transaction.seller = request.user
            transaction.status = 3
            transaction.buyer = request.user
            transaction.price = app.one_price
            txn_expiry_date = string.atoi(common.getSystemParam(key='txn_expiry_date', default=15))
            transaction.end_time = datetime.datetime.now() + datetime.timedelta(days=txn_expiry_date)
            transaction.save()
            #Log transaction
            transactionsLog = models.TransactionLog()
            transactionsLog.app = app
            transactionsLog.status = 2
            transactionsLog.buyer = request.user
            transactionsLog.price = app.one_price
            transactionsLog.save()

            #Send email to seller
            temp_name = 'buyer_one_price_tell_seller'
            sub_params = [transaction.buyer.username, transaction.app.app_name]
            temp_params = [request.user.username, transaction.buyer.username, transaction.app.app_name]
            recipient_list = [transaction.app.publisher.username]
            notificationViews.sendCommonEmail(request, temp_name=temp_name, sub_params=sub_params,
                                              temp_params=temp_params, recipient_list=recipient_list)
        else:
            print "Log error message"
    return render_to_response('transaction/one_price_buy.html', initParam, context_instance=RequestContext(request))


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def buyerPay(request, *args, **kwargs):
    """Buyer pay, after seller begin to trade.."""
    app_id = kwargs.get('app_id')
    txn_id = kwargs.get('txn_id')
    #TODO:Can use or verify it later.
    token_id = kwargs.get('token')
    transaction = get_object_or_404(models.Transaction, pk=txn_id, app_id=app_id, buyer_id=request.user.id, status=2)

    #TODO:invoke pay method
    result = 'success'
    if result:
        transaction.status = 3
        txn_expiry_date = string.atoi(common.getSystemParam(key='txn_expiry_date', default=15))
        transaction.end_time = datetime.datetime.now() + datetime.timedelta(days=txn_expiry_date)
        transaction.save()
        #Log transaction
        transactionsLog = models.TransactionLog()
        transactionsLog.app = transaction.app
        transactionsLog.status = 2
        transactionsLog.buyer = request.user
        transactionsLog.price = transaction.price
        transactionsLog.save()

        #Send email to seller
        temp_name = 'buyer_paid_tell_seller'
        sub_params = [transaction.app.app_name]
        temp_params = [transaction.app.app_name, transaction.buyer.username]
        recipient_list = [transaction.app.publisher.username]
        notificationViews.sendCommonEmail(request, temp_name=temp_name, sub_params=sub_params,
                                          temp_params=temp_params, recipient_list=recipient_list)
    else:
        print "Log error message"
    return None