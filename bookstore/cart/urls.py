from django.conf.urls import url
from cart import views

urlpatterns = [
    url(r'^cart_add/$', views.cart_add,name='cart_add' ),
    url(r'^cart_show/$', views.cart_show,name='cart_show' ),
    url(r'^cart_update/$', views.cart_update,name='cart_update' ),
    url(r'^cart_count/$', views.cart_count,name='cart_count' ),

]
