from django.shortcuts import render,HttpResponseRedirect
from .models import Books
from .enums import *
from django.core.paginator import Paginator
# Create your views here.

def index(request):
	'''显示首页'''
	# 查询每个种类的3个新品信息和4个销量最好的商品信息
	python_new = Books.objects.get_books_by_type(PYTHON, 3, sort='new')
	python_hot = Books.objects.get_books_by_type(PYTHON, 4, sort='hot')
	javascript_new = Books.objects.get_books_by_type(JAVASCRIPT, 3, sort='new')
	javascript_hot = Books.objects.get_books_by_type(JAVASCRIPT, 4, sort='hot')
	algorithms_new = Books.objects.get_books_by_type(ALGORITHMS, 3, sort='new')
	algorithms_hot = Books.objects.get_books_by_type(ALGORITHMS, 4, sort='hot')
	machinelearning_new = Books.objects.get_books_by_type(MACHINELEARNING, 3, sort='new')
	machinelearning_hot = Books.objects.get_books_by_type(MACHINELEARNING, 4, sort='hot')
	operatingsystem_new = Books.objects.get_books_by_type(OPERATINGSYSTEM, 3, sort='new')
	operatingsystem_hot = Books.objects.get_books_by_type(OPERATINGSYSTEM, 4, sort='hot')
	database_new = Books.objects.get_books_by_type(DATABASE, 3, sort='new')
	database_hot = Books.objects.get_books_by_type(DATABASE, 4, sort='hot')
	print(database_hot)
	# 定义模板上下文
	context = {
		'python_new': python_new,
		'python_hot': python_hot,
		'javascript_new': javascript_new,
		'javascript_hot': javascript_hot,
		'algorithms_new': algorithms_new,
		'algorithms_hot': algorithms_hot,
		'machinelearning_new': machinelearning_new,
		'machinelearning_hot': machinelearning_hot,
		'operatingsystem_new': operatingsystem_new,
		'operatingsystem_hot': operatingsystem_hot,
		'database_new': database_new,
		'database_hot': database_hot,
	}
	return render(request,"books/index.html", context=context)


def detail(request,books_id):
	"""商品详情"""
	books = Books.objects.get_books_id(books_id =books_id)
	if books is None:
		# 商品不存在，跳转到首页
		return HttpResponseRedirect('books:index')
	# 新品推荐
	books_li = Books.objects.get_books_by_type(type_id=books.type_id,limit=2,sort='new')
	return render(request,'books/detail.html',{"books":books,"books_li":books_li})

def list(request,type_id,page):
	"""商品列表页面"""
	sort = request.GET.get('sort','default')
	print(sort)
	if int(type_id) not in BOOK_TYPE.keys():
		return HttpResponseRedirect('books/index')
	books_li = Books.objects.get_books_by_type(type_id=type_id,sort=sort)

	paginator = Paginator(books_li,2)
	num_pages = paginator.num_pages
	if page == '' or int(page) > num_pages:
		page = 1
	else:
		page = int(page)
	# 页码控制
	books_li = paginator.page(page)
	if num_pages < 5:
		pages = range(1,num_pages+1)
	elif page <= 3:
		pages = range(1,6)
	elif num_pages - page <= 2:
		pages  = range(num_pages-4,num_pages+1)
	# 新品推荐　
	books_new = Books.objects.get_books_by_type(type_id=type_id,limit=2,sort='new')
	# 定义上下文
	type_title = BOOK_TYPE[int(type_id)]
	context = {
		'books_li': books_li,
		'books_new': books_new,
		'type_id': type_id,
		'sort':sort,
		'type_title': type_title,
		'pages': pages
	}
	return render(request,'books/list.html',context)