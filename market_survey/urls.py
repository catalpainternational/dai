from django.conf.urls import patterns, include, url

from market_survey import views

urlpatterns = patterns('',
    url(r'^average/', views.avg_product_list, name='average'),
    url(r'^', views.product_list, name='index'),
)