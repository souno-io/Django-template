import os

# from django.contrib import auth
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils import timezone
from django.contrib.auth.models import UserManager
from django.db import models
from uuid import uuid4
from django.utils.deconstruct import deconstructible


# 用于获取全部菜单
def _user_all_menus(user):
    menus_role = list(Menu.objects.filter(role__in=Role.objects.filter(user=user)).order_by('seq'))
    menus_user = list(Menu.objects.filter(user=user).order_by('seq'))
    menus_depart = list(Menu.objects.filter(department__in=Department.objects.filter(user=user)).order_by('seq'))
    return menus_role + menus_user + menus_depart


# 用于获取全部菜单
def _user_all_permissions(user):
    permissions_role = list(Permission.objects.filter(role__in=Role.objects.filter(user=user)).order_by('-id'))
    permissions_user = list(Permission.objects.filter(user=user).order_by('-id'))
    permissions_depart = list(
        Permission.objects.filter(department__in=Department.objects.filter(user=user)).order_by('-id'))
    return permissions_role + permissions_user + permissions_depart


# A few helper functions for common logic between User and AnonymousUser.
def _user_get_menus(user, obj, from_name):
    menus = []
    if from_name == 'user':
        menus = list(Menu.objects.filter(user=user).order_by('seq'))
    elif from_name == 'role':
        menus = list(Menu.objects.filter(role__in=Role.objects.filter(user=user)).order_by('seq'))
    elif from_name == 'depart':
        menus = list(
            Menu.objects.filter(department__in=Department.objects.filter(user=user)).order_by('seq'))
    elif from_name == 'all':
        for perm_role in _user_all_menus(user):
            if perm_role not in menus:
                menus.append(perm_role)
    else:
        return []
    return menus


def _user_get_permissions(user, obj, from_name):
    permissions = []
    if from_name == 'user':
        permissions = list(Permission.objects.filter(user=user).order_by('-id'))
    elif from_name == 'role':
        permissions = list(
            Permission.objects.filter(role__in=Role.objects.filter(user=user)).order_by('-id'))
    elif from_name == 'depart':
        permissions = list(
            Permission.objects.filter(department__in=Department.objects.filter(user=user)).order_by('-id'))
    elif from_name == 'all':
        for perm_role in _user_all_permissions(user):
            if perm_role not in permissions:
                permissions.append(perm_role.codename)
    else:
        return []
    return permissions


def _user_has_menu(user, perm, obj):
    """
    A backend can raise `PermissionDenied` to short-circuit permission checking.
    """
    menus = []
    for perm_role in _user_all_menus(user):
        if perm_role not in menus:
            menus.append(perm_role)
    for menu in menus:
        if perm == menu.codename:
            return True
        return False


def _user_has_perm(user, perm, obj):
    """
    A backend can raise `PermissionDenied` to short-circuit permission checking.
    """
    permissions = []
    for perm_role in _user_all_permissions(user):
        if perm_role not in permissions:
            permissions.append(perm_role)
    for menu in permissions:
        if perm == menu.codename:
            return True
        return False


class Permission(models.Model):
    """
    权限表
    """
    codename = models.CharField(_('codename'), max_length=100, unique=True, null=False, blank=False)
    name = models.CharField(_('name'), max_length=255, unique=True, null=False, blank=False)
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting department.'
        ),
    )
    remark = models.CharField('描述', max_length=255, null=True, blank=True, help_text='描述')

    # objects = PermissionManager()

    class Meta:
        verbose_name = _('权限')
        verbose_name_plural = _('权限')
        unique_together = [['name', 'codename']]
        ordering = ['name', 'codename']

    def __str__(self):
        return '%s | %s' % (self.name, self.codename)


class Menu(models.Model):
    """
    菜单表
    """
    LEVEL_TYPE = (
        (1, "一级权限"),
        (2, "二级权限"),
        (3, "三级权限"),
    )
    codename = models.CharField(_('codename'), max_length=100, unique=True, null=False, blank=False)
    name = models.CharField(_('name'), max_length=255, unique=True, null=False, blank=False)
    icon = models.CharField('图标', max_length=100, help_text='图标', default=None, null=True, blank=True)
    level = models.IntegerField(choices=LEVEL_TYPE, verbose_name="级别", help_text="类目级别")
    parentcode = models.ForeignKey('self', verbose_name=_('上级权限'), null=True, blank=True,
                                   max_length=100, related_name="perm_parent", on_delete=models.CASCADE)
    path = models.CharField('路径', max_length=100, help_text='路径', default=None, null=True, blank=True)
    component = models.CharField('组件路径', max_length=100, help_text='组件路径', default=None, null=True, blank=True)
    seq = models.CharField('排序', max_length=100, help_text='排序', default=None, null=True, blank=True)
    remark = models.CharField('描述', max_length=255, null=True, blank=True, help_text='描述')

    # objects = PermissionManager()

    class Meta:
        verbose_name = _('菜单')
        verbose_name_plural = _('菜单')
        unique_together = [['name', 'codename']]
        ordering = ['name', 'codename']

    def __str__(self):
        return '%s | %s' % (self.name, self.codename)


class Role(models.Model):
    name = models.CharField('角色名', max_length=255, null=False, blank=False, help_text='角色名称')
    menus = models.ManyToManyField(
        Menu,
        verbose_name=_('菜单'),
        blank=True,
    )
    permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('权限'),
        blank=True,
    )
    codename = models.CharField(_('codename'), max_length=100, null=False, blank=False, help_text='角色代码')
    remark = models.CharField('描述', max_length=255, null=True, blank=True, help_text='描述')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "角色"
        verbose_name_plural = verbose_name


