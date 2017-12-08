from django.conf.urls import url
from books.views import index,detail,list

urlpatterns = [
    url(r'^index$', index,name='index'),
    url(r'^books/detail(?P<books_id>\d*)$', detail,name='detail'),
    url(r'^list/(?P<type_id>\d+)/(?P<page>\d+)/$', list,name='list'),
]
