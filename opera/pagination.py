from django.conf import settings
from rest_framework import pagination
from rest_framework.response import Response


class MyPagination(pagination.PageNumberPagination):

    def get_paginated_response(self, data):
        page_size=20
        page_size_query_param = 'page_size'
        return Response({
            'page_size': self.page_size,
            'total_objects': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'folios': data,
        })