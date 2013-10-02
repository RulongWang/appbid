from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from home.tests import test
import seller.urls
import usersetting.urls
import query.urls
import bid.urls
import dashboard.urls
import payment.urls
import order.urls


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', include('home.urls', namespace='home')),
    url(r'^comments/', include('django.contrib.comments.urls')),
    url(r'^test/$', test, name='goodtest'),
    url(r'^seller/', include(seller.urls, namespace='seller')),
    url(r'^usersetting/', include(usersetting.urls, namespace='usersetting')),
    url(r'^query/', include(query.urls, namespace='query')),
    url(r'^bid/', include(bid.urls, namespace='bid')),
    url(r'^dashboard/', include(dashboard.urls, namespace='dashboard')),
    url(r'^order/', include(order.urls, namespace='order')),
    url(r'^payment/', include(payment.urls, namespace='payment')),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
