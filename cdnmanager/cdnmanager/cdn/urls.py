from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'cdn.views.home', name='home'),
    # url(r'^cdn/', include('cdn.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    # simple interface with the ftpserver
    url(r'^ftpauth/(?P<username>\w+)/(?P<password>\w+)/$', 'videorepo.views.ftpauth'),

    url(r'^transfer_queue/$', 'videorepo.views.transfer_queue', name='transfer_queue'),
    url(r'^transfer_queue_grid/$', 'videorepo.views.transfer_queue_grid_handler' , name='transfer_queue_grid_handler'),
    url(r'^transfer_queue_grid/cfg/$', 'videorepo.views.transfer_queue_grid_config' , name='transfer_queue_grid_config'),

    url(r'^queue/$', 'videorepo.views.dynamic_transfer_queue', name='dynamic_transfer_queue'),

    url(r'^video_files_by_user_grid/$', 'videorepo.views.video_files_by_user_grid_handler' , name='video_files_by_user_grid_handler'),
    url(r'^video_files_by_user_grid/cfg/$', 'videorepo.views.video_files_by_user_grid_config' , name='video_files_by_user_grid_config'),

    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout'),
    url(r'^videorepo/$', 'videorepo.views.main', name='upload_form'),
    url(r'^$', 'videorepo.views.main', name='main_page'),
    url(r'^projects/add/$', 'videorepo.views.add_project', name='add_project'),

    # Customer logfiles
    url(r'^logfiles/$', 'videorepo.views.customer_logfiles_list', name='customer_logfiles_list'),
    url(r'^logfiles/download/([^/]*)$', 'videorepo.views.download_logfile', name='customer_logfile'),
    url(r'^logfiles/download/all/', 'videorepo.views.download_all_logfiles', name='customer_all_logfiles'),

    # API
    (r'^api/', include('api.urls')),

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

