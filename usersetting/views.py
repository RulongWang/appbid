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
def loginView(request, *args, **kwargs):
    initParam = {}
    user = authenticate(username=request.POST.get('username'), password=request.POST.get('password'))
    redirect_to = request.POST.get('next', None)
    redirect_urls = (None, '', '/usersetting/', '/dashboard/')
    for url in redirect_urls:
        if redirect_to == url or (url and redirect_to.startswith(str(url))):
            redirect_to = '/'
            break
    if user:
        if user.is_active:
            login(request, user)
            #record user login info, such as IP.
            userLoginInfo = models.UserLoginInfo()
            userLoginInfo.user = user
            userLoginInfo.ip = common.getUserClientIP(request)
            userLoginInfo.save()
            log.info('%(name)s login.' % {'name': user.username})
            return redirect(redirect_to)
        else:
            initParam['login_error'] = _('%(name)s is not active. Please active it by %(email)s.') % {'name': user.username, 'email': common.hiddenEmail(user.email)}
    else:
        initParam['login_error'] = _('username or password is not correct.')
    initParam['user_name'] = request.POST.get('username')
    return render_to_response("usersetting/login.html", initParam, context_instance=RequestContext(request))


@csrf_protect
def logoutView(request, *args, **kwargs):
    logout(request)
    log.info('%(name)s logout.' % {'name': request.user.username})
    redirect_to = '/'
    return render_to_response('usersetting/login.html', {"redirect_to": redirect_to}, context_instance=RequestContext(request))


def forgetPassword(request, *args, **kwargs):
    """Forget password page"""
    initParam = {}
    if request.method == "POST":
        flag = False
        username = request.POST.get('username')
        if '@' in username:
            users = models.User.objects.filter(email=username)
            if users:
                type = 1
                flag = True
        else:
            users = models.User.objects.filter(username=username)
            if users:
                type = 2
                flag = True
        if flag:
            user = users[0]
            #Send the email to user
            notificationViews.sendResetPasswordEmail(request, type=type, user=user)
            email = common.hiddenEmail(user.email)
            initParam['msg'] = _('The password reset link has been sent to %(param)s. Please check your email, click attached link to change your password ASAP.') % {'param': email}
        else:
            initParam['error_msg'] = _('%(param)s do not exist.') % {'param': username}

    return render_to_response("usersetting/forget_password.html", initParam, context_instance=RequestContext(request))


def resetPassword(request, *args, **kwargs):
    """Reset password page."""
    initParam = {}
    type = string.atoi(kwargs.get('type'))
    user_id = kwargs.get('user_id')
    username = kwargs.get('username')
    #TODO:use it later.
    token = kwargs.get('token')
    if type == 1 or type == 2:
        if request.method == "POST":
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            if password != confirm_password:
                initParam['error_msg'] = _('Password is not the same with confirm password.')
            else:
                if type == 1:
                    user = get_object_or_404(models.User, pk=user_id, email=username)
                else:
                    user = get_object_or_404(models.User, pk=user_id, username=username)
                user.set_password(password)
                user.save()
                initParam['msg'] = _('Your password has been updated successfully.')
        return render_to_response("usersetting/reset_password.html", initParam, context_instance=RequestContext(request))
    return Http404


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
            if not bool(re.match(r"^[a-zA-Z0-9_]+$", username)):
                initParam['register_error'] = _('Username just includes number, letter or underline.')
            elif models.User.objects.filter(Q(username=username) | Q(email=email)):
                initParam['register_error'] = _('%(name)s or %(email)s has been used.') % {'name': username, 'email': email}
            else:
                user = User.objects.create_user(username, email, password)
                if user is not None:
                    user.is_active = False
                    user.save()
                    #Init user credit point
                    creditViews.initCreditPoint(user=user)
                    #Add user security verification info.
                    securityVerification = models.SecurityVerification()
                    securityVerification.user = user
                    securityVerification.vtype = 1
                    securityVerification.value = user.email
                    securityVerification.is_verified = False
                    securityVerification.save()
                    #Init some setting for the user
                    # privateSet = models.UserPrivateSetting()
                    # privateSet.user = user
                    # userPrivateItem = models.UserPrivateItem.objects.filter(key='is_bid_approved')
                    # if userPrivateItem:
                    #     privateSet.user_private_item = userPrivateItem[0]
                    #     privateSet.value = False
                    #     privateSet.save()
                    return redirect("".join(["/usersetting/register-active/", user.username, '/', str(user.id)]))
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
            if not bool(re.match(r"^[a-zA-Z0-9_]+$", dict.get('username'))):
                data['message'] = _('Username just includes number, letter or underline.')
                raise
            elif models.User.objects.filter(username=dict.get('username')):
                data['message'] = _('%(param)s has been used.') % {'param': dict.get('username')}
                raise
            else:
                data['message'] = _('%(param)s is valid.') % {'param': dict.get('username')}
        if dict.get('email') is not None:
            if models.User.objects.filter(email=dict.get('email')):
                data['message'] = _('%(param)s has been used.') % {'param': dict.get('email')}
                raise
            else:
                data['message'] = _('%(param)s is valid.') % {'param': dict.get('email')}
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
        #Send the register active email
        notificationViews.sendRegisterActiveEmail(request, user=user)
    return render_to_response("usersetting/register_active.html", initParam, context_instance=RequestContext(request))


