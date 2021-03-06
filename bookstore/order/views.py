from django.shortcuts import render,redirect
from django.core.urlresolvers import reverse
from utils.decorators import login_required
from django.http import HttpResponse,JsonResponse
from users.models import Address
from books.models import Books
from order.models import OrderInfo,OrderGoods
from django_redis import get_redis_connection
from datetime import datetime
from django.conf import settings
import os
import time
from django.db import transaction


@login_required
def order_place(request):
    """显示订单页面"""
    # 接收数据
    books_ids = request.POST.getlist('books_ids')
    # 校验数据
    if not all(books_ids):
        return redirect(reverse('cart:show'))

    # 用户收货地址
    passport_id = request.session.get('passport_id')
    addr = Address.objects.get_default_address(passport_id=passport_id)
    # 用户要购买的商品信息
    books_li = []
    # 商品的总数目和总金额
    total_count = 0
    total_price = 0

    conn = get_redis_connection("default")
    cart_key = 'cart_%d'%passport_id
    for id in books_ids:
        # 根据id 获取商品的信息
        books = Books.objects.get_books_by_id(books_id=id)
        # 从ｒｅｄｉｓ中获取商品的信息
        count = conn.hget(cart_key,id)
        books.count = count
        amount = int(count)*books.price
        books.amount = amount
        books_li.append(books)

        # 累计计算商品的总数目和总金额
        total_count += int(count)
        total_price += books.amount

    # 商品运费和实付款
    transit_price = 10
    total_pay = total_price + transit_price

    books_ids = ",".join(books_ids)
    # 组织模板上下文
    context = {
        'addr':addr,
        "total_count":total_count,
        "books_li":books_li,
        "total_price":total_price,
        "transit_price":transit_price,
        "total_pay":total_pay,
        "books_ids":books_ids
    }
    # 使用模板
    return render(request,'order/place_order.html',context)


def order_pay(request):
    """支付订单"""
    if not request.session.has_key('login_line'):
        return JsonResponse({'res':0,'errmsg':'please login'})
    order_id = request.POST.get('order_id')
    if not order_id:
            return JsonResponse({'res':1,'errmsg':"the order dosen't exist"})
    try:
        order = OrderInfo.objects.get(order_id=order_id,
                                      status=1,
                                      pay_method=3)
    except OrderInfo.DoseNotExist:
        return JsonResponse({'res':2,'errmsg':'the error of order!'})

    alipay = Alipay(
        appid='2016090800464054',#app_id
        app_notify_url = None,
        app_private_key_path=os.path.join(settings.BASE_DIR,'order/app_private_key.pem'),
        alipay_public_key_path=os.path.join(settings.BASE_DIR,'order/alipay_public_key.pem'),
        sign_type = 'RSA2',
        debug= True,
        )


    total_pay = order.total_price + order.transit_price
    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no=order_id,
        total_amount=str(total_pay),
        subject='bookstore of good book%s'%order_id,
        return_url=None,
        notify_url=None
        )
    pay_url = settings.ALIPAY_URL + '?' + order_string
    return JsonResponse({'res':3,'pay_url':pay_url,'message':'OK'})

def check_pay(request):
    if not request.session.has_key('login_line'):
        return JsonResponse({'res':0,'errmsg':'please login!'})

    passport_id = request.session.get('passport_id')
    order_id = request.POST.get('order_id')

    if not order_id:
        return JsonResponse({'res':1,'errmsg':"order dosen't exist"})

    try:
        order = OrderInfo.objects.get(order_id=order_id,
                                      passport_id=passport_id,
                                      pay_method=3,
                                      )
    except OrderInfo.DoseNotExist:
        return JsonResponse({'res':2,'errmsg':'the error for your order'})

      # 和支付宝进行交互
    alipay = AliPay(
        appid="2016090800464054",  # 应用id
        app_notify_url=None,  # 默认回调url
        app_private_key_path=os.path.join(settings.BASE_DIR, 'df_order/app_private_key.pem'),
        alipay_public_key_path=os.path.join(settings.BASE_DIR, 'df_order/alipay_public_key.pem'),
        # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        sign_type="RSA2",  # RSA 或者 RSA2
        debug=True,  # 默认False
    )

    while True:
        result = alipay.api_alipay_trade_query(order_id)
        code = result.get('code')
        if code == '10000' and result.get('trade_status') == "TRAADE_SUCCESS":
            order.status = 2
            order.trade_id = result.get('trade_no')
            order.save()
            return JsonResponse({'res':3,'message':'seccessful of pay!'})
        elif code == '40004' or (code == '10000' and result.get('trade_status') =='WAIT_BUYER_PAY'):
            time.sleep(5)
            continue
        else:
            return JsonResponse({'res':4,'errmsg':'the error with pay,please try again!'})


