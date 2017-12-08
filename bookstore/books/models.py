from django.db import models
from db.base_model import BaseModel
from books.enums import *
from tinymce.models import HTMLField


class BooksManager(models.Manager):
	"""商品类型管理"""
	def get_books_by_type(self,type_id,limit=None,sort='default'):
		# 建立时间
		if sort == 'new':
			order_by = ('-create_time',)
		# 销量
		elif sort == 'hot':
			order_by = ('-sales',)
		# 价格
		elif sort == 'price':
			order_by = ('price',)
		# 按照primary key 降序排列
		else:
			order_by = ('-id',)
		# 查询数据　　　*为拆包 将元组解开
		books_li = self.filter(type_id=type_id).order_by(*order_by)
		# 分段
		if limit:
			books_li = books_li[:limit]
		return books_li

	def get_books_id(self,books_id):
		"""根据商品的id获取商品的信息"""
		try:
			books = self.get(id=books_id)
		except self.model.DoesNotExist:
			books = None
		return books


class Books(BaseModel):
	"""商品模型类"""
	# 商品类型选择
	books_type_choices = ((k,v) for k,v in BOOK_TYPE.items())
	# 商品是否上线
	status_choices = ((k,v) for k,v in STATUS_CHOICE.items())
	detail = HTMLField(verbose_name='商品详情')
	name = models.CharField(max_length=20,verbose_name="商品名称")
	desc = models.CharField(max_length=128, verbose_name="商品简介")
	unit = models.CharField(max_length=20, verbose_name="商品单位")
	stock = models.IntegerField(default=1, verbose_name="商品库存")
	sales = models.IntegerField(default=0, verbose_name="商品销量")
	image = models.ImageField(upload_to='books',verbose_name='商品图片')
	price = models.DecimalField(max_digits=10, decimal_places=2,verbose_name="商品价格")
	status = models.SmallIntegerField(default=ONLINE, choices=status_choices, verbose_name='商品状态')
	type_id = models.SmallIntegerField(default=PYTHON,choices=books_type_choices,verbose_name="商品种类")

	objects = BooksManager()

	class Meta:
		db_table = 's_books'
