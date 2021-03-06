# 编写装饰器检查用户是否登录
import time

from django.contrib.auth.hashers import check_password
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from Pro import settings
from django.core.mail import send_mail
from Login.models import get_token
from Login.models import User


def check_login(func):
    def inner(request, *args, **kwargs):
        # next_url = request.get_full_path()
        # 获取session判断用户是否已登录
        if request.session.get('is_login'):
            # 已经登录的用户...
            return func(request, *args, **kwargs)
        else:
            #   没有登录的用户，跳转刚到登录页面
            return redirect("login")
            # return redirect(reverse('profile', error =  "请先登录"))

    return inner


def register(request):
    return render(request, 'register.html')



# @csrf_exempt
def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        # next_url = request.POST.get('next_url')
        remember_sign = request.POST.get("check")

        print(email, password)

        isuser = User.objects.filter(email=email).first()

        print(isuser)
        print(isuser.password)

        if isuser and check_password(password, isuser.password):
            print('ok')
        # if email == '872039610@qq.com' and password == '123'r:
            request.session['user_info'] = {
                'email': email,
                'password': password,
                'username':isuser.username
            }
            request.session['is_login'] = True

            if remember_sign == 'on':
                print('记住密码')
                request.session['is_remember'] = True
            else:
                request.session['is_remember'] = False

            # if next_url and next_url != 'logout/':
            #     response = redirect(next_url)
            # else:
            #     response = redirect('index')
            return redirect('index2')
        else:
            error_msg = '登录失败，请重试'
            return render(request, "login.html", {'error_msg': error_msg})

    # next_url = request.GET.get("next", '')
    # print(next_url)
    # 检查是否勾选了记住密码功能
    password, check_value = '', ''
    user_session = request.session.get('user_info', {})
    email = user_session.get('email', '')
    if request.session.get('is_remember'):
        password = user_session.get('password', '')
        check_value = 'checked'
    return render(request, "login.html", {
        # 'next_url': next_url,
        'email': email,
        'password': password,
        'check_value': check_value
    })


def logout(request):
    rep = redirect("login")
    # request.session.delete()
    # 登出，则删除掉session中的某条数据
    if 'is_login' in request.session:
        del request.session['is_login']
    return rep


# @check_login
def index(request):
    return render(request, "index.html")


# @check_login
def index2(request):
    if request.method == 'POST':
        box = request.POST.getlist('checkboxBtn')
        for b in box:
            print(b)
            user = User.objects.get(id=b)
            user.isdelete = True
            user.save()
        return redirect('index2')
    return render(request, 'index2.html', {"user_all" : User.objects.all().filter(isdelete=False)})


def test(request, token):
    pass
    # User.objects.create(email='872039610@qq.com', password='123456', username='张三')
    # User.objects.create(email='5772027@qq.com', password='123456', username='李四')
    # User.objects.create(email='1232143546@qq.com', password='123456', username='王麻子')
    # User.objects.create(email='1546123477@qq.com', password='123456', username='袁滨心')
    # return HttpResponse('测试数据添加完成')


def delete(request):
    print('我进来了')
    print(request.POST.get("checkboxBtn"))
    # return redirect('index2')


def send_email(request):
    token = get_token(settings.TOKEN_KEY)
    t = time.localtime(time.time() + 180)
    text = f"链接有效期为3分钟!<a href='{token}'>点我激活</a>,请在{t[0]}年{t[1]}月{t[2]}日{t[3]}时{t[4]}分{t[5]}秒前激活！"
    try:
        send_mail(
            subject='注册激活链接',
            message=text,
            from_email='872039610@qq.com',
            recipient_list=['872039610@qq.com'],
            fail_silently=False
        )

        rep = {'code' : 200}
    except:
        rep = {'code' : 300, 'msg' : '发送失败'}

    return JsonResponse(rep)

