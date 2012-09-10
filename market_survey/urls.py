from django.conf.urls import patterns, include, url

from market_survey import views

urlpatterns = patterns('',
    url(r'^', views.product_list, name='index'),
)