class Department(models.Model):
    name = models.CharField('部门名称', max_length=100, null=False, blank=False, help_text='部门名称')
    codename = models.CharField("部门代码", max_length=50, null=False, blank=False, help_text='部门代码')
    parent = models.ForeignKey("self", verbose_name=_('上级部门'), null=True, blank=True,
                               related_name="depart_parent",
                               on_delete=models.CASCADE)
    menus = models.ManyToManyField(
        Menu,
        verbose_name=_('菜单'),
        blank=True,
    )
    permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('权限'),
        blank=True,
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting department.'
        ),
    )
    remark = models.CharField('描述', max_length=255, null=True, blank=True, help_text='描述')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "科室"
        verbose_name_plural = verbose_name


class PermissionsMixin(models.Model):
    """
    Add the fields and methods necessary to support the Group and Permission
    models using the ModelBackend.
    """
    is_superuser = models.BooleanField(
        _('superuser status'),
        default=False,
        help_text=_(
            'Designates that this user has all permissions without '
            'explicitly assigning them.'
        ),
    )
    roles = models.ManyToManyField(
        Role,
        verbose_name=_('Roles'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="user_set",
        related_query_name="user",
    )
    user_menus = models.ManyToManyField(
        Menu,
        verbose_name=_('用户菜单'),
        blank=True,
        help_text=_('Specific menus for this user.'),
        related_name="user_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('用户权限'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="user_set",
        related_query_name="user",
    )
    departments = models.ForeignKey(
        Department,
        null=True,
        verbose_name=_('Departments'),
        blank=True,
        help_text=_(
            'The Departments this user belongs to. A user will get all permissions '
            'granted to each of their Departments.'
        ),
        related_name="user_set",
        related_query_name="user",
        on_delete=models.CASCADE
    )

    class Meta:
        abstract = True

    def get_user_menus(self, obj=None):
        """
        返回该用户直接拥有的权限字符串列表。
        查询所有可用的身份验证后端。
        如果传入对象，则仅返回与此对象匹配的权限。
        """
        return _user_get_menus(self, obj, 'user')

    def get_role_menus(self, obj=None):
        return _user_get_menus(self, obj, 'role')

    def get_depart_menus(self, obj=None):
        return _user_get_menus(self, obj, 'depart')

    def get_all_menus(self, obj=None):
        return _user_get_menus(self, obj, 'all')

    def has_menu(self, perm, obj=None):
        """
        如果用户具有指定的权限，则返回True。
        查询所有可用的身份验证后端，但是如果任何后端返回True，则立即返回。
        因此，通常假定具有来自单个auth后端的权限的用户具有权限。
        如果提供了一个对象，请检查该对象的权限。
        """
        # 活动的超级用户拥有所有权限。
        if self.is_active and self.is_superuser:
            return True

        # Otherwise we need to check the backends.
        return _user_has_menu(self, perm, obj)

    def get_user_permissions(self, obj=None):
        """
        返回该用户直接拥有的权限字符串列表。
        查询所有可用的身份验证后端。
        如果传入对象，则仅返回与此对象匹配的权限。
        """
        return _user_get_permissions(self, obj, 'user')

    def get_role_permissions(self, obj=None):
        return _user_get_permissions(self, obj, 'role')

    def get_depart_permissions(self, obj=None):
        return _user_get_permissions(self, obj, 'depart')

    def get_all_permissions(self, obj=None):
        return _user_get_permissions(self, obj, 'all')

    def get_department(self):
        return self.departments

    def has_perm(self, perm, obj=None):
        """
        如果用户具有指定的权限，则返回True。
        查询所有可用的身份验证后端，但是如果任何后端返回True，则立即返回。
        因此，通常假定具有来自单个auth后端的权限的用户具有权限。
        如果提供了一个对象，请检查该对象的权限。
        """
        # 活动的超级用户拥有所有权限。
        if self.is_active and self.is_superuser:
            return True

        # Otherwise we need to check the backends.
        return _user_has_perm(self, perm, obj)

    def has_module_perms(self, app_label):
        """
        Return True if the user has any permissions in the given app label.
        Use similar logic as has_perm(), above.
        """
        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True

        return False


@deconstructible
class PathAndRename(object):

    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        # set filename as random string
        filename = '{}.{}'.format(uuid4().hex, ext)
        # return the whole path to the file
        return os.path.join(self.path, filename)


class UserProfile(AbstractBaseUser, PermissionsMixin):
    path_and_rename = PathAndRename("avatar/" + timezone.now().strftime("%Y-%m-%d") + "/")
    username_validator = UnicodeUsernameValidator()
    id = models.AutoField(u'用户编号', primary_key=True)
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    full_name = models.CharField(_('姓名'), max_length=60, null=False, blank=False, help_text='姓名')
    # depart_id = models.ForeignKey('Department', related_name='depart_id', verbose_name=u"部门", on_delete=models.CASCADE,null=True, help_text='所属部门')
    mobile = models.CharField(u'电话号码', max_length=20, unique=True, blank=True, null=True, default=None,
                              help_text='电话号码')
    sid_num = models.CharField(u'身份证号', max_length=18, unique=True, blank=True, null=True, default=None,
                               help_text='身份证号')
    avatar = models.ImageField(u'用户头像', upload_to=path_and_rename, blank=True, null=True, unique=False, default=None,
                               help_text='用户头像')
    is_doctor = models.BooleanField(u'是否医生', unique=False, blank=False, null=True, default=False, help_text='是否医生')
    email = models.EmailField('邮件地址', max_length=150, blank=True, help_text='用于登录验证的邮件地址')
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    data_update = models.DateTimeField(_('date update'), auto_now=True)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        # swappable = 'AUTH_USER_MODEL'
        verbose_name = "用户"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username
