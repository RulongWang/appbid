__author__ = 'rulongwang'
import json

from django.contrib.auth import authenticate,login,logout
from django.shortcuts import render_to_response,HttpResponse,  RequestContext, HttpResponseRedirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.db.models import Q
from django.contrib.auth.models import User
from account import models
from account_form import RegisterForm, UserDetailForm, UserPublicProfileForm, EmailItemForm


def login_view(request):
    initParam = {}
    user = authenticate(username=request.POST.get('username'), password=request.POST.get('password'))
    redirect_to = request.POST.get('next', None)
    redirect_urls = (None, '', '/account/logout/', '/account/register/')
    for url in redirect_urls:
        if redirect_to == url:
            redirect_to = '/'
            break
    if user is not None:
        if user.is_active:
            login(request, user)
            return HttpResponseRedirect(redirect_to)
        else:
            initParam['login_error'] = _('%(name)s is not active. Please active it by %(email)s.') % {'name': user.username, 'email': user.email}
    else:
        initParam['login_error'] = _('username or password is not correct.')
    initParam['user_name'] = request.POST.get('username')
    return render_to_response("account/login.html", initParam, context_instance=RequestContext(request))


def logout_view(request):
    logout(request)
    redirect_to = '/'
    return render_to_response('account/login.html', {"redirect_to": redirect_to}, context_instance=RequestContext(request))


def auth_home(request):
    redirect_to = request.GET.get('next', '/')
    return render_to_response("account/login.html", {'redirect_to': redirect_to}, context_instance=RequestContext(request))


def register(request):
    """user register method"""
    initParam = {}
    registerForm = RegisterForm()
    if request.method == "POST":
        registerForm = RegisterForm(request.POST)
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
                    #TODO:need do it later.
                    # userProfile = models.UserProfile()
                    # userProfile.user = user
                    # userProfile.is_bid_approved = False
                    # userProfile.save()
                    return HttpResponseRedirect("/account/register_active/")
                else:
                    initParam['register_error'] = _('Register failed, please try again.')
    initParam['register_form'] = registerForm
    return render_to_response("account/register.html", initParam, context_instance=RequestContext(request))


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


def register_active(request, *args, **kwargs):
    initParam = {}
    return render_to_response("account/register_active.html", initParam, context_instance=RequestContext(request))


def _login(request, username, password):
    pass


def myprofile(request):
    pass


def user_detail(request):
    detail_form = UserDetailForm()
    return render_to_response("account/accountsetting.html",{"form":detail_form},
                        context_instance=RequestContext(request))


def payment_account(request):
    payment_accounts = models.Account.objects.all()
    return render_to_response("account/payment_account.html",{"payment_accounts":payment_accounts},
                        context_instance=RequestContext(request))


def user_public_profile(request):
    form = UserPublicProfileForm()

    return render_to_response("account/account_profile.html",{'form':form},context_instance=RequestContext(request))


def email_notification(request):
    email_items = models.EmailItem.objects.all()

    return render_to_response("account/account_email_setting.html",{"email_items":email_items},
                        context_instance=RequestContext(request))


def change_password(request):
    return render_to_response("account/account_password.html",{"test":"test"},
                        context_instance=RequestContext(request))


def social_connection(request):
    return render_to_response("account/social_connection.html",{"test":"test"},
                        context_instance=RequestContext(request))


