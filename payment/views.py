__author__ = 'Jarvis'

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, HttpResponse, RequestContext, get_object_or_404, Http404, redirect
from django.views.decorators.csrf import csrf_protect
from django.db import transaction

from payment import models


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def payment(request, *args, **kwargs):
    """Payment."""
    initParam = {}

    return render_to_response("payment/payment.html", initParam, context_instance=RequestContext(request))