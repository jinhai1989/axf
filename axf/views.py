from django.shortcuts import render,redirect
from django.http import JsonResponse,HttpResponse
import time
import random
import os
import uuid
from django.views.decorators.csrf import csrf_exempt #解决ajax 传输数据时csrf_token 错误

from project import settings
from .models import Wheel,Nav,Mustbuy,Shop,MainShow,FoodTypes,Goods,User,Cart,Order
# Create your views here.

def home(request):
    wheelsList = Wheel.objects.all() #轮播图
    navList = Nav.objects.all()
    mustbuyList = Mustbuy.objects.all()
    shopList = Shop.objects.all()
    mainList = MainShow.objects.all()

    content = {
        'title': '主页',
        'wheelsList': wheelsList,
        'navList': navList,
        'mustbuyList':mustbuyList,
        'shop1':shopList[0],
        'shop2':shopList[1:3],
        'shop3':shopList[3:7],
        'shop4':shopList[7:],
        'mainList':mainList,
    }
    return render(request,'axf/home.html',content)



def market(request,categoryid,cid,sortid):
    leftSlider = FoodTypes.objects.all() #获取全部分类
    productList = Goods.objects.filter(categoryid = categoryid) #获取某一分类下的所有数据
    if cid != '0': #当子分类不为0时
        productList = productList.filter(childcid=cid) #获取子分类数据

    #排序
    if sortid == '1':
        productList = productList.order_by("productnum")
    elif sortid == '2':
        productList = productList.order_by("price")
    elif sortid == '3':
        productList = productList.order_by("-price")
    #获取某一分类
    group = leftSlider.get(typeid = categoryid)
    childNameList = []
    #group.childtypenames获取到的数据 ----> 全部分类:0#进口水果:103534#国产水果:103533
    arr1 = group.childtypenames.split('#')
    for str in arr1:
        #全部分类：0
        arr2 = str.split(":")
        obj = {"childName":arr2[0],"childId":arr2[1]}
        childNameList.append(obj)

    cartlist = []
    token = request.session.get("token")
    if token:
        user = User.objects.get(userToken = token)
        cartlist = Cart.objects.filter(userAccount = user.userAccount)

    for p in productList:
        for c in cartlist:
            if c.productid == p.productid:
                #条件成立，为p 增加num 属性
                p.num = c.productnum
                continue
    content = {
        'title': '闪送超市',
        'leftSlider':leftSlider,
        'productList':productList,
        'childNameList':childNameList,
        'categoryid':categoryid,
        'cid':cid,
    }
    return render(request,'axf/market.html',content)



#--------------购物车-----------------#
def cart(request):

    #判断用户是否的登录
    token = request.session.get("token")
    if token == None:#未登录
        return redirect('/login/')

    user = User.objects.get(userToken=token)
    cartslist = Cart.objects.filter(userAccount = user.userAccount,isDelete=False)
    content = {
        'title':'购物车',
        'cartslist':cartslist,
    }
    return render(request,'axf/cart.html',content)

#修改购物车
@csrf_exempt
def changecart(request,flag):
    #判断用户是否的登录
    token = request.session.get("token")
    # print(token)
    if token == None:
        # return redirect('/login/') #不能用这种方式跳转，需要用JsonResponse 传数据给js,让js 完成重定向
        return JsonResponse({"data":-1,"status":"error"})

    productid = request.POST.get("productid",None)
    user = User.objects.get(userToken = token)
    product = Goods.objects.get(productid = productid)
    # print(productid)
    # 加
    if flag == "0":
        if product.storenums == 0:
            return JsonResponse({"data": -2, "status": "error"})
        carts  = Cart.objects.filter(userAccount = user.userAccount)
        if carts.count() == 0:
            #直接增加一条购物数据
            #                       userAccount, productid,productnum,productprice,isChose,productimg,productname,isDelete
            c = Cart.createcart(user.userAccount,productid,1,product.price,False,product.productimg,product.productname,False)
            c.save()
        else:
            try:
                c = carts.get(productid = productid)
                #修改 购物数据 的数量和总价
                c.productnum += 1
                c.productprice = "%.2f"%(float(product.price)*c.productnum)
                c.save()
            except Cart.DoesNotExist as e:
                # 增加一条购物数据
                c = Cart.createcart(user.userAccount, productid, 1, product.price, False, product.productimg,product.productname, False)
                c.save()
        print(c.productnum)
        product.storenums -=1
        product.save()
        return JsonResponse({"data": c.productnum,"price":c.productprice, "status": "success"})

    # 减
    elif flag == "1":
        carts  = Cart.objects.filter(userAccount = user.userAccount)
        if carts.count() == 0:
            return JsonResponse({"data": -2, "status": "success"})
        else:
            try:
                c = carts.get(productid = productid)
                #修改 购物数据 的数量和总价
                c.productnum -= 1
                if c.productnum == 0 :
                    c.delete()
                else:
                    c.productprice = "%.2f"%(float(product.price)*c.productnum)
                    c.save()

            except Cart.DoesNotExist as e:
                return JsonResponse({"data":-2, "status": "success"})

        product.storenums +=1
        product.save()
        return JsonResponse({"data": c.productnum,"price":c.productprice, "status": "success"})


    # 是否选中
    elif flag == "2":
        # print("2222")
        carts = Cart.objects.filter(userAccount=user.userAccount) #获取登录用户的购物车信息
        c = carts.get(productid=productid) #获取选商品信息
        c.isChose = not c.isChose #变更选择属性，True  False
        c.save()
        str = ""
        if c.isChose:
            # print('11111')
            str = "√"
        return JsonResponse({"data":str,"status": "success"})

    #全选
    elif flag == "3":
        carts = Cart.objects.filter(userAccount=user.userAccount)  # 获取登录用户的购物车信息
        chose = True
        str = ''
        for c in carts:  # 循环获取选商品信息
            if not c.isChose:
                chose = False
                break

        if chose:
            for c in carts:
                c.isChose = False
                c.save()
            str = ''
        else:
            for c in carts:
                c.isChose = True
                c.save()
            str = '√'
        return JsonResponse({"data": str, "status": "success"})


