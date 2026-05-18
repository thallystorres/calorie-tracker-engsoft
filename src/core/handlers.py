from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from .exceptions import AppError

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

logger = logging.getLogger(__name__)


def drf_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    if isinstance(exc, AppError):
        return Response(
            {"detail": exc.detail, "code": exc.code},
            status=exc.status,
        )

    response = drf_exception_handler(exc, context)

    if response is not None:
        return response

    logger.exception("Erro interno não tratado na API: %s", exc)
    return Response(
        {"detail": "Erro interno do servidor."},
        status=500,
    )


class UIExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        return self.get_response(request)

    def process_exception(
        self, request: HttpRequest, exception: Exception
    ) -> HttpResponse | None:
        if _is_api_request(request):
            return None

        logger.exception(
            "Erro interno não tratado na UI: %s path=%s",
            exception,
            request.path,
        )
        return render(request, "500.html", status=500)


def server_error(request: HttpRequest) -> HttpResponse:
    return render(request, "500.html", status=500)


def not_found(request: HttpRequest, exception: Exception | None = None) -> HttpResponse:
    return render(request, "404.html", status=404)


def _is_api_request(request: HttpRequest) -> bool:
    return request.path.startswith("/api/")
