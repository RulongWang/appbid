__author__ = 'Jarvis'

import datetime
import string

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, RequestContext, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.db import transaction
from django.contrib.auth.models import User

from appbid import models as appModels
from transaction import models
from bid import models as bidModels
from utilities import common


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
    initParam['app'] = [app.id, app.app_name]
    initParam['user'] = [user.id, user.username]
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
        # return redirect

    return render_to_response('transaction/trade_now.html', initParam, context_instance=RequestContext(request))