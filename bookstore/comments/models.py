from django.db import models
from users.models import Passport
from books.models import Books
# Create your models here.


class Comments(models.Model):
	is_delete = models.BooleanField(default=False,verbose_name='逻辑删除')
	create_time = models.DateTimeField(auto_now_add=True,verbose_name='创建时间')
	update_time = models.DateTimeField(auto_now=True,verbose_name='更新时间')
	show = models.BooleanField(default=True,verbose_name="显示评论")
	content = models.CharField(max_length=1000,verbose_name="评论内容")
	passport = models.ForeignKey('users.Passport')
	book = models.ForeignKey('books.Books')

	class Meta:
		db_table = 's_comments'
