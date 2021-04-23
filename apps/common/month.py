# ================================
# 实现了月份对象，以及月份MonthField模型字段
# 叶兴（souno）
# 2021年 4月 7号
# ================================
import datetime
import decimal
import json
import uuid

from django.db import models
from django import forms
from django.core import exceptions
from django.utils.duration import duration_iso_string
from django.utils.functional import Promise
from django.utils.timezone import is_aware
from django.utils.translation import ugettext_lazy as _
from datetime import date
from django.forms import widgets
from django.utils.dates import MONTHS
from django.templatetags.static import static
import sys

PY3 = sys.version_info >= (3,)

if PY3:
    string_type = str


def days(days):
    return datetime.timedelta(days=days)


class Month(object):
    """
    定义的月份类对象，用于对月份的管理，next_month获取下一个月，
    prev_month获取上一个月，
    first_day当月第一天，
    last_day当月最后一天
    """
    def __init__(self, year, month):
        self.year = year
        self.month = month
        self._date = datetime.date(year=self.year, month=self.month, day=1)

    @classmethod
    def from_int(cls, months):
        y, m = divmod(months, 12)
        m += 1
        return cls(y, m)

    @classmethod
    def from_date(cls, date):
        return cls(date.year, date.month)

    @classmethod
    def from_string(cls, date):
        y = int(date[:4])
        m = int(date[5:7])
        return cls(y, m)

    def __add__(self, x):
        """x应为一个整数"""
        return Month.from_int(int(self) + x)

    def __sub__(self, x):
        """x可以是一个证书或者Month实例"""
        if isinstance(x, Month):
            return int(self) - int(x)
        else:
            return Month.from_int(int(self) - int(x))

    def next_month(self):
        return self + 1

    def prev_month(self):
        return self - 1

    def first_day(self):
        return self._date

    def last_day(self):
        return self.next_month().first_day() - days(1)

    def __int__(self):
        return self.year * 12 + self.month - 1

    def __contains__(self, date):
        return self == date

    def __eq__(self, x):
        if isinstance(x, Month):
            return x.month == self.month and x.year == self.year
        if isinstance(x, datetime.date):
            return self.year == x.year and self.month == x.month
        if isinstance(x, int):
            return x == int(self)
        if isinstance(x, string_type):
            return str(self) == x[:7]

    def __gt__(self, x):
        if isinstance(x, Month):
            if self.year != x.year: return self.year > x.year
            return self.month > x.month
        if isinstance(x, datetime.date):
            return self.first_day() > x
        if isinstance(x, int):
            return int(self) > x
        if isinstance(x, string_type):
            return str(self) > x[:7]

    def __ne__(self, x):
        return not self == x

    def __le__(self, x):
        return not self > x

    def __ge__(self, x):
        return (self > x) or (self == x)

    def __lt__(self, x):
        return not self >= x

    def __str__(self):
        return '%s-%02d' % (self.year, self.month)

    def __unicode__(self):
        return self.__str__()

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.datestring())

    def datestring(self):
        return self.first_day().isoformat()

    isoformat = datestring

    def range(self, x):
        """x必须是大于self的Month的实例。返回构成从self到x（包括x）的时间跨度的Month对象的列表"""
        months_as_ints = range(int(self), int(x) + 1)
        return [Month.from_int(i) for i in months_as_ints]

    def strftime(self, fmt):
        return self._date.strftime(fmt)


class MonthJSONEncoder(json.JSONEncoder):
    """JSONEncoder子类，它知道如何对月份日期时间，十进制类型和UUID进行编码。"""
    def default(self, o):
        # See "Date Time String Format" in the ECMA-262 specification.
        if isinstance(o, datetime.datetime):
            r = o.isoformat()
            if o.microsecond:
                r = r[:23] + r[26:]
            if r.endswith('+00:00'):
                r = r[:-6] + 'Z'
            return r
        elif isinstance(o, datetime.date):
            return o.isoformat()
        elif isinstance(o, datetime.time):
            if is_aware(o):
                raise ValueError("JSON can't represent timezone-aware times.")
            r = o.isoformat()
            if o.microsecond:
                r = r[:12]
            return r
        elif isinstance(o, datetime.timedelta):
            return duration_iso_string(o)
        elif isinstance(o, Month):
            return o.__str__()
        elif isinstance(o, (decimal.Decimal, uuid.UUID, Promise)):
            return str(o)
        else:
            return super().default(o)


class MonthSelectorWidget(widgets.MultiWidget):
    def __init__(self, attrs=None):
        # create choices for days, months, years
        _attrs = attrs or {}  # default class
        _attrs['class'] = (_attrs.get('class', '') + ' w-month-year').strip()
        _widgets = [widgets.Select(attrs=_attrs, choices=MONTHS.items())]
        _attrs['class'] += " w-year"
        _widgets.append(widgets.NumberInput(attrs=_attrs))
        super(MonthSelectorWidget, self).__init__(_widgets, attrs)

    @property
    def media(self):
        media = self._get_media()
        media.add_css({
            'screen': (static('month/field/widget_month.css'),)
        })
        return media

    def decompress(self, value):
        if value:
            if isinstance(value, string_type):
                m = int(value[5:7])
                y = int(value[:4])
                return [m, y]
            return [value.month, value.year]
        return [None, None]

    def format_output(self, rendered_widgets):
        return ''.join(rendered_widgets)

    def value_from_datadict(self, data, files, name):
        datelist = [
            widget.value_from_datadict(data, files, name + '_%s' % i)
            for i, widget in enumerate(self.widgets)]
        try:
            D = date(day=1, month=int(datelist[0]),
                     year=int(datelist[1]))
        except ValueError:
            return ''
        else:
            return str(D)


class MonthField(models.DateField):
    description = "A specific month of a specific year."
    widget = MonthSelectorWidget

    default_error_messages = {
        'invalid_year': _("Year informed invalid. Enter at least 4 digits."),
    }

    def to_python(self, value):
        if isinstance(value, Month):
            month = value
        elif isinstance(value, datetime.date):
            month = Month.from_date(value)
            if len(str(month.year)) < 4:
                raise exceptions.ValidationError(
                    self.error_messages['invalid_year'],
                    code='invalid_year',
                    params={'value': value},
                )
        elif isinstance(value, string_type):
            month = Month.from_string(value)
        else:
            month = None
        return month

    def get_prep_value(self, value):
        month = self.to_python(value)
        if month is not None:
            return month.first_day()
        return None

    def from_db_value(self, value, expression, connection):
        return self.to_python(value)

    def clean(self, value, instance):
        return self.to_python(value)

    def formfield(self, **kwargs):
        # The widget is allready being specified somewhere by models.DateField...
        kwargs['widget'] = self.widget
        defaults = {
            'form_class': MonthField
        }
        defaults.update(kwargs)
        return super(MonthField, self).formfield(**defaults)
