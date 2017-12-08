from django.conf.urls import url
from .views import register,register_hander,log,login_check,logout,user

urlpatterns = [
    url(r'^register$', register,name='register'),
    url(r'^register_hander$', register_hander,name='register_hander'),
    url(r'^login$', log,name='login'),
    url(r'^logout$', logout,name='logout'),
    url(r'^login_check$', login_check,name='login_check'),
    url(r'^user_center_info$', user,name='user_center_info'),
]

