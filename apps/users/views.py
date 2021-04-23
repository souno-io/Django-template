from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from users.models import Menu, Role, UserProfile


@csrf_exempt
@api_view(['GET', 'POST'])
def userinfo(request):
    """
    :param request: title:请求用户信息
    :return: GET:接受的所有title值，POST：具体的数据
    """
    if request.method == "GET":
        permissions = []
        for perm in request.user.get_all_permissions():
            permissions.append(perm)
        roles = []
        print(permissions)
        roles_data = list(Role.objects.filter(user=request.user).values_list('codename'))
        for p in roles_data:
            roles.append(p[0])
        username = UserProfile.objects.get(username=request.user.username).full_name
        avatar = UserProfile.objects.get(username=request.user.username).avatar
        result = {
            "code": 200,
            "msg": "success",
            "results": {
                "roles": roles,
                "ability": permissions,
                "username": username,
                "avatar": str(avatar)
            }
        }
        return Response(result)


@csrf_exempt
@api_view(['GET'])
def user_menu(request):
    """
    :param request: title:请求用户菜单
    """
    menus_list = request.user.get_all_menus()
    menus = [{
        "path": "/",
        "component": "Layout",
        "redirect": "index",
        "children": [
            {
                "path": "index",
                "name": "Index",
                "component": "index/index",
                "meta": {
                    "title": "首页",
                    "icon": 'home-2-line',
                    "affix": True,
                    "noKeepAlive": True
                }
            }
        ]
    }]
    for menu in menus_list:
        if menu.level == 1:
            children = []
            for child in menus_list:
                if child.level == 2:
                    if child.parentcode.codename == menu.codename:
                        grandson = []
                        for grand in menus_list:
                            if grand.level == 3:
                                if grand.parentcode.codename == child.codename:
                                    grandson.append({
                                        "name": grand.codename,
                                        "path": grand.path,
                                        "component": grand.component,
                                        "meta": {
                                            "title": grand.name,
                                            "icon": grand.icon
                                        },
                                    })
                        children.append({
                            "name": child.codename,
                            "path": child.path,
                            "component": child.component,
                            "meta": {
                                "title": child.name,
                                "icon": child.icon
                            },
                            "children": grandson
                        })
            menus.append({
                "name": menu.codename,
                "path": menu.path,
                "component": "Layout",
                "meta": {
                    "title": menu.name,
                    "icon": menu.icon,
                },
                "children": children
            })
    result = {
        "code": 200,
        "msg": "success",
        "results": menus
    }
    return Response(result)


# @csrf_exempt
# def userIndex(request):
#     """
#     :param request: title:首页
#     """
#     return render(request, 'static/web/index.html')


@csrf_exempt
@api_view(['GET'])
def has_menu(request, menu_code):
    """
    :param perm_code: 权限代码
    :param request: title:退出登录
    """
    if request.user.has_menu(menu_code):
        result = {
            "code": 200,
            "msg": "success",
        }
    else:
        result = {
            "code": 403,
            "msg": "failure",
        }
    return Response(result)


@csrf_exempt
@api_view(['GET', 'POST'])
def logout(request):
    """
    :param request: title:退出登录
    """
    result = {
        "code": 200,
        "msg": "success",
    }
    return Response(result)
