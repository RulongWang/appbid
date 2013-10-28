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
from django.conf import settings


if  getattr(settings, "PAYPAL_DEBUG", False):
    EC_RETURNURL    = "https://beta.appswalk.com/payment/paypal_return"
    EC_CANCELURL = "https://beta.appswalk.com/payment/paypal_cancel"
    AP_RETURNURL    = "https://beta.appswalk.com/payment/paypal_ap_return"
    AP_CANCELURL = "https://beta.appswalk.com/payment/paypal_cancel"

    AP_REDIRECTURL = "https://www.sandbox.paypal.com/cgi-bin/webscr?cmd=_ap-payment&paykey="


else:
    EC_RETURNURL    = "https://www.appswalk.com/payment/paypal_return"
    EC_CANCELURL = "https://www.appswalk.com/payment/paypal_cancel"
    AP_RETURNURL    = "https://www.appswalk.com/payment/paypal_ap_return"
    AP_CANCELURL = "https://www.appswalk.com/payment/paypal_cancel"
    AP_REDIRECTURL = "https://www.paypal.com/webscr?cmd=_ap-payment&paykey="





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
    amount = initParam.get('amount')
    amount = 400
    #Call PayPal api of payment
    p = PayPal()
    #Parameters needed:  1, amount  2, currency  ,3 EC_RETURNRUL 4, EC_CANCELURL 5,
    result = p.SetExpressCheckout(amount, "USD", EC_RETURNURL, EC_CANCELURL, initParam=kwargs)

    if result:
        redirect_url = p.paypal_url()
        print('success_excute_setExpressCheckout')
        print(redirect_url)
        print p.token
        return HttpResponseRedirect(redirect_url)
    else:
        print p.apierror
        print p.setexpresscheckouterror
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
        res_dict = p.GetExpressCheckoutDetailsInfo(EC_RETURNURL, EC_CANCELURL,token)
        state = p._get_value_from_qs(res_dict,"ACK")

        if not state in ["Success", "SuccessWithWarning"]:
            error = p._get_value_from_qs(res_dict, "L_SHORTMESSAGE0")
            return render_to_response("payment/paypal_error.html", {"token":token,"error":error}, context_instance=RequestContext(request))

        # payerid = p._get_value_from_qs(res_dict,"PayerID")

        #Do something after payment.
        executeMethod = kwargs.pop('executeMethod', None)
        if executeMethod:
            result = executeMethod(request, kwargs=kwargs)
            if result:
                print result
            else:
                #business id is not correct. or return error page.
                print 'the payment is not correct. Please check your operation or contact customer service.'

        return render_to_response("payment/paypal_return.html", {"token":token,"payerid":payerid,"res_dict":res_dict}, context_instance=RequestContext(request))


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def start_paypal_ap(request, *args, **kwargs):
    """Payment operation."""
    p = PayPal()
    result = p.setAPCall(AP_RETURNURL, AP_CANCELURL, 'pay')

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

    #Do something after user payed.
    executeMethod = kwargs.pop('executeMethod', None)
    if executeMethod:
        result = executeMethod(request, kwargs=kwargs)
        if result:
            print result
        else:
            #transaction is not correct. or return error page.
            print 'the pay is not correct. Please check your operation or contact customer service.'

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