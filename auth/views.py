__author__ = 'rulongwang'
from django.contrib.auth import authenticate,login,logout
from django.shortcuts import render_to_response
from django.shortcuts import render_to_response, RequestContext, HttpResponseRedirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect

def login_view(request):
    user = authenticate(username=request.POST['username'], password=request.POST['password'])
    if user is not None:
        login(request, user)
        print request.user
        # return HttpResponseRedirect('/')
        return render_to_response('auth/logon.html', {"test":"test"}, context_instance=RequestContext(request))

    else:
        pass
        # return store_view(request)

def logout_view(request):
    logout(request)
    return render_to_response('auth/logon.html',{"test":"test"}, context_instance=RequestContext(request))

    # return store_view(request)

def auth_home(request):
    return render_to_response('auth/logon.html',{"test":"test"}, context_instance=RequestContext(request))