@csrf_protect
@transaction.commit_on_success
def registerActiveConfirm(request, *args, **kwargs):
    """Active the account by user clicking the active link."""
    initParam = {}
    username = kwargs.get('username')
    #TODO:Will use it later.
    confirm_token = kwargs.get('confirm_token')
    users = models.User.objects.filter(username=username)
    if users:
        users[0].is_active = True
        users[0].save()
        #Update user security verification info.
        securityVerifications = models.SecurityVerification.objects.filter(user_id=users[0].id, vtype=1)
        if securityVerifications:
            securityVerifications[0].is_verified = True
            securityVerifications[0].save()
        initParam['account_msg'] = _('The account active successfully.')
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
            userDetail = detailForm.save(commit=False)
            userDetail.user_id = request.user.id
            userDetail.save()
            initParam['account_msg'] = _('The account detail has been updated.')
    initParam['form'] = detailForm
    return render_to_response("usersetting/account_setting.html", initParam, context_instance=RequestContext(request))


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
            userPublicProfile.user_id = request.user.id
            thumbnail = request.FILES.get('thumbnail')
            if thumbnail:
                if thumbnail.content_type.startswith('image'):
                    if thumbnail.size > 1000000:
                        initParam['account_msg'] = _('The image size is more than 1M.')
                    else:
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
                        if thumbnail:
                            #Shrink image to (50*50) for user thumbnail.
                            path = '/'.join([settings.MEDIA_ROOT, str(userPublicProfile.thumbnail)])
                            common.imageThumbnail(path=path, size=(50, 50))
                        initParam['account_msg'] = _('The public profile has been updated.')
                else:
                    initParam['account_msg'] =  _('The file type of %(param)s does not supported.') % {'param': thumbnail.name}
            else:
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
@login_required(login_url='/usersetting/home/')
def securityVerification(request, *args, **kwargs):
    """If user has passed phone verification, then will do this security verification(send verification number to phone),
       when do operation such as: change password, update email, update phone number, update payment password."""
    initParam = {}
    user = get_object_or_404(models.User, pk=request.user.id, username=request.user.username)
    if request.method == "POST":
        pin = request.POST.get('pin', None)
        redirect_to = request.POST.get('next')
        if pin and redirect_to:
            #TODO:Check whether pin is correct judging with session value. to do it later.
            return redirect(redirect_to)
    else:
        securitySettings = user.securityverification_set.filter(vtype=2, is_verified=True)
        if securitySettings:
            initParam['phone_number'] = common.hiddenPhone(securitySettings[0].value)
            initParam['next'] = kwargs.get('current', None)
            return render_to_response("usersetting/security_verification.html", initParam, context_instance=RequestContext(request))

    saveMethod = kwargs.get('saveMethod', None)
    if saveMethod:
        return saveMethod(request, args, kwargs)


def sendPIN(request, *args, **kwargs):
    """Send PIN - personal identification number to user's phone, and return verification number to current page."""
    data = {}
    try:
        dict = request.POST
    except:
        dict = request.GET
    try:
        user = models.User.objects.filter(pk=request.user.id, username=request.user.username)
        if user:
            data['ok'] = 'true'
            #TODO:To da it later.
            # send PIN to user phone
            #TODO:set pin to session
        else:
            raise
    except:
        data['ok'] = 'false'
        data['message'] = _('Send PIN failed, please try again.')
    return HttpResponse(json.dumps(data), mimetype=u'application/json')


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
                messages.info(request, _('The account password has been updated.'))
                return redirect(reverse('usersetting:security_setting'))
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
            securitySetting.value = common.hiddenPhone(securitySetting.value)
            initParam['phone_info'] = securitySetting
    return render_to_response("usersetting/security_setting.html", initParam, context_instance=RequestContext(request))


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def securitySettingEmail(request, *args, **kwargs):
    """Verify email security setting."""
    initParam = {}
    user = get_object_or_404(models.User, pk=request.user.id, username=request.user.username)
    if request.method == "POST":
        new_email = request.POST.get('email')
        if user.email == new_email:
            initParam['account_error'] = _('The new email can not be the same as the old one.')
        elif models.User.objects.filter(email=new_email):
            initParam['account_error'] = _('%(param)s has been used.') % {'param': new_email}
        else:
            securityVerifications = user.securityverification_set.filter(vtype=1)
            if securityVerifications:
                securityVerification = securityVerifications[0]
            else:
                securityVerification = models.SecurityVerification()
                securityVerification.user = user
                securityVerification.vtype = 1
            user.email = new_email
            user.save()
            securityVerification.value = new_email
            securityVerification.is_verified = False
            securityVerification.save()
            return redirect(reverse('usersetting:security_setting_email_update'))
    return render_to_response("usersetting/security_setting_email.html", initParam, context_instance=RequestContext(request))


