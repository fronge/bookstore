from django.shortcuts import render
from django.http import JsonResponse
from books.models import Books
from utils.decorators import login_required
from django_redis import get_redis_connection
import json
# Create your views here.


@login_required
def cart_add(request):
	"""向购物车中添加数据"""
	if not request.session.has_key('login_line'):
		return JsonResponse({
			'res': 0,
			'errmsg': '请先登录'
		})

	books_id = request.POST.get('books_id')
	books_count = request.POST.get('books_count')
	# 进行数据校验
	if not all([books_count,books_id]):
		return JsonResponse({
			'res': 1,
			'errmsg': '数据不完整'
		})

	books = Books.objects.get_books_by_id(books_id=books_id)
	if books is None:
		# 商品不存在
		return JsonResponse({
			'res': 2,
			'errmsg': "商品不存在"
		})
	try:
		count = int(books_count)
	except Exception as e:
		return JsonResponse({
			'res': 3,
			'errmsg': '商品数量必须为数字'
		})
	# 创建一个redis 链接
	conn = get_redis_connection('default')
	# 购物车rides存储的key值
	cart_key = 'cart_%d'%request.session.get('passport_id')
	# 从缓存中取出商品的数量	
	res = conn.hget(cart_key,books_id)
	if res is None:
		res = count
	else:
		res = int(res) + count
		#stock是数的库存
	if res > books.stock:
		return JsonResponse({
			'res':4,
			'errmsg':'商品库存不足'
		})
	else:
		# 将商品数量加入缓存
		conn.hset(cart_key,books_id,res)

	return JsonResponse({
		'res':5
	})

@login_required
def cart_show(request):
	"""显示用户购物车页面"""
	# 在session中取得用户的id
	passport_id = request.session.get('passport_id')
	# 获取用户购物车缓存的记录
	conn = get_redis_connection('default')

	cart_key = 'cart_%d'%passport_id
	# 书的id :数量
	res_dict = conn.hgetall(cart_key)
	# 书的列表
	books_li = []
	# 商品的总数
	total_count = 0
	# 全部商品的价格
	total_price = 0
	for id, count in res_dict.items():
		# 根据缓存中的book_id来获取书的对象
		try:
			books = Books.objects.get_books_by_id(books_id=id)
			# 每种书的小计，赋值给书作为一个属性
			books.amount = int(count)*books.price
			# 每种书的数量
			books.count = count
			books_li.append(books)

			total_count += int(count)
			total_price += int(count) * books.price
		except Exception as e:
			print(e)

	# 定义模板的上下文
	context = {
		'books_li': books_li,
		'total_count':total_count,
		'total_price':total_price,
	}
	return render(request,'cart/cart.html',context)

@login_required
def cart_update(request):
	# 接受数据
	books_id = request.POST.get('books_id')
	books_count = request.POST.get('books_count')
	print(books_id,books_count)
	# 数据校验
	if not all([books_count,books_id]):
		return JsonResponse({
			'res': 1,
			'errmsg': '数据不完整'
		})

	books = Books.objects.get_books_by_id(books_id=books_id)
	if books is None:
		# 商品不存在
		return JsonResponse({
			'res': 2,
			'errmsg': "商品不存在"
		})
	try:
		count = int(books_count)
	except Exception as e:
		return JsonResponse({
			'res': 3,
			'errmsg': '商品数量必须为数字'
		})
	conn = get_redis_connection('default')
	cart_key = 'cart_%d'%request.session.get('passport_id')
	conn.hset(cart_key,books_id,count)
	return JsonResponse({
		'res':5
		})

@login_required
def cart_count(request):
	"""获取用户购物车中的商品数目"""
	conn = get_redis_connection('default')
	cart_key = 'cart_%d'%request.session.get('passport_id')
	res = 0
	# 获取的是什么　hvals对应哈希对应的所有的值
	# todo 获取的比前段获取的多一个
	res_list = conn.hvals(cart_key)
	print(res_list)
	for i in res_list:
		res += int(i)

	return JsonResponse({'res':res})

@login_required
def cart_del(request):
	"""删除用户购物车中的商品信息"""
	books_id = request.POST.get('books_id')
	# 对商品信息做验证
	if not books_id:
		return JsonResponse({'res':1,'errmsg':'数据不完整'})
	books = Books.objects.get_books_by_id(books_id=books_id)
	if not books:
		return JsonResponse({"res":2,"errmsg":'商品不存在'})

	# 删除购物车中商品信息
	conn = get_redis_connection('default')
	cart_key = 'cart_%d'%request.session.get('passport_id')
	conn.hdel(cart_key,books_id)

	return JsonResponse({"res":5})

# 数据验证函数
def data_required(books_id,books_count):
	if not all([books_count,books_id]):
		return {
			'res': 1,
			'errmsg': '数据不完整'
		}

	books = Books.objects.get_books_by_id(books_id=books_id)
	if books is None:
		# 商品不存在
		return {
			'res': 2,
			'errmsg': "商品不存在"
		}
	try:
		count = int(books_count)
	except Exception as e:
		return {
			'res': 3,
			'errmsg': '商品数量必须为数字'
		}
	conn = get_redis_connection('default')
	cart_key = 'cart_%d'%passport_id
	conn.hset(cart_key,books_id,res)
	return {
		'res':5
		}
