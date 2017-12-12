from django.conf.urls import url
from users import views

urlpatterns = [
    url(r'^register/$', views.register,name='register'),
    url(r'^register_hander/$', views.register_hander,name='register_hander'),
    url(r'^login/$', views.log,name='login'),
    url(r'^logout/$', views.logout,name='logout'),
    url(r'^login_check/$', views.login_check,name='login_check'),
    url(r'^center/$', views.user,name='center'),
    url(r'^address/$', views.address,name='address'), #用户中心－地址栏
    url(r'^order/$', views.order,name='order'), #用户中心－订单页
    url(r'^verifycode/$', views.verifycode,name='verifycode'),#验证码
]

