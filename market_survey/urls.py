from django.conf.urls import patterns, include, url

from market_survey import views

urlpatterns = patterns('',
    url(r'^summary/', views.avg_product_list, name='summary'),
    url(r'^filtering/', views.product_list, name='filtering'),
    url(r'^', views.index, name='index'),
)