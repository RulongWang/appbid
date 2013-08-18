__author__ = 'rulongwang'
from django.contrib.auth import authenticate,login,logout
from django.shortcuts import render_to_response,HttpResponse,  RequestContext, HttpResponseRedirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.core.urlresolvers import reverse
from account.RegisterForm import RegisterForm
from django.contrib.auth.models import User

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
            return HttpResponseRedirect("/")


    return render_to_response("account/register.html",{"register_form":registerForm},
                        context_instance=RequestContext(request))


def _login(request, username, password):
    pass


def myprofile(request):
    pass