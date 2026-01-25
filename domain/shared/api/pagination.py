"""
Custom pagination classes.
"""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class BasePagination(PageNumberPagination):
    """
    Base pagination class with consistent response format.
    """

    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        """Return paginated response with metadata."""
        return Response(
            {
                "success": True,
                "data": data,
                "pagination": {
                    "count": self.page.paginator.count,
                    "total_pages": self.page.paginator.num_pages,
                    "current_page": self.page.number,
                    "page_size": self.get_page_size(self.request),
                    "has_next": self.page.has_next(),
                    "has_previous": self.page.has_previous(),
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
            }
        )

    def get_paginated_response_schema(self, schema):
        """Schema for OpenAPI documentation."""
        return {
            "type": "object",
            "properties": {
                "success": {"type": "boolean", "example": True},
                "data": schema,
                "pagination": {
                    "type": "object",
                    "properties": {
                        "count": {"type": "integer", "example": 100},
                        "total_pages": {"type": "integer", "example": 5},
                        "current_page": {"type": "integer", "example": 1},
                        "page_size": {"type": "integer", "example": 20},
                        "has_next": {"type": "boolean", "example": True},
                        "has_previous": {"type": "boolean", "example": False},
                        "next": {"type": "string", "nullable": True},
                        "previous": {"type": "string", "nullable": True},
                    },
                },
            },
        }


class StandardPagination(BasePagination):
    """Standard pagination - 20 items per page."""

    page_size = 20


class LargePagination(BasePagination):
    """Large pagination - 50 items per page."""

    page_size = 50


class SmallPagination(BasePagination):
    """Small pagination - 10 items per page."""

    page_size = 10
