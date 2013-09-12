from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin


urlpatterns = patterns('',
    # Examples:
    #home
    url(r'^$', 'home.views.home', name='home'),
    # url(r'^appbid/', include('appbid.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #url(r'^admin/', include(admin.site.urls)),
    #url(r'^test/$', test, name='goodtest')
    #homepage
    #url(r'^register_app/$', register_app, name="register_app")

)
