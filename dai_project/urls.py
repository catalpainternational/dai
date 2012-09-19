import os
from django.conf.urls import patterns, include, url

from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'dai_project.views.home', name='home'),
    # url(r'^dai_project/', include('dai_project.foo.urls')),
    url(r'^rosetta/', include('rosetta.urls')),
    (r'^localeurl/', include('localeurl.urls')),
    url(r'^', include('market_survey.urls')),
    url(r'^', include(admin.site.urls)),
    #(r'^admins/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.join(os.path.dirname(__file__), 'templates/admin/static').replace('\\','/'), 'show_indexes': True}),
    (r'^grappelli/', include('grappelli.urls')),
)
