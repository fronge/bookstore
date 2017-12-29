from django.shortcuts import render,redirect,HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse,HttpResponse
from django.core.urlresolvers import reverse
from django_redis import get_redis_connection

from books.models import Books
from .models import Passport,Address
from order.models import OrderInfo,OrderGoods
import re
import json
# 登录验证的装饰器
from utils.decorators import login_required
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from users.tasks import send_active_email
from django.core.mail import send_mail
from bookstore import settings
# 绘制验证码
from PIL import Image,ImageDraw,ImageFont
import random
import io

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
    user = Passport.objects.check_passport(username=username)
    if user:
        return JsonResponse({'res':3})

    try:
        # 写入数据库
        passport = Passport.objects.add_one_passport(username=username,password=password,email=email)
        # 生成激活的token itstangerous
        serializer = Serializer(settings.SECRET_KEY, 3600)
        token = serializer.dumps({'confirm': passport.id})
        token = token.decode()
        # 给用户的邮箱发激活邮件
        # send_mail('藏书阁书城-首页用户激活', '', settings.EMAIL_FROM, [email],html_message='<a href="http://127.0.0.1:8000/user/active/%s/">http://127.0.0.1:8000/user/active/</a>' % token)
#        send_active_email(token,username,email)
        print("进入正确的注册")
        return JsonResponse({
        'res': 1,
        'code': 200
        })
    except Exception as e:
        print(e)
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
    verifycode = data.get('verifycode','')
    print(username)   
 # 如果用户名或密码有空
    if not all([username,password,verifycode]):
        return JsonResponse({
            'res':2
        })
    if verifycode.upper() != request.session['verifycode']:
        return JsonResponse({
            'res': 6
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
        print("进入正确的验证")
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
    return HttpResponseRedirect('/users/login/')

def user(request):
    """用户中心－信息页"""
    passport_id = request.session.get("passport_id")
    addr = Address.objects.get_default_address(passport_id=passport_id)
    con = get_redis_connection('default')
    key = 'history_%d'%passport_id
    # 取出用户最近浏览的五个商品的id
    history_li = con.lrange(key,0,4)
    books_li = []
    for id in history_li:
        books = Books.objects.filter(id=id)
        books_li.append(books)
    context = {
        "addr": addr,
        "page": 'user',
        "books_li": books_li
    }
    return render(request,"users/user_center_info.html",context)

@login_required
@csrf_exempt
def address(request):
    """用户中心　地址页"""
    # 获取登录用户的id
    passport_id = request.session.get("passport_id")

    if request.method == "GET":
        # 显示地址页面
        # 查询用户的默认地址
        addr = Address.objects.get_default_address(passport_id=passport_id)
        addr_li = Address.objects.filter(passport_id=passport_id).order_by('-create_time')[:4]
        return render(request,'users/user_center_site.html',{'addr':addr,'addr_li':addr_li})

    else:
        recipient_name = request.POST.get('recipient_name')
        recipient_addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        recipient_phone = request.POST.get('phone_num')
        is_def = request.POST.get('is_default')
        if is_def == 'true':
            is_def = True
        elif is_def == 'false':
            is_def = False
        # 校验
        if not all([recipient_name,recipient_addr,zip_code,recipient_phone]):
            return render(request,'users/user_center_site.html',{"res":1,'errmsg':'参数不能为空'})

        # 添加收,货地址
        Address.objects.add_one_address(passport_id=passport_id,
                                        recipient_name=recipient_name,
                                        recipient_addr=recipient_addr,
                                        zip_code=zip_code,
                                        recipient_phone=recipient_phone,
                                        is_def=is_def)
        # return redirect(reverse('users:address'))
        return JsonResponse({'res':2})

@login_required
def order(request):
    """用户中心－订单页"""
    passport_id = request.session.get('passport_id')
    order_li = OrderInfo.objects.filter(passport_id=passport_id)
    # 获取订单的商品信息
    for order in order_li:
        order_id = order.order_id
        order_books_li = OrderGoods.objects.filter(order_id=order_id)
        # 计算商品的小计
        for order_books in order_books_li:
            count = order_books.count
            price = order_books.price
            amount = count * price
            # 保存订单中每个商品的小计
            order_books.amount = amount

        # 给order对象动态增加一个属性order_goods_li 保存订单中商品的信息
        order.order_books_li = order_books_li

    context = {
        'order_li':order_li,
        'page':'order'
    }
    
    return render(request,'users/user_center_order.html',context)

def verifycode(request):
	"""绘制验证码"""
	try:
		# 定义一个变量，用于画面的背景色，宽，高
		bgcolor = (random.randrange(20,100),random.randrange(20,100),255)
		width = 100
		height = 25
		# 创建画面对象
		im =  Image.new("RGB",(width,height),bgcolor)
		# 撞见画笔对象
		draw = ImageDraw.Draw(im)
		# 调用画笔的point
		for i in range(0,100):
			xy = (random.randrange(0,width),random.randrange(0,height))
			fill = (random.randrange(0,255),255,random.randrange(0,255))
			draw.point(xy,fill=fill)
		# 定义验证码的备选值
		str1 = 'ABCD123EFGHIJK456LMNPQRSTU78V9WSYZ0'
		# 随机选取４个值作为验证码
		rand_str = ''
		for i in range(0,4):
			rand_str += str1[random.randrange(0,len(str1))]
		# 构造字体对象
		font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf')
		fontcolor = (255,random.randrange(0,255),random.randrange(0,255))
		# 绘制4个字
		draw.text((5,2),rand_str[0],font=font,fill=fontcolor)
		draw.text((25,2),rand_str[1],font=font,fill=fontcolor)
		draw.text((50,2),rand_str[2],font=font,fill=fontcolor)
		draw.text((75,2),rand_str[3],font=font,fill=fontcolor)
		# 释放画笔
		del draw
		# 存入session,用与做进一步的验证
		request.session['verifycode'] = rand_str
		# 内存文件操作
		buf = io.BytesIO()
		im.save(buf,"png")
		# 将图片保存在内存中，文件类型为png
		return HttpResponse(buf.getvalue(),'image/png')
	except Exception as e:
		print(e)
		return render(request,'users/login.html')

def register_active(request,token):
    """账户激活"""
    serializer = Serializer(settings.SECRET_KEY,3600)
    try:
        info = serializer.loads(token)
        passport_id = info['confirm']
        #进行用户激活
        passport = Passport.objects.get(id=passport_id)
        passport.is_active = True
        passport.save()
        #跳转页面到登录页面
        return redirect(reverse('user:login'))
    except SignatureExpired:
        return HttpResponse("激活链接已过期")

