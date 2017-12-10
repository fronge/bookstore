from django.conf.urls import url
from cart import views

urlpatterns = [
    url(r'^cart_add/$', views.cart_add,name='cart_add' ),
    url(r'^cart_show/$', views.cart_show,name='cart_show' ),

]
