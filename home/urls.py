__author__ = 'rulongwang'

from django.conf.urls import patterns, url
from home import views
from help import views as helpView


urlpatterns = patterns('',
    url(r'^$', views.home, name='home'),
    url(r'^termsandconditions$',helpView.terms,name='terms'),
    url(r'^siterules',helpView.siterules,name='siterule'),
    url(r'^screw-home$', views.screwHome, name='screw_home'),
    url(r'^support',helpView.support,name='support'),
    url(r'^privacy',helpView.privacy,name='privacy'),
    url(r'^contact',helpView.contact,name='contact'),
    url(r'^about',helpView.about,name='about'),
    url(r'^look',views.look,name='look'),
    url(r'^haha',views.haha,name='haha'),

)
