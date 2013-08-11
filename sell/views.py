from django.http import HttpResponse
from django.shortcuts import render_to_response, RequestContext, HttpResponseRedirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
from sell import forms
from appbid import models


@csrf_protect
# @method_decorator(login_required)
def register_app(request, *args, **kwargs):
    app = {}
    isExist = False
    if kwargs['pk']:
        app = get_object_or_404(models.App, pk=kwargs['pk'])
        isExist = True

    if request.method == "POST":
        form = forms.AppForm(request.POST)
        saveMethod = kwargs.pop('saveMethod', None)
        if form.is_valid():
            if not isExist:
                app = createApp(form)
            elif saveMethod is not None:
                saveMethod(form.cleaned_data, app)
            return HttpResponseRedirect(reverse(kwargs['nextPage'], args=(app.id,)))
        else:
            print 'bbb'
            return render_to_response(kwargs['backPage'], {'form': form, 'flag': kwargs['flag']},
                                      context_instance=RequestContext(request))
    else:
        form = forms.AppForm()
        if isExist:
            form = forms.AppForm(instance=app)
        return render_to_response(kwargs['backPage'], {'form': form, 'flag': kwargs['flag']},
                                  context_instance=RequestContext(request))


def createApp(form):
    model = form.save(commit=False)
    model.publisher = models.User.objects.get(pk=2)
    model.status = 1
    model.save()
    return model

def updateApp1(form, model):
    """Save the first register page - ."""
    model.description = form['description']
    model.save()


def updateApp2(form, model):
    """Save the second register page - register_download."""
    model.description = form['description']
    model.save()


def updateApp3(form, model):
    """Save the third register page - register_revenue."""
    model.description = form['description']
    model.save()


def hello(request):
    return HttpResponse(" This is the home page")



