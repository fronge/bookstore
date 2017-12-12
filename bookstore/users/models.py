from django.db import models
from db.base_model import BaseModel
from hashlib import sha1


def get_hash(str):
	"""将一个字符串转成hash"""
	sh = sha1()
	sh.update(str.encode('utf-8'))
	return sh.hexdigest()


class PassportManger(models.Manager):
	"""用于实现对用户数据库表的操作"""
	def add_one_passport(self, username, password, email):
		"""添加一个账户信息"""
		passport = self.create(
			username=username,
			password=get_hash(password),
			email=email
		)
		return passport

	def get_one_passport(self, username, password):
		try:
			passport =self.get(username=username, password=get_hash(password))
		except self.model.DoesNotExist as e:
			print("用户密码错误",e)
			passport = None
		return passport

	def check_passport(self,username):
		"""检查用户是否存在"""
		try:
			passport = self.get(username=username)
		except self.model.DoesNotExist:
			passport = None

		return passport

class AddressManger(models.Manager):
	"""地址管理类"""
	def get_default_address(self,passport_id):
		try:
			# 判断是否有默认地址
			addr = self.get(passport_id=passport_id,is_default=True)
		#没有默认地址
		except self.model.DoesNotExist:
			addr = None
		return addr

	# 增加一个用户收货信息
	def add_one_address(self, passport_id, recipient_name, recipient_addr, zip_code, recipient_phone):
		addr = self.get_default_address(passport_id=passport_id)
		if addr:
			is_default = False
		else:
			is_default = True
		addr = self.create(
						passport_id=passport_id,
						recipient_name=recipient_name,
						recipient_addr=recipient_addr,
						recipient_phone=recipient_phone,
						zip_code=zip_code,
						is_default=is_default
						)
		return addr


class Passport(BaseModel):
	"""用户模型类"""
	username = models.CharField(max_length=20, verbose_name='用户名称')
	password = models.CharField(max_length=40, verbose_name='用户密码')
	email = models.EmailField(verbose_name='用户邮箱')
	is_active = models.BooleanField(default=False, verbose_name='激活状态')

	# 用户表的管理器
	objects = PassportManger()

	class Meta:
		db_table = 's_user_account'


class Address(BaseModel):
	"""地址模型类"""
	recipient_name = models.CharField(max_length=20,verbose_name='收件人')
	recipient_addr = models.CharField(max_length=256,verbose_name='收件地址')
	zip_code = models.CharField(max_length=5,verbose_name="邮编")
	recipient_phone = models.CharField(max_length=11,verbose_name='联系电话')
	is_default = models.BooleanField(default=False,verbose_name='是否默认')
	passport = models.ForeignKey("Passport",verbose_name="账户")

	objects = AddressManger()

	class Meta:
		db_table = "s_user_address"