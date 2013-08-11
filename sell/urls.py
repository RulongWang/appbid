from django.conf.urls import patterns, url
from sell import views

urlpatterns = patterns('',
    url(r'^register_app/(?P<pk>\d*)$', views.register_app,
        {'flag': 1,
         'backPage': 'sell/register_content.html',
         'nextPage': 'sell:register_download',
         'saveMethod': views.updateApp1,
         }, name='register_app'),
    url(r'^register_download/(?P<pk>\d*)$', views.register_app,
        {'flag': 2,
         'backPage': 'sell/register_content.html',
         'nextPage': 'sell:register_revenue',
         'saveMethod': views.updateApp2,
         }, name='register_download'),
    url(r'^register_revenue/(?P<pk>\d*)$', views.register_app,
        {'flag': 3,
         'backPage': 'sell/register_content.html',
         'nextPage': 'sell:register_revenue',
         'saveMethod': views.updateApp3,
         }, name='register_revenue'),
)
