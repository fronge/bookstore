from django.shortcuts import render,redirect,HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.urlresolvers import reverse
from .models import Passport
from .models import Address
import re
import json
from utils.decorators import login_required


# 注册页面
def register(requset):
	return render(requset,'users/register.html')

# 注册
@csrf_exempt
def register_hander(request):
	data = json.loads(request.body.decode("utf-8"))
	username = data.get('username','')
	password = data.get('password','')
	email = data.get('email','')
	# 判断是否有空
	if not all([username,password,email]):
		return JsonResponse({
		'res':2,
		'code':500
		})
	# 判断用户是有存在
	user = Passport.objects.filter(username=username)
	if user:
		return JsonResponse({'res':3})
	try:
		# 写入数据库
		Passport.objects.add_one_passport(username=username,password=password,email=email)
		return JsonResponse({
			'res': 1,
			'code': 200
		})
	except:
		return JsonResponse({
			'res':0,
		})


# 登陆
def log(request):
	"""跳转"""
	checked = ''
	return render(request,"users/login.html",{"checked":checked})


# 登录校验状态 ajax版本
@csrf_exempt
def login_check(request):
	data = json.loads(request.body.decode('utf-8'))
	username = data.get('username','')
	password = data.get('password','')
	remember = data.get('remember','')
	# 如果用户名或密码有空
	if not all([username,password]):
		return JsonResponse({
			'res':2
		})
	# url_path为了给session设置个路由,哪里来的，set_cookie 是JsonResponse的方法
	next_url = request.session.get('url_path',reverse("books:index"))
	jres = JsonResponse({'res':1,'next_url':next_url})
	# 比对用户名和密码是否正确
	user = Passport.objects.get_one_passport(username =username,password=password)
	if user:
		# 如果选择记住密码
		if remember:
			jres.set_cookie('username',username,max_age=7*24*3600)
		else:
			jres.delete_cookie('username')
		# 如果正确，将用户名,登录状态写入session中
		request.session['username']=username
		request.session['login_line']=True
		request.session['passport_id']=user.id
		return jres
	else:
		# 用户名或密码错误
		return JsonResponse({
			'res':0
		})

def logout(request):
	"""退出登录"""
	request.session.flush()
	# 跳转到首页
	return HttpResponseRedirect('/books/index')

@login_required
def user(request):
	"""用户中心－信息页"""
	passport_id = request.session.get("passport_id")
	addr = Address.objects.get_default_address(passport_id=passport_id)
	books_li = []
	context = {
		"addr": addr,
		"page": 'user',
		"books_li": books_li
	}
	return render(request,"users/user_center_info.html",context)