def order_commit(request):
    """生成订单"""
    # 验证是否登录
    if not request.session.has_key('login_line'):
        return JsonResponse({'res':0,'errmsg':'用户未登录'})

    # 接收数据
    pay_method = request.POST.get('pay_method')
    addr_id = request.POST.get('addr_id')
    books_ids = request.POST.get('books_ids')

    # 进行数据校验
    if not all([addr_id,pay_method,books_ids]):
        return JsonResponse({'res':1,"errmsg":"数据不完整"})

    try:
        addr = Address.objects.get(id=addr_id)
    except :
        return JsonResponse({'res':2,"errmsg":"地址信息错误"})
    if int(pay_method) not in OrderInfo.PAY_METHODS_ENUM.values():
        return JsonResponse({'res':3,'errmsg':'不支持的支付方式'})

    # 订单创建
    passport_id = request.session.get('passport_id')
    # 订单id: 时间戳+用户id
    order_id = datetime.now().strftime('%Y%m%d%H%M%S') + str(passport_id)
    # 运费
    transit_price = 10
    # 订单商品总数和总金额
    total_count = 0
    total_price = 0

    # 创建一个保存点，这是一个事务
    sid = transaction.savepoint()
    try:
        order = OrderInfo.objects.create(order_id=order_id,
                                        passport_id=passport_id,
                                        addr_id=addr_id,
                                        total_count=total_count,
                                        total_price=total_price,
                                        transit_price=transit_price,
                                        pay_method=pay_method
                                        )
        # 向订单商品标中添加订单商品的记录
        books_ids = books_ids.split(',')
        conn = get_redis_connection('default')
        cart_key = 'cart_%d'%passport_id

        # 遍历获取用户购买的商品信息
        for id in books_ids:
            books = Books.objects.get_books_by_id(books_id = id)
            if books is None:
                transaction.savepoint_rollback(sid)
                return JsonResponse({'res':4,'errmsg':'商品信息错误'})

            # 获取用户购买的商品数目
            count = conn.hget(cart_key,id)

            # 判断商品的库存
            if int(count) > books.stock:
                transaction.savepoint_rollback(sid)
                return JsonResponse({"res":5,"errmsg":'库存不足'})

            # 创建一条定点商品记录
            OrderGoods.objects.create(order_id=order_id,
                                    books_id=id,
                                    count=count,
                                    price=books.price)

            # 更新商品的销量，减少商品的库存
            books.sales += int(count)
            books.stock -= int(count)
            books.save()

            # 累计计算商品的总数目和总金额
            total_count += int(count)
            total_price += int(count) * books.price

        # 累计更新订单的商品总数目和总金额
        order.total_count = total_count
        order.total_price = total_price
        order.save()

        # 累计计算商品的总数目和总金额

    except Exception as e:
        transaction.savepoint_rollback(sid)
        return JsonResponse({'res':7,'errmsg':'服务器错误'})

    conn.hdel(cart_key,*books_ids)

    #事务提交
    transaction.savepoint_commit(sid)
    # 返回应答
    return JsonResponse({'res':6})


def check_pay(request):
    """获取用户支付的结果"""
    if not request.session.has_key('login_line'):
        return JsonResponse({'res':1,'errmsg':''})
    order_id = request.POST.get('order_id')

    # 数局鉴定
    if not order_id:
        return JsonResponse({'res':1,'errmsg':'订单不存在'})

    try:
        order = OrderInfo.objects.get(order_id=order_id,
                                    status=1,
                                    pay_method=3)
    except OrderInfo.DoseNotExist:
        return JsonResponse({'res':2,'errmsg':'订单信息出错'})