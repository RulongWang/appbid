__author__ = 'Jarvis'

import time
import datetime
import string
import logging
import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, RequestContext, redirect, get_object_or_404, Http404, HttpResponse
from django.views.decorators.csrf import csrf_protect
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.db import transaction
from django.contrib.auth.models import User

from appbid import settings
from appbid import models as appModels
from payment import models as paymentModels
from transaction import models
from bid import models as bidModels
from utilities import common
from notification import views as notificationViews
from credit import views as creditViews
from payment import views as paymentViews

log = logging.getLogger('appbid')


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def initTransaction(request, *args, **kwargs):
    """Init transaction model data, when seller pay the service fee."""
    app = kwargs.get('app')
    if app:
        transactions = models.Transaction.objects.filter(app_id=app.id, seller_id=request.user.id, is_active=True)
        if transactions:
            transaction = transactions[0]
            transaction.buyer = None
            transaction.price = None
            transaction.end_time = None
            transaction.buy_type = None
            transaction.seller_price = None
            transaction.appswalk_price = None
            transaction.gateway = None
            transaction.buyer_account = None
            transaction.seller_account = None
            transaction.appswalk_account = None
            transaction.pay_key = None
        else:
            transaction = models.Transaction()
            transaction.app = app
            transaction.seller = request.user
            transaction.is_active = True
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
    transactions = models.Transaction.objects.filter(app_id=app.id, seller_id=request.user.id, is_active=True)
    if transactions:
        transaction = transactions[0]
    else:
        transaction = models.Transaction()
        transaction.app = app
        transaction.status = 1
        transaction.seller = request.user
        transaction.is_active = True
        transaction.save()
    #Remind that seller has 7 days to trade now, if bid price is more than reserve price.
    cur_time = datetime.datetime.now()
    if transaction.status == 1 and app.status != 1 and app.end_date <= cur_time and bid.price >= app.reserve_price:
        if transaction.end_time is None:
            paid_expiry_date = string.atoi(common.getSystemParam(key='sell_expiry_date', default=7))
            transaction.end_time = app.end_date + datetime.timedelta(days=paid_expiry_date)
            transaction.save()
        if transaction.end_time > cur_time:
            initParam['time_remaining'] = time.mktime(time.strptime(str(transaction.end_time), '%Y-%m-%d %H:%M:%S'))
            initParam['is_expiry_date'] = False
        else:
            initParam['is_expiry_date'] = True
    initParam['transaction'] = transaction

    if request.method == 'POST':
        if transaction and transaction.status != 1:
            initParam['error_msg'] = _('You have traded with buyer %(param)s, can not trade again.') % {'param': user.username}
        else:
            if transaction is None:
                transaction = models.Transaction()
                transaction.app = app
                transaction.seller = request.user
                transaction.is_active = True
            transaction.status = 2
            transaction.buyer = user
            transaction.price = bid.price
            paid_expiry_date = string.atoi(common.getSystemParam(key='paid_expiry_date', default=7))
            transaction.end_time = cur_time + datetime.timedelta(days=paid_expiry_date)
            transaction.buy_type = 2
            transaction.save()
            #Log transaction
            transactionsLog = models.TransactionLog()
            transactionsLog.transaction = transaction
            transactionsLog.app = transaction.app
            transactionsLog.status = transaction.status
            transactionsLog.seller = transaction.seller
            transactionsLog.buyer = transaction.buyer
            transactionsLog.price = transaction.price
            transactionsLog.buy_type = transaction.buy_type
            transactionsLog.save()
            #Update app status and end_date
            if app.status == 2:
                app.status = 3
                app.end_date = cur_time
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
    app_id = kwargs.get('app_id')
    action = kwargs.get('action')
    if 'sell' == action and user_id == request.user.id:
        transaction = get_object_or_404(models.Transaction, app_id=app_id, seller_id=user_id, is_active=True)
    elif 'buy' == action and user_id == request.user.id:
        transaction = get_object_or_404(models.Transaction, app_id=app_id, buyer_id=user_id)
        if transaction.status == 2:
            token = common.getToken(key='token_length', default=30)
            initParam['pay_url'] = '/'.join([common.getHttpHeader(request), 'transaction/buyer-pay', str(app_id), str(transaction.id), token])
    else:
        raise Http404

    support_user = common.getSystemParam(key='support_user', default='appswalk')
    support_users = models.User.objects.filter(username=support_user)
    if support_users:
        initParam['support_user'] = support_users[0]
    else:
        log.error(_('Support user account does not exist.'))

    initParam['transaction'] = transaction
    if transaction.status == 2 or transaction.status == 3:
        if transaction.end_time > datetime.datetime.now():
            initParam['time_remaining'] = time.mktime(time.strptime(transaction.end_time.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S'))
        else:
            initParam['time_remaining'] = "Deal Closed"
            initParam['paid_expiry'] = True
        if tradeOperation(request, transaction=transaction, initParam=initParam):
            return redirect(request.path)
    elif transaction.status == 4:
        initParam['time_remaining'] = common.dateBefore(transaction.end_time)

        initParam['seller_txn'] = creditViews.getAppraisement(user_id=transaction.seller.id, txn_id=transaction.id)
        initParam['buyer_txn'] = creditViews.getAppraisement(user_id=transaction.buyer.id, txn_id=transaction.id)
        if creditViews.createAppraisement(request, initParam=initParam):
            return redirect(request.path)

    return render_to_response('transaction/trade_action.html', initParam, context_instance=RequestContext(request))


def tradeOperation(request, *args, **kwargs):
    initParam = kwargs.get('initParam')
    transaction = kwargs.get('transaction')
    if transaction and request.method == 'POST':
        delivery = request.POST.get('delivery')
        if delivery and delivery == 'confirm_delivery':
            if transaction.status == 3:
                transaction.status = 4
                transaction.end_time = datetime.datetime.now()
                transaction.save()
                #Log transaction
                transactionsLog = models.TransactionLog()
                transactionsLog.transaction = transaction
                transactionsLog.app = transaction.app
                transactionsLog.status = transaction.status
                transactionsLog.buyer = transaction.buyer
                transactionsLog.save()
                #Send email to seller and buyer
                notificationViews.closedTradeInform(transaction=transaction)
                return transaction
            else:
                initParam['error_msg'] = _('Transaction can not be confirmed delivery.')
                log.error(_('Transaction: %(param1)s, status: %(param2)s can not confirm delivery.')
                      % {'param1': transaction.id, 'param2': transaction.status})
        #TODO:if no complain, then increase credit point.
        #Increase seller and buyer credit point
        # point = common.getSystemParam(key='cp_closed_trade', default=50)
        # creditViews.increaseCreditPoint(user=transaction.buyer, point=point)
        # creditViews.increaseCreditPoint(user=transaction.seller, point=point)
    return None


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def closedTrade(request, *args, **kwargs):
    """Need update end_time to now."""
    initParam = {}
    transaction = get_object_or_404(models.Transaction, pk=kwargs.get('txn_id'), buyer_id=kwargs.get('buyer_id'), is_active=True)
    transaction.status = 4
    transaction.end_date = datetime.datetime.now()
    transaction.save()
    #Log transaction
    transactionsLog = models.TransactionLog()
    transactionsLog.transaction = transaction
    transactionsLog.app = transaction.app
    transactionsLog.status = transaction.status
    transactionsLog.buyer = transaction.buyer
    transactionsLog.save()
    #Increase seller and buyer credit point
    point = common.getSystemParam(key='cp_closed_trade', default=50)
    creditViews.increaseCreditPoint(user=transaction.buyer, point=point)
    creditViews.increaseCreditPoint(user=transaction.seller, point=point)
    #Send email to seller and buyer
    notificationViews.closedTradeInform(transaction=transaction)

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

    transactions = models.Transaction.objects.filter(app_id=app.id, seller_id=publisher_id, buyer_id=request.user.id, status=1)
    if transactions:
        transaction = transactions[0]
    else:
        transaction = models.Transaction()
        transaction.app = app
        transaction.seller = app.publisher
        transaction.status = 1
        transaction.is_active = False
        transaction.buyer = request.user
        transaction.price = app.one_price
        transaction.buy_type = 1
        paid_expiry_date = string.atoi(common.getSystemParam(key='paid_expiry_date', default=7))
        transaction.end_time = datetime.datetime.now() + datetime.timedelta(days=paid_expiry_date)
        transaction.save()

        #Log transaction
        transactionsLog = models.TransactionLog()
        transactionsLog.transaction = transaction
        transactionsLog.app = transaction.app
        transactionsLog.status = transaction.status
        transactionsLog.buyer = transaction.buyer
        transactionsLog.price = transaction.price
        transactionsLog.buy_type = transaction.buy_type
        transactionsLog.save()

    initParam['transaction'] = transaction
    initParam['page_source'] = 'one-price'
    if transaction.end_time > datetime.datetime.now():
        initParam['time_remaining'] = time.mktime(time.strptime(transaction.end_time.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S'))
    else:
        initParam['time_remaining'] = "Deal Closed"
        initParam['paid_expiry'] = True

    if request.method == 'POST':
        #Buyer credit point judge for bidding.
        min_cp = common.getSystemParam(key='min_cp_for_bid', default=50)
        cp = creditViews.getUserCreditPoint(user=request.user)
        if cp == -1 or cp < string.atoi(min_cp):
            initParam['error_msg'] = _('You are allowed to buy, because your credit points is too low.')
        else:
            #Buyser pay for app.
            txn_fee_pct = string.atof(common.getSystemParam(key='txn_fee_pct', default=0.01))
            initParam['currency'] = app.currency.currency
            initParam['appsWalk_account'] = settings.APPSWALK_ACCOUNT
            initParam['gateway'] = 'paypal'
            gateways = paymentModels.Gateway.objects.filter(name__iexact=initParam.get('gateway'))
            acceptGateways = paymentModels.AcceptGateway.objects.filter(user_id=transaction.seller.id, type_id=gateways[0].id, is_active=True)
            initParam['seller_account'] = acceptGateways[0].value
            initParam['appsWalk_amount'] = app.one_price * txn_fee_pct
            initParam['seller_amount'] = app.one_price * (1 - txn_fee_pct)
            initParam['txn_id'] = transaction.id
            #The needed operation method in pay.
            initParam['executeMethod'] = updateTransaction
            #The back page, when pay has error.
            if request.session.get('back_page', None):
                del request.session['back_page']
            if request.session.get('back_page_msg', None):
                del request.session['back_page_msg']
            request.session['back_page'] = '/'.join([common.getHttpHeader(request), 'query/app-detail', str(app.id)])
            request.session['back_page_msg'] = 'App Detail'
            #The success return page, when pay finish.
            if request.session.get('success_page', None):
                del request.session['success_page']
            if request.session.get('success_page_msg', None):
                del request.session['success_page_msg']
            request.session['success_page'] = '/'.join([common.getHttpHeader(request), 'transaction/trade-action/buy', str(app.id), str(request.user.id)])
            request.session['success_page_msg'] = 'Trade Action'
            return paymentViews.pay(request, initParam=initParam)
    return render_to_response('transaction/one_price_buy.html', initParam, context_instance=RequestContext(request))


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def buyerPay(request, *args, **kwargs):
    """Buyer pay, after seller begin to trade."""
    initParam = {}
    app_id = kwargs.get('app_id')
    txn_id = kwargs.get('txn_id')
    #TODO:Can use or verify it later.
    token_id = kwargs.get('token')
    transaction = get_object_or_404(models.Transaction, pk=txn_id, app_id=app_id, buyer_id=request.user.id, status=2, is_active=True)
    app = transaction.app

    #Buyser pay for app.
    txn_fee_pct = string.atof(common.getSystemParam(key='txn_fee_pct', default=0.01))
    initParam['currency'] = app.currency.currency
    initParam['appsWalk_account'] = settings.APPSWALK_ACCOUNT
    initParam['gateway'] = 'paypal'
    gateways = paymentModels.Gateway.objects.filter(name__iexact=initParam.get('gateway'))
    acceptGateways = paymentModels.AcceptGateway.objects.filter(user_id=transaction.seller.id, type_id=gateways[0].id, is_active=True)
    initParam['seller_account'] = acceptGateways[0].value
    initParam['appsWalk_amount'] = transaction.price * txn_fee_pct
    initParam['seller_amount'] = transaction.price * (1 - txn_fee_pct)
    initParam['txn_id'] = transaction.id
    #The needed operation method in pay.
    initParam['executeMethod'] = updateTransaction
    #The back page, when pay has error.
    if request.session.get('back_page', None):
        del request.session['back_page']
    if request.session.get('back_page_msg', None):
        del request.session['back_page_msg']
    url = '/'.join([common.getHttpHeader(request), 'transaction/trade-action/buy', str(app.id), str(request.user.id)])
    request.session['back_page'] = url
    request.session['back_page_msg'] = 'Trade Action'
    #The success return page, when pay finish.
    if request.session.get('success_page', None):
        del request.session['success_page']
    if request.session.get('success_page_msg', None):
        del request.session['success_page_msg']
    request.session['success_page'] = url
    request.session['success_page_msg'] = 'Trade Action'
    return paymentViews.pay(request, initParam=initParam)


def updateTransaction(*args, **kwargs):
    """The operation after buyer payed successfully."""
    initParam = kwargs.get('initParam')
    txn_id = initParam.get('txn_id')
    pay_key = initParam.get('pay_key')
    gateway = initParam.get('gateway')
    if txn_id and pay_key and gateway:
        transactions = models.Transaction.objects.filter(pk=txn_id)
        if transactions:
            gateways = paymentModels.Gateway.objects.filter(name__iexact=gateway)
            if gateways:
                transactions[0].gateway = gateways[0]
                transactions[0].pay_key = pay_key
                transactions[0].save()
                log.info(_('Transaction with id %(param1)s set pay_key to %(param2)s, gateway to %(param3)s.')
                         % {'param1': txn_id, 'param2': pay_key, 'param3': gateway})
                return transactions[0]
            else:
                log.error(_('PayKey: %(param1)s, Transaction ID: %(param2)s. Gateway %(param3)s no exists.')
                      % {'param1': pay_key, 'param2': txn_id, 'param1': gateway})
        else:
            log.error(_('PayKey: %(param1)s, Transaction with id %(param2)s no exists.')
                      % {'param1': pay_key, 'param2': txn_id})
    else:
        log.error(_('Transaction ID or PayKey or Gateway no exists.'))
    return None


def checkTransaction(request, *args, **kwargs):
    """Check and get transaction information."""
    initParam = kwargs.get('initParam')
    pay_key = initParam.get('pay_key')
    gateway = initParam.get('gateway')
    if pay_key and gateway:
        gateways = paymentModels.Gateway.objects.filter(name__iexact=gateway)
        if gateways:
            transactions = models.Transaction.objects.filter(buyer_id=request.user.id,
                                                             pay_key=pay_key, gateway_id=gateways[0].id)
            if transactions:
                return transactions[0]
    return None


def executePay(*args, **kwargs):
    """The operation after buyer payed successfully."""
    initParam = kwargs.get('initParam')
    txn_id = initParam.get('transaction_id')
    pay_key = initParam.get('pay_key')
    if txn_id and pay_key:
        transactions = models.Transaction.objects.filter(pk=txn_id, pay_key=pay_key)
        if transactions:
            initParam['transaction'] = transactions[0]
            if transactions[0].status == 1:
                return executeOnePriceBuy(initParam=initParam)
            elif transactions[0].status == 2:
                return executeBuyerPay(initParam=initParam)
            else:
                log.error(_('The transaction with id %(param1)s status %(param2)s should be payed with buyer %(param3)s.')
                          % {'param1': txn_id, 'param2': transactions[0].status, 'param3': transactions[0].buyer.username})
        else:
            log.error(_('The transaction with id %(param1)s does not exist.') % {'param1': txn_id})
    else:
        log.error('Transaction_ID or pay_key no exists.')
    return None


def executeOnePriceBuy(*args, **kwargs):
    """The operation of one price buy, after buyer payed successfully."""
    initParam = kwargs.get('initParam')
    transaction = initParam.get('transaction')
    if transaction:
        transaction.status = 3
        transaction.is_active = True
        txn_expiry_date = string.atoi(common.getSystemParam(key='txn_expiry_date', default=15))
        transaction.end_time = datetime.datetime.now() + datetime.timedelta(days=txn_expiry_date)
        transaction.buyer_account = initParam.get('buyer_account')
        acceptGateways = paymentModels.AcceptGateway.objects.filter(user_id=transaction.seller.id, type_id=transaction.gateway.id, is_active=True)
        transaction.seller_account = acceptGateways[0].value
        transaction.appswalk_account = settings.APPSWALK_ACCOUNT
        txn_fee_pct = string.atof(common.getSystemParam(key='txn_fee_pct', default=0.01))
        transaction.appswalk_price = transaction.price * txn_fee_pct
        transaction.seller_price = transaction.price * (1 - txn_fee_pct)
        transaction.save()
        #Log transaction
        transactionsLog = models.TransactionLog()
        transactionsLog.transaction = transaction
        transactionsLog.app = transaction.app
        transactionsLog.status = transaction.status
        transactionsLog.buyer = transaction.buyer
        transactionsLog.price = transaction.price
        transactionsLog.buyer_account = transaction.buyer_account
        transactionsLog.seller_account = transaction.seller_account
        transactionsLog.appswalk_account = transaction.appswalk_account
        transactionsLog.gateway = transaction.gateway
        transactionsLog.appswalk_price = transaction.appswalk_price
        transactionsLog.seller_price = transaction.seller_price
        transactionsLog.pay_key = transaction.pay_key
        transactionsLog.save()
        #Update app status and end_date.
        app = transaction.app
        if app.status == 2:
            app.status = 3
            app.end_date = datetime.datetime.now()
            app.save()

        #Send email to seller
        notificationViews.onePriceBuyInformSellerEmail(transaction=transaction)

        log.info(_('The transaction of one price buy with id %(param1)s is payed by %(param2)s.')
                 % {'param1': transaction.id, 'param2': transaction.buyer.username})
        return transaction
    return None


def executeBuyerPay(*args, **kwargs):
    """The operation, after buyer payed successfully."""
    initParam = kwargs.get('initParam')
    transaction = initParam.get('transaction')
    if transaction:
        transaction.status = 3
        txn_expiry_date = string.atoi(common.getSystemParam(key='txn_expiry_date', default=15))
        transaction.end_time = datetime.datetime.now() + datetime.timedelta(days=txn_expiry_date)
        transaction.buyer_account = initParam.get('buyer_account')
        acceptGateways = paymentModels.AcceptGateway.objects.filter(user_id=transaction.seller.id, type_id=transaction.gateway.id, is_active=True)
        transaction.seller_account = acceptGateways[0].value
        transaction.appswalk_account = settings.APPSWALK_ACCOUNT
        txn_fee_pct = string.atof(common.getSystemParam(key='txn_fee_pct', default=0.01))
        transaction.appswalk_price = transaction.price * txn_fee_pct
        transaction.seller_price = transaction.price * (1 - txn_fee_pct)
        transaction.save()
        #Log transaction
        transactionsLog = models.TransactionLog()
        transactionsLog.transaction = transaction
        transactionsLog.app = transaction.app
        transactionsLog.status = transaction.status
        transactionsLog.buyer = transaction.buyer
        transactionsLog.price = transaction.price
        transactionsLog.buyer_account = transaction.buyer_account
        transactionsLog.seller_account = transaction.seller_account
        transactionsLog.appswalk_account = transaction.appswalk_account
        transactionsLog.buy_type = transaction.buy_type
        transactionsLog.gateway = transaction.gateway
        transactionsLog.appswalk_price = transaction.appswalk_price
        transactionsLog.seller_price = transaction.seller_price
        transactionsLog.pay_key = transaction.pay_key
        transactionsLog.save()

        #Send email to seller
        notificationViews.buyerPayInformSellerEmail(transaction=transaction)

        log.info(_('The transaction with id %(param1)s is payed by %(param2)s.')
                 % {'param1': transaction.id, 'param2': transaction.buyer.username})
        return transaction
    return None


def jobCheckPayComplete(*args, **kwargs):
    """Check whether buyer pay is complete in case that buyer close the page after pay by paypal.
        In the case, payReturn (url 'paypal_ap_return') is not executed.
    """
    #Just check pay before 5 min.
    do_time = datetime.datetime.now() + datetime.timedelta(0, -300)
    transactions = models.Transaction.objects.filter(status=2, create_time__lte=do_time, pay_key__isnull=False,
                                                     gateway_id__isnull=False, is_active=True)
    for transaction in transactions:
        paymentViews.checkPayComplete(transaction=transaction, executeMethod=executePay)


def remindBuyerPay(request, *args, **kwargs):
    """Seller click button to remind buyer to pay."""
    data = {}
    try:
        dict = request.POST
    except:
        dict = request.GET
    txn_id = dict.get('txn_id')
    transactions = models.Transaction.objects.filter(pk=txn_id, seller_id=request.user.id)
    if transactions:
        notificationViews.remindBuyerPay(request, transaction=transactions[0])
        data['ok'] = 'true'
    else:
        data['ok'] = 'false'
    return HttpResponse(json.dumps(data), mimetype=u'application/json')
