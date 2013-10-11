__author__ = 'Jarvis'

import time
import datetime
import string

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, RequestContext, redirect, get_object_or_404, Http404
from django.views.decorators.csrf import csrf_protect
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.db import transaction
from django.contrib.auth.models import User

from appbid import models as appModels
from transaction import models
from bid import models as bidModels
from utilities import common
from notification import views as notificationViews
from credit import views as creditViews


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
    return transaction


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
    transaction = None
    transactions = models.Transaction.objects.filter(app_id=app.id, seller_id=request.user.id)
    if transactions:
        transaction = transactions[0]
        initParam['transaction'] = transaction
        #Remind that seller has 7 days to trade now, if bid price is more than reserve price.
        if app.status == 3 and bid.price >= app.reserve_price and transaction.status == 1 and transaction.end_time:
            if transaction.end_time > datetime.datetime.now():
                initParam['time_remaining'] = time.mktime(time.strptime(str(transaction.end_time), '%Y-%m-%d %H:%M:%S'))
                initParam['is_expiry_date'] = False
            else:
                initParam['is_expiry_date'] = True

    if request.method == 'POST':
        if transaction and transaction.status != 1:
            initParam['error_msg'] = _('You have traded with buyer %(param)s, can not trade again.') % {'param': user.username}
        else:
            if transaction is None:
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
            transactionsLog.status = 2
            transactionsLog.seller = request.user
            transactionsLog.buyer = user
            transactionsLog.price = bid.price
            transactionsLog.save()
            #Update app status and end_date
            if app.status == 2:
                app.status = 3
                app.end_date = datetime.datetime.now()
                app.save()
            #Send the email of pay to buyer
            notificationViews.tradeNowInformBuyerPayEmail(request, app=app, user=user)

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
def closedTrade(request, *args, **kwargs):
    """Need update end_time to now."""
    initParam = {}
    transaction = get_object_or_404(models.Transaction, pk=kwargs.get('txn_id'), buyer_id=kwargs.get('buyer_id'))
    transaction.status = 4
    transaction.end_date = datetime.datetime.now()
    transaction.save()
    #Log transaction
    transactionsLog = models.TransactionLog()
    transactionsLog.app = transaction.app
    transactionsLog.status = 4
    transactionsLog.buyer = request.user
    transactionsLog.save()
    #Increase seller and buyer credit point
    point = common.getSystemParam(key='cp_closed_trade', default=50)
    creditViews.increaseCreditPoint(user=transaction.buyer, point=point)
    creditViews.increaseCreditPoint(user=transaction.seller, point=point)
    #Send email to seller and buyer
    notificationViews.closedTradeInform(request, transaction=transaction)

    initParam['transaction'] = transaction
    return render_to_response('transaction/trade_action.html', initParam, context_instance=RequestContext(request))


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
    initParam['app'] = app

    if request.method == 'POST':
        #Buyer credit point judge for bidding.
        min_cp = common.getSystemParam(key='min_cp_for_bid', default=50)
        cp = creditViews.getUserCreditPoint(user=request.user)
        if cp == -1 or cp < string.atoi(min_cp):
            initParam['error_msg'] = _('You can not buy, because your credit point is too low. You can pay credit point, after our verification.')
        else:
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
                transactionsLog.status = 3
                transactionsLog.buyer = request.user
                transactionsLog.price = app.one_price
                transactionsLog.save()
                #Send email to seller
                notificationViews.onePriceBuyInformSellerEmail(request, transaction=transaction)
                # TODO: return 'return to result page'
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
        transactionsLog.status = 3
        transactionsLog.buyer = request.user
        transactionsLog.price = transaction.price
        transactionsLog.save()
        #Send email to seller
        notificationViews.onePriceBuyInformSellerEmail(request, transaction=transaction)
    else:
        print "Log error message"
    return None