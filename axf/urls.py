"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url

from . import views
urlpatterns = [
    url(r'^home/$',views.home,name="home" ),#主页
    url(r'^market/(\d+)/(\d+)/(\d+)/$',views.market,name="market" ),#超市
    url(r'^cart/$',views.cart,name="cart" ),#购物车
    url(r'^changecart/(\d+)/$',views.changecart,name="changecart" ),#修改购物车
    url(r'^saveorder/$',views.saveorder,name="saveorder" ),#递交订单

    url(r'^mine/$',views.mine,name="mine" ),#我的
    url(r'^login/$',views.login,name="login" ),#登录
    url(r'^register/$',views.register,name="register" ),#注册
    #验证用户账号是否存在
    url(r'^checkuserid/$',views.checkuserid,name="checkuserid" ),
    url(r'^quit/$',views.quit,name="quit" ),
]
