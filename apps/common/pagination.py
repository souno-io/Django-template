from rest_framework.pagination import PageNumberPagination


class Thth20PageNumberPagination(PageNumberPagination):
    page_query_param = 'pageNo'
    page_size_query_param = 'pageSize'  # ?pageNo=xx&pageSize=??
    max_page_size = 100  # 最大页数设置

