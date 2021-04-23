from django.db import connections
from .month import Month
from string import Template
from django.core import serializers
from .his import His


def interface_utils(request, models, SQL):
    print(SQL.keys())
    results = {}
    if request.method == "GET":
        try:
            keys = list(SQL.keys())
            for i in keys:
                results[i] = SQL[i]['name']
        except Exception as e:
            results = {
                'status': 10022,
                'results': None,
                'message': '获取参数列表失败！'
            }
    if request.method == "POST":
        # json_result = json.loads(request.data)
        json_result = request.data
        try:
            if 'update' in json_result and json_result['update'] is True and SQL[json_result['title']]['model'] is not None:
                if 'year' in json_result and 'month' in json_result:
                    first_day = str(Month(int(json_result['year']), int(json_result['month'])).first_day())
                    last_day = str(Month(int(json_result['year']), int(json_result['month'])).next_month().first_day())
                    date_str = dict(start_date=first_day, end_date=last_day)
                    print(date_str)
                    sql = Template(SQL[json_result['title']]['sql']).substitute(date_str)
                    # print(sql)
                else:
                    sql = SQL[json_result['title']]['sql']
                model = getattr(models, SQL[json_result['title']]['model'])
                with His(sql) as query_his:
                    qs = query_his.rows_as_dicts()
                # print(qs)
                if 'year' in json_result and 'month' in json_result:
                    qs[0]['YUEFEN'] = str(json_result['year']) + '-' + str(json_result['month'])
                print(qs)
                if type(qs) == str:
                    results = {
                        'status': 10022,
                        'message': '获取数据失败！',
                        'title': SQL[json_result['title']]['name'],
                        'results': qs
                    }
                else:
                    for i in qs:
                        model.objects.create(**i)
                        results = {
                            'status': 200,
                            'message': '写入数据成功！',
                            'title': SQL[json_result['title']]['name'],
                            'results': serializers.serialize('python', model.objects.order_by("-id")[:1])
                        }
            else:
                with His(SQL[json_result['title']]['sql']) as query_his:
                    qs = query_his.rows_as_dicts()
                results = {
                    'code': 200,
                    'message': '获取数据成功！',
                    'title': SQL[json_result['title']]['name'],
                    'results': qs
                }
        except KeyError as e:
            results = {
                'status': 10022,
                'results': None,
                'message': '传入的值错误，请检查！',
                'title': str(e)
            }
    return results
