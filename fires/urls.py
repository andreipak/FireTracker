from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^firestarter/$', 'firestarter.fires.views.index'),
    (r'^firestarter/fire/(?P<un_id>[-\w]+)/(?P<address>[-\w]+)/$', 'firestarter.fires.views.fire'),
    (r'^firestarter/person/(?P<un_id>[-\w]+)/(?P<slug>[-\w]+)/$', 'firestarter.fires.views.person'),
    (r'^firestarter/admin/', include(admin.site.urls)),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
)