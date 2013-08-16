__author__ = 'rulongwang'
from django.contrib.auth import authenticate,login,logout
from django.shortcuts import render_to_response,HttpResponse,  RequestContext, HttpResponseRedirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.core.urlresolvers import reverse


def login_view(request):
    user = authenticate(username=request.POST['username'], password=request.POST['password'])
    redirect_to = request.POST['next']
    #print redirect_to
    if user is not None:
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


def myprofile(request):
    pass