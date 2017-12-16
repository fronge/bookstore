from django.shortcuts import redirect,HttpResponseRedirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse

def login_required(view_func):
	def wrapper(request,*args,**kwargs):
		if request.session.has_key('login_line'):
			return view_func(request,*args,**kwargs)
		else:
			return HttpResponseRedirect('/users/login/')


	return wrapper