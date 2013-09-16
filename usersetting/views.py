__author__ = 'rulongwang'

import json
import os

from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, HttpResponse, RequestContext, HttpResponseRedirect, get_object_or_404, Http404
from django.views.decorators.csrf import csrf_protect
from django.utils.translation import ugettext as _
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.models import User
from usersetting import models
from usersetting import forms
from order import models as orderModels
from payment import models as paymentModels


@csrf_protect
def loginView(request, *args, **kwargs):
    initParam = {}
    user = authenticate(username=request.POST.get('username'), password=request.POST.get('password'))
    redirect_to = request.POST.get('next', None)
    redirect_urls = (None, '', '/usersetting/logout/', '/usersetting/register/', '/usersetting/register-active/')
    for url in redirect_urls:
        if redirect_to == url or redirect_to.startswith(str(url)):
            redirect_to = '/'
            break
    if user:
        if user.is_active:
            login(request, user)
            return HttpResponseRedirect(redirect_to)
        else:
            initParam['login_error'] = _('%(name)s is not active. Please active it by %(email)s.') % {'name': user.username, 'email': user.email}
    else:
        initParam['login_error'] = _('username or password is not correct.')
    initParam['user_name'] = request.POST.get('username')
    return render_to_response("usersetting/login.html", initParam, context_instance=RequestContext(request))


@csrf_protect
def logoutView(request, *args, **kwargs):
    logout(request)
    redirect_to = '/'
    return render_to_response('usersetting/login.html', {"redirect_to": redirect_to}, context_instance=RequestContext(request))


@csrf_protect
def authHome(request, *args, **kwargs):
    redirect_to = request.GET.get('next', '/')
    return render_to_response("usersetting/login.html", {'redirect_to': redirect_to}, context_instance=RequestContext(request))


@csrf_protect
def register(request, *args, **kwargs):
    """user register method"""
    initParam = {}
    registerForm = forms.RegisterForm()
    if request.method == "POST":
        registerForm = forms.RegisterForm(request.POST)
        if registerForm.is_valid():
            username = (registerForm.cleaned_data["username"]).strip()
            email = (registerForm.cleaned_data["email"]).strip()
            password = (registerForm.cleaned_data["password"]).strip()
            if models.User.objects.filter(Q(username=username) | Q(email=email)):
                initParam['register_error'] = _('%(name)s or %(email)s has been used.') % {'name': username, 'email': email}
            else:
                user = User.objects.create_user(username, email, password)
                if user is not None:
                    user.is_active = False
                    user.save()
                    #Init some setting for the user
                    privateSet = models.UserPrivateSetting()
                    privateSet.user = user
                    userPrivateItem = models.UserPrivateItem.objects.filter(key='is_bid_approved')
                    if userPrivateItem:
                        privateSet.user_private_item = userPrivateItem[0]
                        privateSet.value = False
                        privateSet.save()
                    return HttpResponseRedirect("".join(["/usersetting/register-active/", user.username, '/', str(user.id)]))
                else:
                    initParam['register_error'] = _('Register failed, please try again.')
    initParam['register_form'] = registerForm
    return render_to_response("usersetting/register.html", initParam, context_instance=RequestContext(request))


def ajaxUserVerified(request, *args, **kwargs):
    """Verified user name or email in register user."""
    data = {}
    try:
        dict = request.POST
    except:
        dict = request.GET
    try:
        if dict.get('username') is not None:
            if models.User.objects.filter(username=dict.get('username')):
                data['message'] = _('%(name)s has been used.') % {'name': dict.get('username')}
                raise
            else:
                data['message'] = _('%(name)s is valid.') % {'name': dict.get('username')}
        if dict.get('email') is not None:
            if models.User.objects.filter(email=dict.get('email')):
                data['message'] = _('%(email)s has been used.') % {'email': dict.get('email')}
                raise
            else:
                data['message'] = _('%(email)s is valid.') % {'email': dict.get('email')}
        data['ok'] = 'true'
    except:
        data['ok'] = 'false'
    return HttpResponse(json.dumps(data), mimetype=u'application/json')


@csrf_protect
def registerActive(request, *args, **kwargs):
    initParam = {}
    if kwargs['username'] and kwargs['pk']:
        user = get_object_or_404(models.User, pk=kwargs['pk'], username=kwargs['username'])
        initParam['email'] = user.email
        #Send the active email.
        #TODO:do it later.
    return render_to_response("usersetting/register_active.html", initParam, context_instance=RequestContext(request))


def accountActiveByEmail(request, *args, **kwargs):
    """Active the usersetting by user clicking the active link."""
    return None

def _login(request, username, password):
    pass


def myprofile(request):
    pass


