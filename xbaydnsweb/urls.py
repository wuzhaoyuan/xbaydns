from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    # (r'^xbaydnsweb/', include('xbaydnsweb.foo.urls')),

    # Uncomment this for admin:
     #(r'^admin/', include('django.contrib.admin.urls')),
     (r'', include('django.contrib.admin.urls')),
)
