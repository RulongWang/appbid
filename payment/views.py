__author__ = 'Jarvis'

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.db import transaction
from paypal.driver import PayPal
from payment import models


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def payment(request, *args, **kwargs):
    """Payment operation."""

    #For saving the redirect url of the success or failed page, after payment done.
    initParam = kwargs.get('initParam')
    #Call PayPal api of payment
    p = PayPal()
    p.SetExpressCheckout("10.00", "USD", "http://localhost/return", "http://localhost/cancel")
    initParam['success_url'] = 'payment/payment.html'
    return 'success'
    # initParam['failed_url'] = 'payment/payment.html'
    # return 'failed'