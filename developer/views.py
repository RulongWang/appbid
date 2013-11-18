__author__ = 'rulongwang'

import json
import os
import logging
import string
import re

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render_to_response, HttpResponse, RequestContext, get_object_or_404, Http404, redirect
from django.views.decorators.csrf import csrf_protect
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.db import transaction
from django.conf import settings
from django.contrib.auth.models import User

from usersetting import models
from payment import models as paymentModels
from usersetting import forms
from notification import views as notificationViews
from credit import views as creditViews
from utilities import common

log = logging.getLogger('appbid')


@csrf_protect
def developer(request, *args, **kwargs):
    return render_to_response("developer/developer.html", context_instance=RequestContext(request))


