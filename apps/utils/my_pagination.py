from collections import OrderedDict

from django.core.paginator import Paginator
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


# 1, 自定义分页对象
class MyPageNumberPagination(PageNumberPagination):
    # 1, 可以在前端指定页面数据大小
    page_size_query_param = "page_size"

    # 2, 限制页面最大的数量
    max_page_size = 100
    page_size = 10

    # 重写响应值的方法
    def get_paginated_response(self, data):
        paginator: Paginator = self.page.paginator
        return Response(OrderedDict([
            ('count', paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('page', self.page.number),
            ('pages', self.page.paginator.num_pages),
            ('lists', data)
        ]))
