__author__ = 'rulongwang'

import json
import os
import random
import string

from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, HttpResponse, RequestContext, HttpResponseRedirect, get_object_or_404, Http404
from django.views.decorators.csrf import csrf_protect
from django.utils.translation import ugettext as _
from django.db.models import Q
from django.db import transaction
from django.conf import settings
from django.contrib.auth.models import User
from usersetting import models
from usersetting import forms
from utilities import email, common
from payment import models as paymentModels
from notification import models as notificationModels


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
            initParam['login_error'] = _('%(name)s is not active. Please active it by %(email)s.') % {'name': user.username, 'email': common.hiddenEmail(user.email)}
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
@transaction.commit_on_success
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


@csrf_protect
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
    """Send the active email to register."""
    initParam = {}
    if kwargs.get('username') and kwargs.get('pk'):
        user = get_object_or_404(models.User, pk=kwargs.get('pk'), username=kwargs.get('username'))
        initParam['email'] = common.hiddenEmail(user.email)

        if request.is_secure():
            link_header = ''.join(['https://', request.META.get('HTTP_HOST')])
        else:
            link_header = ''.join(['http://', request.META.get('HTTP_HOST')])
        token = ''.join(random.sample(string.ascii_letters+string.digits, 30))
        active_link = '/'.join([link_header, 'usersetting', user.username, 'emails', str(user.id), 'confirm_verification', token])

        templates = notificationModels.NotificationTemplate.objects.filter(name='register-active')
        if templates:
            subject = templates[0].subject
            template = templates[0].template.replace('{username}', user.username).replace('{active_link}', active_link)
            recipient_list = [user.email]
            email.sentEmail(subject=subject, message=template, recipient_list=recipient_list)
    return render_to_response("usersetting/register_active.html", initParam, context_instance=RequestContext(request))


@csrf_protect
@transaction.commit_on_success
def registerActiveConfirm(request, *args, **kwargs):
    """Active the account by user clicking the active link."""
    initParam = {}
    username = kwargs.get('username')
    confirm_token = kwargs.get('confirm_token')
    if username and confirm_token and len(confirm_token) == 30:
        users = models.User.objects.filter(username=username)
        if users:
            users[0].is_active = True
            users[0].save()
            securityVerification = models.SecurityVerification()
            securityVerification.user_id = users[0].id
            securityVerification.vtype = 1
            securityVerification.value = users[0].email
            securityVerification.is_verified = True
            securityVerification.save()
            initParam['account_msg'] = _('The account active successfully.')
        else:
            initParam['account_error'] = _('The account %(name)s is not exist.') % {'name': username}
    else:
        initParam['account_error'] = _('The active link is not correct.')
    return render_to_response("usersetting/register_active_confirm.html", initParam, context_instance=RequestContext(request))


def _login(request, username, password):
    pass


def myprofile(request):
    pass


@csrf_protect
@transaction.commit_on_success
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


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def paymentAccount(request, *args, **kwargs):
    payment_accounts = paymentModels.AcceptGateway.objects.all()
    return render_to_response("usersetting/accept_payment.html",{"payment_accounts":payment_accounts},
                        context_instance=RequestContext(request))

@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
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


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
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


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
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


def socialConnection(request, *args, **kwargs):
    return render_to_response("usersetting/social_connection.html",{"test":"test"},
                        context_instance=RequestContext(request))


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def securitySetting(request, *args, **kwargs):
    """security setting include email, phone"""
    initParam = {}
    user = get_object_or_404(models.User, pk=request.user.id, username=request.user.username)
    securitySettings = user.securityverification_set.all()
    for securitySetting in securitySettings:
        if securitySetting.vtype == 1:
            securitySetting.value = common.hiddenEmail(securitySetting.value)
            initParam['email_info'] = securitySetting
        if securitySetting.vtype == 2:
            initParam['phone_info'] = securitySetting
    return render_to_response("usersetting/security_setting.html",initParam, context_instance=RequestContext(request))


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def securitySettingEmail(request, *args, **kwargs):
    """Verify email security setting."""
    initParam = {}
    user = get_object_or_404(models.User, pk=request.user.id, username=request.user.username)
    securitySettings = user.securityverification_set.all()
    for securitySetting in securitySettings:
        if securitySetting.vtype == 1:
            securitySetting.value = common.hiddenEmail(securitySetting.value)
            initParam['email_info'] = securitySetting
        if securitySetting.vtype == 2:
            initParam['phone_info'] = securitySetting
    return render_to_response("usersetting/security_setting_email.html",initParam, context_instance=RequestContext(request))


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def securitySettingPhone(request, *args, **kwargs):
    """Verify phone security setting."""
    initParam = {}
    user = get_object_or_404(models.User, pk=request.user.id, username=request.user.username)
    securitySettings = user.securityverification_set.all()
    for securitySetting in securitySettings:
        if securitySetting.vtype == 1:
            securitySetting.value = common.hiddenEmail(securitySetting.value)
            initParam['email_info'] = securitySetting
        if securitySetting.vtype == 2:
            initParam['phone_info'] = securitySetting
    return render_to_response("usersetting/security_setting_phone.html",initParam, context_instance=RequestContext(request))
