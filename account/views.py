__author__ = 'rulongwang'
from django.contrib.auth import authenticate,login,logout
from django.shortcuts import render_to_response,HttpResponse,  RequestContext, HttpResponseRedirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.core.urlresolvers import reverse
from account_form import RegisterForm,UserDetails, PublicProfile,EmailItems
from django.contrib.auth.models import User
from account import models


def login_view(request):
    user = authenticate(username=request.POST['username'], password=request.POST['password'])
    redirect_to = request.POST['next']
    #print redirect_to
    if user is not None and user.is_active:
        login(request, user)

       # return HttpResponseRedirect(redirect_to)
       # return render_to_response("home/home.html", {'var': 'foo'}, context_instance=RequestContext(request))
        # return redirect()
        # return HttpResponseRedirect('auth')
        return HttpResponseRedirect(redirect_to)

    else:
        return HttpResponse("s is not logged in")
        # return store_view(request)


def logout_view(request):
    logout(request)
    redirect_to = '/'
    return render_to_response('account/login.html', {"redirect_to": redirect_to}, context_instance=RequestContext(request))

    # return store_view(request)


def auth_home(request):
    redirect_to = request.GET['next']
    return render_to_response("account/login.html", {'redirect_to': redirect_to}, context_instance=RequestContext(request))


def register(request):
    registerForm = RegisterForm()
    if request.method =="POST":
        rform =RegisterForm(request.POST.copy())

        if rform.is_valid():
            username = rform.cleaned_data["username"]
            email = rform.cleaned_data["email"]
            password = rform.cleaned_data["password"]
            user = User.objects.create_user(username,email,password)
            user.save()
            userProfile = models.UserProfile()
            userProfile.user = user
            userProfile.is_bid_approved = False
            userProfile.save()
            return HttpResponseRedirect("/")


    return render_to_response("account/register.html",{"register_form":registerForm},
                        context_instance=RequestContext(request))


def _login(request, username, password):
    pass


def myprofile(request):
    pass



def account_settting(request):
    detail_form = UserDetails()
    return render_to_response("account/accountsetting.html",{"form":detail_form},
                        context_instance=RequestContext(request))




def user_detail(request):
    return render_to_response("account/accountsetting.html",{"test":"test"},
                        context_instance=RequestContext(request))


def user_public_profile(request):
    form = PublicProfile()
    return render_to_response("account/account_profile.html",{'form':form},context_instance=RequestContext(request))


def email_notification(request):
    email_items = models.email_setting.objects.all()
    return render_to_response("account/account_email_setting.html",{"email_items":email_items},
                        context_instance=RequestContext(request))


def change_password(request):
    return render_to_response("account/account_password.html",{"test":"test"},
                        context_instance=RequestContext(request))


def social_connection(request):
    return render_to_response("account/social_connection.html",{"test":"test"},
                        context_instance=RequestContext(request))


