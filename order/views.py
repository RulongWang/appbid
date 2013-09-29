__author__ = 'Jarvis'

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, HttpResponse, RequestContext, get_object_or_404, Http404, redirect
from django.views.decorators.csrf import csrf_protect
from django.utils.translation import ugettext as _
from django.db import transaction
from django.contrib.auth.models import User

from appbid import models as appModels
from payment import views as paymentViews
from order import models, forms


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def checkout(request, *args, **kwargs):
    """checkout."""
    initParam = {}
    app_id = kwargs.get('app_id')
    service_id = kwargs.get('service_id')
    service_sn = kwargs.get('service_sn')
    user = get_object_or_404(User, pk=request.user.id, username=request.user.username)
    app = get_object_or_404(appModels.App, pk=app_id, publisher_id=user.id)
    serviceDetail = get_object_or_404(models.ServiceDetail, pk=service_id, app_id=app_id, sn=service_sn)

    initParam['currency'] = app.currency.currency
    acceptGateways = user.acceptgateway_set.filter(is_active=True, is_default=True)
    initParam['acceptgateway'] = acceptGateways[0]

    if request.method == "POST":
        serviceDetailForm = forms.ServiceDetailForm(request.POST, instance=serviceDetail)
        #Payment for service detail
        payment = paymentViews.payment(request)
        if payment == 'success':
            # serviceDetail = serviceDetailForm.save(commit=False)
            #TODO:TODO later...
            return render_to_response("payment/payment.html", initParam, context_instance=RequestContext(request))
        else:
            initParam['order_error'] = _('Payment failed.')
    else:
        serviceDetailForm = forms.ServiceDetailForm(instance=serviceDetail)
    initParam['serviceDetailForm'] = serviceDetailForm

    return render_to_response("order/checkout.html", initParam, context_instance=RequestContext(request))