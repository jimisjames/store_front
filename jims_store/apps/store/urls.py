from django.conf.urls import url, include
from . import views


urlpatterns = [
    url(r'^$', views.home),
    url(r'^cart$', views.cart),
    url(r'^reg$', views.reg),
    url(r'^admin$', views.admin),
    url(r'^contact$', views.contact),
    url(r'^products$', views.products),
    url(r'^login_page$', views.login_page),
    url(r'^login$', views.login),
    url(r'^logout$', views.logout),
    url(r'^item_page$', views.item_page),
    url(r'^new_product$', views.new_product),
    url(r'^remove/(?P<id>\d+)$', views.remove),
    url(r'^view/(?P<id>\d+)$', views.view),
    url(r'^level/(?P<id>\d+)$', views.level),
    url(r'^in_stock/(?P<id>\d+)$', views.in_stock),
    url(r'^new_photo/(?P<id>\d+)$', views.new_photo),
    url(r'^delete/product/(?P<id>\d+)$', views.delete_product),
]
