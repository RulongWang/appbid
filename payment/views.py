__author__ = 'Jarvis'

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

from django.shortcuts import render_to_response, HttpResponse, RequestContext, get_object_or_404, Http404, redirect
from django.views.decorators.csrf import csrf_protect
from django.db import transaction
from paypal.driver import PayPal
from payment import models
from paypal.driver import PayPal
from paypal.models import PayPalResponse
from paypal.utils import process_payment_request, process_refund_request


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def payment(request, *args, **kwargs):
    """Payment operation.
    :param request:
    :param args:
    :param kwargs:
    """

    #For saving the redirect url of the success or failed page, after payment done.
    initParam = kwargs.get('initParam')
    amount = initParam['amount']
    #Call PayPal api of payment
    p = PayPal()
    result = p.SetExpressCheckout(amount, "USD", "http://beta.appswalk.com/payment/paypal_return", "http://beta.appswalk.com/payment/paypal_cancel")
    if result:
        redirect_url = p.paypal_url()
        print('success_excute_setExpressCheckout')
        print(redirect_url)
        return HttpResponseRedirect(redirect_url)

    # initParam['success_url'] = 'payment/payment.html'
    # return 'success'
    # initParam['failed_url'] = 'payment/payment.html'
    # return 'failed'


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def paypalreturn(request, *args, **kwargs):
    """Payment operation."""

    token = request.GET.get('token')

    return render_to_response("payment/paypal_cancel.html", {'token',token}, context_instance=RequestContext(request))


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def paymentcancel(request, *args, **kwargs):
    """Payment operation."""
    initParam = {'payment': None}
    return render_to_response("payment/paypal_cancel.html", initParam, context_instance=RequestContext(request))