from django.shortcuts import render
from django.http import JsonResponse
from books.models import Books
from utils.decorators import login_required
from django_redis import get_redis_connection
# Create your views here.

def cart_add(request):
	"""向购物车中添加数据"""
	if not request.session.has_key('loin_line'):
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

	books = Books.objects.get_books_id(books_id=books_id)
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

	res = conn.hget(cart_key,books_id)
	if res is None:
		res = count
	else:
		res = int(res) + count

	if res > books.stock:
		return JsonResponse({
			'res':4,
			'errmsg':'商品库存不足'
		})
	else:
		conn.hget(cart_key,books_id,res)

	return JsonResponse({
		'res':5
	})
