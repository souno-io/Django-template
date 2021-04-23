import xadmin
from xadmin import views
from .models import UserProfile, Role, Menu, Department, Permission
from django.utils.translation import gettext_lazy as _
# from django.contrib.auth.admin import UserAdmin
from xadmin.plugins.auth import PermissionModelMultipleChoiceField

ACTION_NAME = {
    'add': _('Can add %s'),
    'change': _('Can change %s'),
    'edit': _('Can edit %s'),
    'delete': _('Can delete %s'),
    'view': _('Can view %s'),
}


def get_Menu_name(p):
    action = p.codename.split('_')[0]
    if action in ACTION_NAME:
        return ACTION_NAME[action] % str(p.content_type)
    else:
        return p.name


class UserProfileAdmin(object):
    list_display = ['id', 'username', 'full_name', 'email', 'date_joined', 'is_active', 'is_staff']
    search_fields = ['id', 'username', 'full_name', 'email', 'date_joined', 'is_active', 'is_staff']
    list_filter = ['id', 'username', 'full_name', 'email', 'date_joined', 'is_active', 'is_staff']
    model_icon = "fa fa-id-card-o"


class RolesAdmin(object):
    search_fields = ('name',)
    ordering = ('name',)
    style_fields = {'permissions': 'm2m_transfer'}
    model_icon = 'fa fa-group'
    list_display = ('name', 'codename', 'menus')

    def get_field_attrs(self, db_field, **kwargs):
        attrs = super(RolesAdmin, self).get_field_attrs(db_field, **kwargs)
        if db_field.name == 'permissions':
            attrs['form_class'] = PermissionModelMultipleChoiceField
        return attrs


class DepartmentsAdmin(object):
    search_fields = ('name',)
    ordering = ('name',)
    style_fields = {'permissions': 'm2m_transfer'}
    model_icon = 'fa fa-desktop'
    list_display = ('name', 'codename', 'parent', 'is_active', 'remark')


class MenuAdmin(object):

    def show_name(self, p):
        return get_Menu_name(p)

    show_name.short_description = _('Menu Name')
    show_name.is_column = True

    model_icon = 'fa fa-bars'
    list_display = ('name', 'codename', 'level', 'parentcode')


class PermissionAdmin(object):

    def show_name(self, p):
        return get_Menu_name(p)

    show_name.short_description = _('Permission Name')
    show_name.is_column = True

    model_icon = 'fa fa-lock'
    list_display = ('name', 'codename', 'is_active', 'remark')


class GlobalSettings(object):
    site_title = "操作后台"  # 页眉
    site_footer = "souno.cn"  # 页脚
    # menu_style = 'accordion'  # 左侧样式


class BaseSetting(object):
    enable_themes = True
    use_bootswatch = True


xadmin.site.register(views.BaseAdminView, BaseSetting)
xadmin.site.register(views.CommAdminView, GlobalSettings)
# xadmin.site.unregister(UserProfile)
xadmin.site.register(Role, RolesAdmin)
xadmin.site.register(Menu, MenuAdmin)
xadmin.site.register(UserProfile, UserProfileAdmin)
xadmin.site.register(Department, DepartmentsAdmin)
xadmin.site.register(Permission, PermissionAdmin)