@csrf_protect
@login_required(login_url='/usersetting/home/')
def userDetail(request, *args, **kwargs):
    """Save user detail info."""
    initParam = {}
    user = get_object_or_404(models.User, pk=request.user.id, username=request.user.username)
    userDetails = models.UserDetail.objects.filter(user_id=user.id)
    if userDetails:
        userDetail = userDetails[0]
    else:
        userDetail = models.UserDetail()
        userDetail.user = user
        userDetail.save()
    detailForm = forms.UserDetailForm(instance=userDetail)
    if request.method == "POST":
        detailForm = forms.UserDetailForm(request.POST, instance=userDetail)
        if detailForm.is_valid():
            detailForm.save()
            initParam['account_msg'] = _('The account detail has been updated.')
    initParam['form'] = detailForm
    return render_to_response("usersetting/account_setting.html", initParam, context_instance=RequestContext(request))


def paymentAccount(request, *args, **kwargs):
    payment_accounts = paymentModels.AcceptGateway.objects.all()
    return render_to_response("usersetting/accept_payment.html",{"payment_accounts":payment_accounts},
                        context_instance=RequestContext(request))


def userPublicProfile(request, *args, **kwargs):
    """Save user public profile."""
    initParam = {}
    user = get_object_or_404(models.User, pk=request.user.id, username=request.user.username)
    userPublicProfiles = models.UserPublicProfile.objects.filter(user_id=user.id)
    if userPublicProfiles:
        userPublicProfile = userPublicProfiles[0]
    else:
        userPublicProfile = models.UserPublicProfile()
        userPublicProfile.user = user
        userPublicProfile.gender = 3
        userPublicProfile.save()
    userPublicProfileForm = forms.UserPublicProfileForm(instance=userPublicProfile)
    if request.method == "POST":
        userPublicProfileForm = forms.UserPublicProfileForm(request.POST, instance=userPublicProfile)
        if userPublicProfileForm.is_valid():
            userPublicProfile = userPublicProfileForm.save(commit=False)
            thumbnail = request.FILES.get('thumbnail')
            if thumbnail:
                path = '/'.join([settings.MEDIA_ROOT, str(user.id)])
                if os.path.exists(path) is False:
                    os.makedirs(path)
                if userPublicProfile.thumbnail:
                    path = '/'.join([settings.MEDIA_ROOT, str(userPublicProfile.thumbnail)])
                    if os.path.exists(path):
                        os.remove(path)
                userPublicProfile.thumbnail = thumbnail
                userPublicProfileForm = forms.UserPublicProfileForm(instance=userPublicProfile)
            userPublicProfile.save()
            initParam['account_msg'] = _('The public profile has been updated.')
    initParam['form'] = userPublicProfileForm
    return render_to_response("usersetting/publicprofile.html", initParam, context_instance=RequestContext(request))


def subscriptionSetting(request, *args, **kwargs):
    """Save subscription setting."""
    initParam = {}
    user = get_object_or_404(models.User, pk=request.user.id, username=request.user.username)
    if request.method == "POST":
        ids = request.POST.getlist('subscription_id')
        user.subscriptionitem_set.clear()
        for id in ids:
            try:
                subscriptionItem = models.SubscriptionItem.objects.get(id=id)
                user.subscriptionitem_set.add(subscriptionItem)
            except models.SubscriptionItem.DoesNotExist:
                return Http404
        initParam['account_msg'] = _('The subscription setting has been updated.')

    subscriptionSettings = models.SubscriptionItem.objects.all()
    selectSettings = user.subscriptionitem_set.all()
    initParam['subscriptionSettings'] = subscriptionSettings
    initParam['selectSettings'] = selectSettings
    return render_to_response("usersetting/subscription.html", initParam, context_instance=RequestContext(request))


def changePassword(request, *args, **kwargs):
    initParam = {}
    if request.method == "POST":
        old_password = request.POST.get('old-password')
        new_password = request.POST.get('new-password')
        user = authenticate(username=request.user.username, password=old_password)
        if user:
            if old_password == new_password:
                initParam['account_error'] = _('Old password and new password can not be the same.')
            else:
                user.set_password(new_password)
                user.save()
                initParam['account_msg'] = _('The account password has been updated.')
        else:
            initParam['account_error'] = _('Old password is not correct.')
    return render_to_response("usersetting/account_password.html", initParam, context_instance=RequestContext(request))


def socialConnection(request):
    return render_to_response("usersetting/social_connection.html",{"test":"test"},
                        context_instance=RequestContext(request))


def security_setting(request):
    return render_to_response("usersetting/security_setting.html",{"test":"test"},
                        context_instance=RequestContext(request))
