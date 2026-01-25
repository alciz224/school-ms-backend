"""
Base view classes and utilities.
"""

from rest_framework.views import APIView
from rest_framework.response import Response


class BaseAPIView(APIView):
    """Base API view with common utilities."""

    def success_response(self, data=None, message=None, status=200):
        """Return a standardized success response."""
        response = {"success": True}
        if message:
            response["message"] = message
        if data is not None:
            response["data"] = data
        return Response(response, status=status)

    def error_response(self, message, code="error", details=None, status=400):
        """Return a standardized error response."""
        return Response(
            {
                "success": False,
                "message": message,
                "error": {"code": code, "details": details},
            },
            status=status,
        )

    def get_client_ip(self):
        """Get client IP from request."""
        request = self.request
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "0.0.0.0")

    def get_user_agent(self):
        """Get user agent from request."""
        return self.request.META.get("HTTP_USER_AGENT", "")
