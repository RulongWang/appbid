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




ec_sandbox_return_url = "http://beta.appswalk.com/payment/paypal_return"
ec_sandbox_cancel_url = "http://beta.appswalk.com/payment/paypal_cancel"

ap_sandbox_return_url = ""
ap_sandbox_cancel_url = " "
ap_sandbox_pay_url = "https://svcs.paypal.com/AdaptivePayments/Pay"
ap_sandbox_redirect_url = "https://www.sandbox.paypal.com/cgi-bin/webscr?cmd=_ap-payment&paykey=AP-1HL82102R3357810C"
ap_production_pay_url = ""


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
    result = p.SetExpressCheckout(amount, "USD",ec_sandbox_return_url , ec_sandbox_cancel_url)

    if result:
        redirect_url = p.paypal_url()
        print('success_excute_setExpressCheckout')
        print(redirect_url)
        return HttpResponseRedirect(redirect_url)
    else:
        return HttpResponseRedirect('/payment/paypal_cancel')

    # initParam['success_url'] = 'payment/payment.html'
    # return 'success'
    # initParam['failed_url'] = 'payment/payment.html'
    # return 'failed'



        #error message from paypal
        # ACK=notSuccess&TIMESTAMP=date/timeOfResponse&
        # CORRELATIONID=debuggingToken&VERSION=VersionNo&
        # BUILD=buildNumber&L_ERRORCODE0=errorCode&
        # L_SHORTMESSAGE0=shortMessage&
        # L_LONGMESSAGE0=longMessage&
        # L_SEVERITYCODE0=severityCode

@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def paypalreturn(request, *args, **kwargs):
    """Payment operation."""

    token = request.GET.get('token')
    payerid = request.GET.get('PayerID')

    if token is None:
        error = "Token is missing"
    else:
        p = PayPal()
        res_dict = p.GetExpressCheckoutDetailsInfo(ec_sandbox_return_url, ec_sandbox_cancel_url,token)
        state = p._get_value_from_qs(res_dict,"ACK")

        if not state in ["Success", "SuccessWithWarning"]:
            error = p._get_value_from_qs(res_dict, "L_SHORTMESSAGE0")
            return render_to_response("payment/paypal_error.html", {"token":token,"error":error}, context_instance=RequestContext(request))

        # payerid = p._get_value_from_qs(res_dict,"PayerID")


        return render_to_response("payment/paypal_return.html", {"token":token,"payerid":payerid,"res_dict":res_dict}, context_instance=RequestContext(request))


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def start_paypal_ap(request, *args, **kwargs):
    """Payment operation."""
    p = PayPal()
    reuslt = p.setAPCall('returnUrl','cancelUrl','pay')
    paykey = request.GET.get('Paykey')

    if paykey is None:
        error = "paykey is missing"
    else:
        p = PayPal()
        return render_to_response("payment/paypal_return.html", {"token":paykey}, context_instance=RequestContext(request))





@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def paypal_ap_return(request, *args, **kwargs):
    """Payment operation."""
    print request.GET
    print '*****************'
    print request.POST
    print args
    print '============='
    print kwargs
    print 'xxxxxx'
    print request
    # paykey = request.GET.get('Paykey')
    #
    # if paykey is None:
    #     error = "paykey is missing"
    # else:
    #     p = PayPal()
    #
    return render_to_response("payment/paypal_return.html", {"token":'test'}, context_instance=RequestContext(request))




@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def paypal_docheckout(request, *args, **kwargs):
 # perform GET

        token   = request.GET.get("token")
        payerid = request.GET.get("PayerID")

        # charge from PayPal

        # get the order id by token

        result, response = process_payment_request('40', 'USD', token, payerid)
        # process the result
        if not result:
            # show the error message (comes from PayPal API) and redirect user to the error page
            #if request.user.is_authenticated():
                #request.user.message_set.create(message = _("Amount %s has not been charged, server error is '%s'" % (amount, response.error)))
            #return HttpResponseRedirect(error_url)

        # Now we are gone, redirect user to success page
        #if request.user.is_authenticated():
            #request.user.message_set.create(message = _("Amount %s has been successfully charged, your transaction id is '%s'" % (amount, response.trans_id)))


            return render_to_response("payment/paypal_failed.html", context_instance = RequestContext(request))
        else:
            return render_to_response("payment/paypal_success.html", context_instance = RequestContext(request))


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def paymentcancel(request, *args, **kwargs):
    """Payment operation."""
    initParam = {'payment': None}
    return render_to_response("payment/paypal_cancel.html", initParam, context_instance=RequestContext(request))