# 提交订单
@csrf_exempt
def saveorder(request):
    #判断用户是否的登录
    token = request.session.get("token")
    # print(token)
    if token == None:
        return JsonResponse({"data": -1, "status": "error"})

    user = User.objects.get(userToken=token)
    carts = Cart.objects.filter(isChose = True) #获取所有已选择的购物车商品数据
    if carts.count() == 0: #没有数据，
        return JsonResponse({"data": -1, "status": "error"})

    oid = str(random.randint(1,10000)) + str(int(time.time()))
    o = Order.createorder(oid,user.userAccount,0,)
    o.save()
    for item in carts: #修改购物车信息
        item.isDelete = True
        item.orderid = oid
        item.save()
    return JsonResponse({"status": "success"})




#-------------我的-----------------#
def mine(request):
    username = request.session.get("username","未登录")
    content = {
        'title':'我的',
        'username':username,
    }
    return render(request,'axf/mine.html',content)

#登录
from .forms.login import LoginForm
def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            #信息没有大问题，验证账号和密码是否正确
            username = form.cleaned_data["username"]
            passwd = form.cleaned_data["passwd"]
            try:
                user = User.objects.get(userAccount = username)
                if user.userPasswd != passwd:
                    return redirect('/login/')
            except User.DoesNotExist as e:
                return redirect('/login/')

            #登陆成功

            user.userToken = str(time.time()) + str(random.randint(55, 999999))
            user.save()

            request.session["username"] = user.userName
            request.session["token"] = user.userToken
            return redirect('/mine/')
        else:
            return render(request,'axf/login.html',{"title":"登录",
                                                    "form":form,
                                                    "error":form.errors})
    else:
        form = LoginForm()
        return render(request, 'axf/login.html', {"title": "登录",
                                                  "form": form})

#退出
from django.contrib.auth import logout
def quit(request):
    logout(request)
    return redirect('/mine/')


#---------------------注册-----------------------------
def register(request):
    if request.method == "POST":
        userAccount = request.POST.get("userAccount")
        userPasswd  = request.POST.get("userPasswd")
        userName    = request.POST.get("userName")
        userPhone    = request.POST.get("userPhone")
        userAdderss = request.POST.get("userAdderss")
        userRank    = 0
        userToken   = str(time.time()) + str(random.randint(55,999999))

        file = request.FILES['userImg']
        imgSuffix = file.name.split(".")[-1] #获取后缀名
        # imgname = str(uuid.uuid4()) + '.' + imgSuffix
        imgname = userAccount + '.' + imgSuffix
        userImg = os.path.join(settings.MDEIA_ROOT,imgname)

        with open(userImg,"wb") as fp:
            for data in file.chunks():
                fp.write(data)

        user = User.createuser(userAccount,userPasswd,userName,userPhone,userAdderss,userImg,userRank,userToken)
        user.save()

        request.session["username"] = userName
        request.session["token"] = userToken

        return redirect('/mine/')

    return render(request,'axf/register.html',{"title":"注册"})

#用户账号验证
@csrf_exempt #解决ajax 传输数据时csrf_token 错误
def checkuserid(request):
    userid = request.POST.get("userid") #获取页面输入字段
    try:
        user = User.objects.get(userAccount=userid) #可以按条件获取数据说明用户名已在数据库内
        json = {"data":"用户已存在","status":"error"}
    except User.DoesNotExist as e: #无法获取数据，说明用户名没有被占用
        json = {"data": "可以注册", "status": "success"}
    return JsonResponse(json)