@csrf_protect
@login_required(login_url='/usersetting/home/')
def securitySettingEmailUpdate(request, *args, **kwargs):
    initParam = {}
    user = get_object_or_404(models.User, pk=request.user.id, username=request.user.username)
    initParam['email'] = common.hiddenEmail(user.email)
    #Send the security verification email
    notificationViews.sendSecurityVerificationEmail(request, user=user)
    return render_to_response("usersetting/security_setting_email_update.html", initParam, context_instance=RequestContext(request))


@csrf_protect
@transaction.commit_on_success
def securitySettingEmailConfirm(request, *args, **kwargs):
    initParam = {}
    username = kwargs.get('username')
    confirm_token = kwargs.get('confirm_token')
    if username and confirm_token and len(confirm_token) == 30:
        users = models.User.objects.filter(username=username)
        if users:
            securityVerification = models.SecurityVerification.objects.filter(user_id=users[0].id, vtype=1)
            if securityVerification:
                securityVerification[0].value = users[0].email
                securityVerification[0].is_verified = True
                securityVerification[0].save()
                initParam['account_msg'] = _('Your new email verify successfully.')
            else:
                initParam['account_error'] = _('The email verification failed.')
        else:
            initParam['account_error'] = _('The verification link is not correct.')
    else:
        initParam['account_error'] = _('The verification link is not correct.')
    return render_to_response("usersetting/security_setting_email_confirm.html", initParam, context_instance=RequestContext(request))


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def securitySettingPhone(request, *args, **kwargs):
    """Verify phone security setting."""
    initParam = {}
    user = get_object_or_404(models.User, pk=request.user.id, username=request.user.username)
    if request.method == "POST":
        new_phone = request.POST.get('phone')
        pin = request.POST.get('pin')
        #TODO:Check whether pin is correct judging with session value. to do it later.
        securitySettings = user.securityverification_set.filter(vtype=2)
        if securitySettings:
            if securitySettings[0].value == new_phone:
                initParam['account_error'] = _('The new phone number can not be the same as the old one.')
            elif models.SecurityVerification.objects.filter(vtype=2, value=new_phone):
                initParam['account_error'] = _('%(param)s has been used.') % {'param': new_phone}
            else:
                securitySettings[0].value = new_phone
                securitySettings[0].is_verified = True
                securitySettings[0].save()
                messages.info(request, _('The phone number has been updated.'))
                return redirect(reverse('usersetting:security_setting'))
        else:
            securitySetting = models.SecurityVerification()
            securitySetting.user = user
            securitySetting.vtype = 2
            securitySetting.value = new_phone
            securitySetting.is_verified = True
            securitySetting.save()
            messages.info(request, _('The phone number has been updated.'))
            return redirect(reverse('usersetting:security_setting'))
    return render_to_response("usersetting/security_setting_phone.html", initParam, context_instance=RequestContext(request))


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def paymentAccount(request, *args, **kwargs):
    """payment account setting."""
    initParam = {}
    user = get_object_or_404(models.User, pk=request.user.id, username=request.user.username)

    if request.method == "POST":
        types = request.POST.getlist('gateway_type')
        accounts = request.POST.getlist('payment_account')
        if types and accounts and len(types) == len(accounts):
            for i in range(len(types)):
                gateway = get_object_or_404(paymentModels.Gateway, pk=types[i])
                acceptGateways = user.acceptgateway_set.filter(type_id=types[i])
                if acceptGateways:
                    acceptGateway = acceptGateways[0]
                else:
                    acceptGateway = paymentModels.AcceptGateway()
                    acceptGateway.user = user
                    acceptGateway.type = gateway
                acceptGateway.value = accounts[i].strip()
                acceptGateway.is_active = True
                acceptGateway.is_default = True
                acceptGateway.save()
            initParam['account_msg'] = _('Payment account is updated.')
            #The parameter 'next' means the original URL.
            if request.POST.get('next'):
                return redirect(''.join(['/', request.POST.get('next')]))

    #Init payment account data in page.
    gateways_map = {}
    for gateway in paymentModels.Gateway.objects.filter(is_active=True):
        gateways_map[gateway] = None
    for acceptGateway in user.acceptgateway_set.all():
        acceptGateway.value = common.hiddenEmail(acceptGateway.value)
        gateways_map[acceptGateway.type] = acceptGateway
    initParam['gateways_map'] = gateways_map
    if kwargs.get('next'):
        initParam['next'] = kwargs.get('next')

    return render_to_response("usersetting/accept_payment.html", initParam, context_instance=RequestContext(request))